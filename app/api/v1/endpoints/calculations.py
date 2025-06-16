"""
Calculation endpoints
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
import pandas as pd
from pathlib import Path

from app.models.requests import WikkelCalculationRequest, SplitDataRequest
from app.models.responses import WikkelCalculationResponse, DataSplitResponse
from app.services.calculation_service import CalculationService
from app.services.file_service import FileService

router = APIRouter()


def get_calculation_service() -> CalculationService:
    """Dependency to get calculation service"""
    return CalculationService()


def get_file_service() -> FileService:
    """Dependency to get file service"""
    return FileService()


@router.post("/wikkel", response_model=WikkelCalculationResponse)
async def calculate_wikkel(
    request: WikkelCalculationRequest,
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """
    Calculate wikkel value based on parameters
    
    - **aantal_per_rol**: Number of items per roll
    - **formaat_hoogte**: Format height
    - **kern**: Core size (default: 76)
    - Returns calculated wikkel value and details
    """
    result = calc_service.calculate_wikkel(
        aantal_per_rol=request.aantal_per_rol,
        formaat_hoogte=request.formaat_hoogte,
        kern=request.kern
    )
    
    return WikkelCalculationResponse(
        message="Wikkel calculated successfully",
        wikkel_value=result["wikkel_value"],
        calculation_details=result["calculation_details"]
    )


@router.post("/split/{file_id}", response_model=DataSplitResponse)
async def split_data(
    file_id: str,
    request: SplitDataRequest,
    calc_service: CalculationService = Depends(get_calculation_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    Split data from uploaded file across lanes/VDPs
    
    - **file_id**: ID of uploaded file
    - **request**: Split parameters
    - Returns split results and lane information
    """
    # Find and load file
    upload_files = list(Path("uploads").glob(f"{file_id}_*"))
    if not upload_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = str(upload_files[0])
    df = file_service.load_dataframe(file_path)
    file_service.validate_dataframe(df)
    
    # Perform split
    result = calc_service.split_dataframe(
        df,
        mes=request.mes,
        aantal_vdps=request.aantal_vdps,
        sluitbarcode_posities=request.sluitbarcode_posities,
        afwijking_waarde=request.afwijking_waarde,
        wikkel=request.wikkel,
        extra_etiketten=request.extra_etiketten,
        pdf_sluitetiket=request.pdf_sluitetiket
    )
    
    return DataSplitResponse(
        message="Data split successfully",
        total_lanes=result["total_lanes"],
        lanes_created=result["lanes_created"],
        summary_data=result["summary_data"],
        metrics=result["metrics"]
    )


@router.get("/metrics/{file_id}")
async def get_file_metrics(
    file_id: str,
    file_service: FileService = Depends(get_file_service)
):
    """
    Get basic metrics for uploaded file
    
    - **file_id**: ID of uploaded file
    - Returns file metrics and statistics
    """
    # Find and load file
    upload_files = list(Path("uploads").glob(f"{file_id}_*"))
    if not upload_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = str(upload_files[0])
    df = file_service.load_dataframe(file_path)
    
    # Calculate metrics
    metrics = {
        "file_info": {
            "filename": upload_files[0].name,
            "size": upload_files[0].stat().st_size,
            "records": len(df),
            "columns": list(df.columns)
        },
        "data_metrics": {
            "total_aantal": int(df['aantal'].sum()) if 'aantal' in df.columns else 0,
            "max_aantal": int(df['aantal'].max()) if 'aantal' in df.columns else 0,
            "min_aantal": int(df['aantal'].min()) if 'aantal' in df.columns else 0,
            "avg_aantal": float(df['aantal'].mean()) if 'aantal' in df.columns else 0,
            "unique_articles": int(df['Artnr'].nunique()) if 'Artnr' in df.columns else 0
        },
        "column_info": {
            col: {
                "dtype": str(df[col].dtype),
                "null_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique())
            }
            for col in df.columns
        }
    }
    
    return {
        "success": True,
        "message": "Metrics calculated successfully",
        "file_id": file_id,
        "metrics": metrics
    }
