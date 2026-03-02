"""
Calculation service layer - wraps existing business logic
"""
from typing import Dict, Any, List, Tuple
import pandas as pd
from fastapi import HTTPException

# Import business logic (API-safe version)
from app.core.business_logic import (
    splitter_df_2,
    wikkel_formule,
    lijst_opbreker,
    banen_in_vdp_check,
    maak_een_dummy_baan,
    summary_splitter_df_2,
    df_sum_met_slice,
    df_sum_form_writer,
    pdf_sum_form_writer,
)


class CalculationService:
    """Service for handling calculations and data processing"""
    
    def __init__(self):
        self.wikkel_calculator = wikkel_formule()
    
    def calculate_wikkel(self, aantal_per_rol: int, formaat_hoogte: int, kern: int = 76) -> Dict[str, Any]:
        """Calculate wikkel value using existing logic"""
        try:
            wikkel_value = self.wikkel_calculator(aantal_per_rol, formaat_hoogte, kern)
            
            return {
                "wikkel_value": wikkel_value,
                "calculation_details": {
                    "aantal_per_rol": aantal_per_rol,
                    "formaat_hoogte": formaat_hoogte,
                    "kern": kern,
                    "formula_used": "wikkel_formule"
                }
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Wikkel calculation failed: {str(e)}")
    
    def split_dataframe(
        self, 
        df: pd.DataFrame,
        mes: int,
        aantal_vdps: int = 1,
        sluitbarcode_posities: int = 8,
        afwijking_waarde: int = 0,
        wikkel: int = 1,
        extra_etiketten: int = 5,
        pdf_sluitetiket: bool = False
    ) -> Dict[str, Any]:
        """Split DataFrame using existing splitter_df_2 logic"""
        try:
            # Use existing splitter function
            split_result = splitter_df_2(
                df,
                mes=mes,
                aantalvdps=aantal_vdps,
                sluitbarcode_posities=sluitbarcode_posities,
                afwijking_waarde=afwijking_waarde,
                wikkel=wikkel,
                extra_etiketten=extra_etiketten,
                pdf_sluitetiket=pdf_sluitetiket
            )
            
            # Process results into lanes
            lanes = [pd.concat(split_result[x]).reset_index(drop=True) 
                    for x in range(len(split_result))]
            
            # Calculate metrics
            total_lanes = len(lanes)
            aantalbanen = aantal_vdps * mes
            
            # Check if dummy lanes are needed
            dummy_needed, dummy_count, final_vdps = banen_in_vdp_check(
                aantalbanen, total_lanes, aantal_vdps, mes
            )
            
            # Create summary data
            summary_data = []
            for i, lane in enumerate(lanes):
                summary_data.append({
                    "lane_number": i + 1,
                    "records": len(lane),
                    "total_labels": int(lane['aantal'].sum()) if 'aantal' in lane.columns else 0,
                    "columns": list(lane.columns)
                })
            
            return {
                "total_lanes": total_lanes,
                "lanes_created": len(lanes),
                "dummy_lanes_needed": dummy_needed,
                "dummy_lanes_count": dummy_count if dummy_needed else 0,
                "final_vdps": final_vdps,
                "summary_data": summary_data,
                "metrics": {
                    "input_records": len(df),
                    "total_aantal": int(df['aantal'].sum()),
                    "mes": mes,
                    "aantal_vdps": aantal_vdps,
                    "calculated_average": int(df['aantal'].sum()) // (mes * aantal_vdps) + afwijking_waarde
                },
                "lanes": lanes  # Include actual lane data
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Data splitting failed: {str(e)}")
    
    def generate_summary(
        self,
        df: pd.DataFrame,
        mes: int,
        aantal_vdps: int = 1,
        extra_etiketten: int = 5
    ) -> Dict[str, Any]:
        """Generate summary using existing summary logic"""
        try:
            # Generate summary slices
            summary_slices = summary_splitter_df_2(
                df, mes, aantal_vdps, extra_etiketten=extra_etiketten
            )
            
            # Generate summary DataFrame
            summary_df = df_sum_met_slice(df, summary_slices, numvdp=1)
            
            # Convert to serializable format
            summary_data = []
            for _, row in summary_df.iterrows():
                summary_data.append(row.to_dict())
            
            return {
                "summary_data": summary_data,
                "total_items": len(summary_data),
                "total_labels": int(df['aantal'].sum()),
                "vdp_count": aantal_vdps,
                "slices": summary_slices,
                "metrics": {
                    "input_records": len(df),
                    "mes": mes,
                    "aantal_vdps": aantal_vdps,
                    "extra_etiketten": extra_etiketten
                }
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Summary generation failed: {str(e)}")
    
    def create_form_summary(self, **kwargs) -> Dict[str, Any]:
        """Create form summary using existing df_sum_form_writer"""
        try:
            summary_df = df_sum_form_writer(**kwargs)
            
            # Convert to serializable format
            summary_data = []
            for _, row in summary_df.iterrows():
                summary_data.append(row.to_dict())
            
            return {
                "form_summary": summary_data,
                "parameters": kwargs
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Form summary creation failed: {str(e)}")

    def create_pdf_summary(
        self,
        output_dir: str,
        titel: str,
        banen_data: dict,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a PDF summary using pdf_sum_form_writer."""
        try:
            output_path = pdf_sum_form_writer(output_dir, titel, banen_data, **kwargs)
            return {
                "pdf_path": str(output_path),
                "parameters": kwargs,
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF summary creation failed: {str(e)}")
