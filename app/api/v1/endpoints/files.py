"""
File processing endpoints
"""
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
import pandas as pd
from pathlib import Path

from app.models.requests import ProcessFileRequest
from app.models.responses import (
    FileUploadResponse, 
    FileProcessingResponse, 
    DataFrameResponse,
    BaseResponse
)
from app.services.file_service import FileService
from app.services.calculation_service import CalculationService

router = APIRouter()


def get_file_service() -> FileService:
    """Dependency to get file service"""
    return FileService()


def get_calculation_service() -> CalculationService:
    """Dependency to get calculation service"""
    return CalculationService()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service)
):
    """
    Upload an Excel or CSV file for processing
    
    - **file**: Excel (.xlsx, .xls) or CSV file
    - Returns file information and upload status
    """
    file_info = await file_service.save_uploaded_file(file)
    
    return FileUploadResponse(
        message="File uploaded successfully",
        file_id=file_info["file_id"],
        filename=file_info["filename"],
        file_size=file_info["file_size"],
        file_type=file_info["file_type"],
        upload_path=file_info["file_path"]
    )


@router.get("/validate/{file_id}", response_model=DataFrameResponse)
async def validate_file(
    file_id: str,
    file_service: FileService = Depends(get_file_service)
):
    """
    Validate uploaded file and return DataFrame info
    
    - **file_id**: ID of uploaded file
    - Returns DataFrame structure and validation results
    """
    # Find file by ID (simplified - in production, use proper file tracking)
    upload_files = list(Path("uploads").glob(f"{file_id}_*"))
    if not upload_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = str(upload_files[0])
    
    # Load and validate DataFrame
    df = file_service.load_dataframe(file_path)
    validation_result = file_service.validate_dataframe(df)
    
    # Convert DataFrame to serializable format (first 10 rows for preview)
    preview_data = []
    for _, row in df.head(10).iterrows():
        preview_data.append(row.to_dict())
    
    return DataFrameResponse(
        message="File validated successfully",
        columns=list(df.columns),
        data=preview_data,
        shape=list(df.shape),
        dtypes={col: str(dtype) for col, dtype in df.dtypes.items()}
    )


@router.post("/process", response_model=FileProcessingResponse)
async def process_file(
    file_id: str,
    request: ProcessFileRequest,
    file_service: FileService = Depends(get_file_service),
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """
    Process uploaded file with specified parameters
    
    - **file_id**: ID of uploaded file
    - **request**: Processing parameters
    - Returns processing results and output file paths
    """
    # Find and load file
    upload_files = list(Path("uploads").glob(f"{file_id}_*"))
    if not upload_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = str(upload_files[0])
    df = file_service.load_dataframe(file_path)
    file_service.validate_dataframe(df)
    
    # Calculate wikkel if needed
    wikkel_value = request.wikkel_handmatige_invoer
    if not request.wikkel_handmatig:
        # Use automatic calculation (simplified - would need max aantal_per_rol from data)
        aantal_per_rol = int(df['aantal'].max()) if 'aantal' in df.columns else 10
        wikkel_calc = calc_service.calculate_wikkel(
            aantal_per_rol, request.formaat_hoogte, request.kern
        )
        wikkel_value = wikkel_calc["wikkel_value"]
    
    # Split data
    split_result = calc_service.split_dataframe(
        df,
        mes=request.mes,
        aantal_vdps=request.vdp_aantal,
        sluitbarcode_posities=request.posities_sluitbarcode,
        afwijking_waarde=request.afwijkings_waarde,
        wikkel=wikkel_value,
        extra_etiketten=request.extra_etiketten,
        pdf_sluitetiket=request.pdf_sluitetiket
    )
    
    # Generate summary
    summary_result = calc_service.generate_summary(
        df,
        mes=request.mes,
        aantal_vdps=request.vdp_aantal,
        extra_etiketten=request.extra_etiketten
    )
    
    # Create form summary with request parameters
    form_params = request.dict()
    form_summary = calc_service.create_form_summary(**form_params)
    
    return FileProcessingResponse(
        message="File processed successfully",
        job_id=file_id,
        input_file=upload_files[0].name,
        output_files=[],  # Would contain actual output file paths
        processing_summary={
            "split_result": split_result,
            "summary_result": summary_result,
            "form_summary": form_summary
        },
        metrics={
            "input_records": len(df),
            "total_labels": int(df['aantal'].sum()),
            "lanes_created": split_result["lanes_created"],
            "wikkel_used": wikkel_value
        }
    )


@router.delete("/{file_id}", response_model=BaseResponse)
async def delete_file(
    file_id: str,
    file_service: FileService = Depends(get_file_service)
):
    """
    Delete uploaded file
    
    - **file_id**: ID of file to delete
    """
    upload_files = list(Path("uploads").glob(f"{file_id}_*"))
    if not upload_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    success = file_service.cleanup_file(str(upload_files[0]))
    
    if success:
        return BaseResponse(message="File deleted successfully")
    else:
        raise HTTPException(status_code=500, detail="Failed to delete file")
