"""
Pydantic models for API requests
"""
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class ProcessFileRequest(BaseModel):
    """Request model for file processing"""
    
    # Order and identification
    ordernummer: str = Field(..., description="Order number", example="202012345")
    
    # Processing parameters
    mes: int = Field(4, ge=1, le=20, description="Number of lanes/mes")
    vdp_aantal: int = Field(1, ge=1, le=50, description="Number of VDPs")
    
    # Barcode settings
    sluitbarcode_uitvul_waarde: str = Field("01409468", description="Barcode fill value")
    posities_sluitbarcode: int = Field(8, ge=1, le=20, description="Barcode positions")
    
    # Calculation parameters
    afwijkings_waarde: int = Field(0, description="Deviation value")
    kern: int = Field(76, ge=40, le=100, description="Core size")
    
    # Format settings
    formaat_breedte: int = Field(80, ge=10, le=500, description="Format width")
    formaat_hoogte: int = Field(80, ge=10, le=500, description="Format height")
    y_waarde: int = Field(10, ge=1, le=100, description="Y value")
    
    # Processing options
    wikkel_handmatig: bool = Field(True, description="Manual wikkel calculation")
    wikkel_handmatige_invoer: int = Field(1, ge=1, le=100, description="Manual wikkel value")
    extra_etiketten: int = Field(10, ge=0, le=1000, description="Extra labels")
    
    # Output options
    pdf_sluitetiket: bool = Field(True, description="PDF closing label")
    opmerkingen: str = Field("", description="Comments")


class WikkelCalculationRequest(BaseModel):
    """Request model for wikkel calculations"""
    
    aantal_per_rol: int = Field(..., ge=1, description="Number per roll")
    formaat_hoogte: int = Field(..., ge=10, le=500, description="Format height")
    kern: int = Field(76, ge=40, le=100, description="Core size")


class SplitDataRequest(BaseModel):
    """Request model for data splitting"""
    
    mes: int = Field(..., ge=1, le=20, description="Number of lanes")
    aantal_vdps: int = Field(1, ge=1, le=50, description="Number of VDPs")
    sluitbarcode_posities: int = Field(8, ge=1, le=20, description="Barcode positions")
    afwijking_waarde: int = Field(0, description="Deviation value")
    wikkel: int = Field(1, ge=1, le=100, description="Wikkel value")
    extra_etiketten: int = Field(5, ge=0, le=1000, description="Extra labels")
    pdf_sluitetiket: bool = Field(False, description="PDF closing label")


class SummaryGenerationRequest(BaseModel):
    """Request model for summary generation"""
    
    mes: int = Field(..., ge=1, le=20, description="Number of lanes")
    aantal_vdps: int = Field(1, ge=1, le=50, description="Number of VDPs")
    extra_etiketten: int = Field(5, ge=0, le=1000, description="Extra labels")
    titel: str = Field("summary", description="Summary title")
