"""
Pydantic models for API responses
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class FileUploadResponse(BaseResponse):
    """Response model for file upload"""
    file_id: str
    filename: str
    file_size: int
    file_type: str
    upload_path: str


class ProcessingStatusResponse(BaseResponse):
    """Response model for processing status"""
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: Optional[int] = None  # 0-100
    estimated_completion: Optional[datetime] = None


class FileProcessingResponse(BaseResponse):
    """Response model for file processing results"""
    job_id: str
    input_file: str
    output_files: List[str]
    processing_summary: Dict[str, Any]
    metrics: Dict[str, Any]


class WikkelCalculationResponse(BaseResponse):
    """Response model for wikkel calculations"""
    wikkel_value: int
    calculation_details: Dict[str, Any]


class DataSplitResponse(BaseResponse):
    """Response model for data splitting"""
    total_lanes: int
    lanes_created: int
    summary_data: List[Dict[str, Any]]
    metrics: Dict[str, Any]


class SummaryResponse(BaseResponse):
    """Response model for summary generation"""
    summary_id: str
    summary_data: List[Dict[str, Any]]
    total_items: int
    total_labels: int
    vdp_count: int
    file_paths: List[str]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
    uptime: Optional[str] = None
    dependencies: Dict[str, str] = {}


class DataFrameResponse(BaseResponse):
    """Response model for DataFrame data"""
    columns: List[str]
    data: List[Dict[str, Any]]
    shape: List[int]  # [rows, columns]
    dtypes: Dict[str, str]
