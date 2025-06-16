"""
Summary generation endpoints
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
import pandas as pd
from pathlib import Path

from app.models.requests import SummaryGenerationRequest
from app.models.responses import SummaryResponse, BaseResponse
from app.services.calculation_service import CalculationService
from app.services.file_service import FileService

router = APIRouter()


def get_calculation_service() -> CalculationService:
    """Dependency to get calculation service"""
    return CalculationService()


def get_file_service() -> FileService:
    """Dependency to get file service"""
    return FileService()


@router.post("/generate/{file_id}", response_model=SummaryResponse)
async def generate_summary(
    file_id: str,
    request: SummaryGenerationRequest,
    calc_service: CalculationService = Depends(get_calculation_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    Generate summary for uploaded file
    
    - **file_id**: ID of uploaded file
    - **request**: Summary generation parameters
    - Returns generated summary data
    """
    # Find and load file
    upload_files = list(Path("uploads").glob(f"{file_id}_*"))
    if not upload_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = str(upload_files[0])
    df = file_service.load_dataframe(file_path)
    file_service.validate_dataframe(df)
    
    # Generate summary
    result = calc_service.generate_summary(
        df,
        mes=request.mes,
        aantal_vdps=request.aantal_vdps,
        extra_etiketten=request.extra_etiketten
    )
    
    return SummaryResponse(
        message="Summary generated successfully",
        summary_id=file_id,
        summary_data=result["summary_data"],
        total_items=result["total_items"],
        total_labels=result["total_labels"],
        vdp_count=result["vdp_count"],
        file_paths=[]  # Would contain actual output file paths
    )


@router.post("/form-summary", response_model=BaseResponse)
async def create_form_summary(
    parameters: Dict[str, Any],
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """
    Create form summary with custom parameters
    
    - **parameters**: Dictionary of form parameters
    - Returns form summary data
    """
    result = calc_service.create_form_summary(**parameters)
    
    return BaseResponse(
        message="Form summary created successfully",
        timestamp=None  # Will be set automatically
    )


@router.get("/export/{file_id}/{format}")
async def export_summary(
    file_id: str,
    format: str,
    mes: int = 4,
    aantal_vdps: int = 1,
    extra_etiketten: int = 5,
    calc_service: CalculationService = Depends(get_calculation_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    Export summary in specified format
    
    - **file_id**: ID of uploaded file
    - **format**: Export format (json, excel, csv)
    - **mes**: Number of lanes
    - **aantal_vdps**: Number of VDPs
    - **extra_etiketten**: Extra labels
    - Returns exported summary file
    """
    if format not in ["json", "excel", "csv"]:
        raise HTTPException(status_code=400, detail="Format must be json, excel, or csv")
    
    # Find and load file
    upload_files = list(Path("uploads").glob(f"{file_id}_*"))
    if not upload_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = str(upload_files[0])
    df = file_service.load_dataframe(file_path)
    file_service.validate_dataframe(df)
    
    # Generate summary
    result = calc_service.generate_summary(
        df, mes=mes, aantal_vdps=aantal_vdps, extra_etiketten=extra_etiketten
    )
    
    if format == "json":
        return {
            "success": True,
            "message": "Summary exported as JSON",
            "data": result
        }
    
    # For Excel/CSV export, we'd need to create actual files
    # This is a simplified version that returns the data structure
    return {
        "success": True,
        "message": f"Summary export in {format} format",
        "note": "File export functionality would be implemented here",
        "data_preview": result["summary_data"][:5]  # First 5 rows as preview
    }
