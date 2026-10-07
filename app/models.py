from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from .database import Base

class FileRecord(Base):
    __tablename__ = "files"
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    crs = Column(String, nullable=True)
    feature_count = Column(Integer, default=0)
    status = Column(String, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    features = relationship("FeatureRecord", back_populates="file", cascade="all, delete-orphan")

class FeatureRecord(Base):
    __tablename__ = "features"
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(String, ForeignKey("files.id"), nullable=False)
    feature_index = Column(Integer, nullable=False)
    geometry_type = Column(String, nullable=False)
    geometry_wkt = Column(Text, nullable=True)
    properties = Column(Text, nullable=True)
    file = relationship("FileRecord", back_populates="features")
    measurement = relationship("MeasurementRecord", back_populates="feature", uselist=False, cascade="all, delete-orphan")

class MeasurementRecord(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    feature_id = Column(Integer, ForeignKey("features.id"), nullable=False)
    measurement_type = Column(String, nullable=True)
    value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    status = Column(String, nullable=False)
    error_message = Column(Text, nullable=True)
    feature = relationship("FeatureRecord", back_populates="measurement")
