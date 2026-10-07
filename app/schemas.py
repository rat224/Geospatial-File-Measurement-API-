from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict

class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    filename: str
    feature_count: int
    crs: Optional[str]
    status: str
    created_at: datetime
    error_message: Optional[str] = None

class MeasurementResponse(BaseModel):
    feature_id: int
    geometry_type: str
    measurement_type: Optional[str]
    value: Optional[float]
    unit: Optional[str]
    status: str
    error_message: Optional[str] = None

class MeasurementsResponse(BaseModel):
    file_id: str
    measurements: list[MeasurementResponse]
