import json, os, tempfile, zipfile
from pathlib import Path
import geopandas as gpd
from .crs_service import project_for_measurement
from .measurement_service import measure_geometry

ALLOWED_EXTENSIONS = {".kml", ".zip"}
MAX_FILE_SIZE = 50 * 1024 * 1024

def safe_extract(zip_path: Path, destination: Path):
    with zipfile.ZipFile(zip_path) as zf:
        members = zf.infolist()
        if not any(Path(m.filename).suffix.lower() == ".shp" for m in members):
            raise ValueError("ZIP file does not contain a Shapefile (.shp).")
        for member in members:
            target = (destination / member.filename).resolve()
            if not str(target).startswith(str(destination.resolve()) + os.sep):
                raise ValueError("Unsafe ZIP path detected.")
        zf.extractall(destination)

def read_geospatial_file(path: Path):
    if path.suffix.lower() == ".kml":
        try:
            return gpd.read_file(path, driver="KML")
        except Exception:
            return gpd.read_file(path)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        safe_extract(path, tmp_path)
        shp = next(tmp_path.rglob("*.shp"), None)
        if shp is None:
            raise ValueError("No .shp file found in ZIP archive.")
        return gpd.read_file(shp)

def process(path: Path):
    gdf = read_geospatial_file(path)
    if gdf.empty:
        return gdf, gdf.crs.to_string() if gdf.crs else None, [], None
    original_crs = gdf.crs.to_string() if gdf.crs else None
    projected, measurement_crs = project_for_measurement(gdf)
    results = []
    for idx, (_, row) in enumerate(gdf.iterrows()):
        geometry = projected.iloc[idx].geometry
        measurement_type, value, status, error = measure_geometry(geometry)
        properties = {k: (None if v is None else str(v)) for k, v in row.drop(labels=[gdf.geometry.name]).items()}
        results.append({
            "feature_index": idx,
            "geometry_type": geometry.geom_type if geometry is not None else "Unknown",
            "geometry_wkt": geometry.wkt if geometry is not None else None,
            "properties": properties,
            "measurement_type": measurement_type,
            "value": value,
            "unit": "m²" if measurement_type == "area" else "m" if measurement_type == "length" else None,
            "status": status,
            "error_message": error,
        })
    return gdf, original_crs, results, measurement_crs
