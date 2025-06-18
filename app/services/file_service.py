"""
File processing service layer
"""
import uuid
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple
import pandas as pd
from fastapi import UploadFile, HTTPException

# Import business logic (API-safe version)
from app.core.business_logic import file_to_generator
from app.core.config import settings


class FileService:
    """Service for handling file operations"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.upload_dir.mkdir(exist_ok=True)
    
    async def save_uploaded_file(self, file: UploadFile) -> Dict[str, Any]:
        """Save uploaded file and return file info"""
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_path = Path(file.filename)
        if file_path.suffix.lower() not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}_{file.filename}"
        file_path = self.upload_dir / safe_filename
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
        # Get file info
        file_size = file_path.stat().st_size
        if file_size > settings.MAX_FILE_SIZE:
            file_path.unlink()  # Delete file
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes"
            )
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "safe_filename": safe_filename,
            "file_path": str(file_path),
            "file_size": file_size,
            "file_type": file_path.suffix.lower()
        }
    
    def load_dataframe(self, file_path: str) -> pd.DataFrame:
        """Load file into pandas DataFrame using existing logic"""
        try:
            return file_to_generator(file_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to load file: {str(e)}")
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate DataFrame has required columns"""
        required_columns = ['aantal', 'Omschrijving', 'sluitbarcode', 'Artnr']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing_columns}. Required: {required_columns}"
            )
        
        return {
            "valid": True,
            "shape": df.shape,
            "columns": list(df.columns),
            "total_records": len(df),
            "total_aantal": int(df['aantal'].sum()) if 'aantal' in df.columns else 0
        }
    
    def cleanup_file(self, file_path: str) -> bool:
        """Clean up uploaded file"""
        try:
            Path(file_path).unlink(missing_ok=True)
            return True
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a file"""
        path = Path(file_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "filename": path.name,
            "size": path.stat().st_size,
            "extension": path.suffix,
            "exists": True
        }
