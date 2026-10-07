import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import FileRecord, FeatureRecord, MeasurementRecord
from .schemas import FileResponse, MeasurementsResponse, MeasurementResponse
from .services.file_processor import process, ALLOWED_EXTENSIONS, MAX_FILE_SIZE

Base.metadata.create_all(bind=engine)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app = FastAPI(title="Geospatial File Measurement API", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/files/", response_model=FileResponse, status_code=201)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Only .kml or .zip files are supported.")
    data = await file.read()
    if not data:
        raise HTTPException(400, "Uploaded file is empty.")
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(413, "File exceeds the 50 MB limit.")
    file_id = uuid.uuid4().hex
    stored = UPLOAD_DIR / f"{file_id}{suffix}"
    stored.write_bytes(data)
    record = FileRecord(id=file_id, filename=file.filename, file_type=suffix[1:].upper(), status="PROCESSING")
    db.add(record); db.commit()
    try:
        gdf, crs, results, measurement_crs = process(stored)
        record.crs = crs
        record.feature_count = len(results)
        record.status = "COMPLETED"
        for item in results:
            feature = FeatureRecord(file_id=file_id, feature_index=item["feature_index"], geometry_type=item["geometry_type"], geometry_wkt=item["geometry_wkt"], properties=__import__('json').dumps(item["properties"]))
            db.add(feature); db.flush()
            db.add(MeasurementRecord(feature_id=feature.id, measurement_type=item["measurement_type"], value=item["value"], unit=item["unit"], status=item["status"], error_message=item["error_message"]))
        db.commit()
        return record
    except Exception as exc:
        db.rollback()
        record = db.get(FileRecord, file_id)
        record.status = "FAILED"; record.error_message = str(exc)
        db.commit()
        raise HTTPException(422, f"Unable to process geospatial file: {exc}")

@app.get("/api/files/{file_id}/", response_model=FileResponse)
def get_file(file_id: str, db: Session = Depends(get_db)):
    record = db.get(FileRecord, file_id)
    if not record: raise HTTPException(404, "File not found.")
    return record

@app.get("/api/files/{file_id}/measurements/", response_model=MeasurementsResponse)
def get_measurements(file_id: str, db: Session = Depends(get_db)):
    record = db.get(FileRecord, file_id)
    if not record: raise HTTPException(404, "File not found.")
    measurements = []
    for feature in record.features:
        m = feature.measurement
        measurements.append(MeasurementResponse(feature_id=feature.feature_index, geometry_type=feature.geometry_type, measurement_type=m.measurement_type, value=m.value, unit=m.unit, status=m.status, error_message=m.error_message))
    return {"file_id": file_id, "measurements": measurements}
