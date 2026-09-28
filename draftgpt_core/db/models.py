from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()


class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    APPROVED = "APPROVED"


class CADModelJob(Base):
    __tablename__ = "cad_model_jobs"

    job_id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    
    # Metadata & Results
    bounding_box = Column(JSON, nullable=True)
    extracted_features = Column(JSON, nullable=True)
    drawing_layout = Column(JSON, nullable=True)
    dxf_output_path = Column(String, nullable=True)
    
    # Engineer Review Flags
    flagged_items = Column(JSON, default=list)  # e.g., low-confidence features
    reviewer_notes = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)