# DF naar CSV - FastAPI Integration

This document describes the FastAPI integration for the DF naar CSV application, which provides REST API endpoints for processing Excel/CSV files for VDP (Variable Data Printing) generation.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip package manager

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Start the development server
python run_api.py
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📋 API Endpoints

### Health & Status
- `GET /health` - Health check and system status
- `GET /` - Root endpoint (health check)

### File Operations
- `POST /api/v1/files/upload` - Upload Excel/CSV file
- `GET /api/v1/files/validate/{file_id}` - Validate uploaded file
- `POST /api/v1/files/process` - Process file with parameters
- `DELETE /api/v1/files/{file_id}` - Delete uploaded file

### Calculations
- `POST /api/v1/calculations/wikkel` - Calculate wikkel values
- `POST /api/v1/calculations/split/{file_id}` - Split data across VDPs
- `GET /api/v1/calculations/metrics/{file_id}` - Get file metrics

### Summaries
- `POST /api/v1/summaries/generate/{file_id}` - Generate summaries
- `POST /api/v1/summaries/form-summary` - Create form summary
- `GET /api/v1/summaries/export/{file_id}/{format}` - Export summaries

## 🔧 Usage Examples

### 1. Upload a File
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -F "file=@your_file.xlsx"
```

Response:
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "file_id": "uuid-here",
  "filename": "your_file.xlsx",
  "file_size": 5391,
  "file_type": ".xlsx"
}
```

### 2. Validate File
```bash
curl "http://localhost:8000/api/v1/files/validate/{file_id}"
```

### 3. Calculate Wikkel
```bash
curl -X POST "http://localhost:8000/api/v1/calculations/wikkel" \
  -H "Content-Type: application/json" \
  -d '{"aantal_per_rol": 100, "formaat_hoogte": 80, "kern": 76}'
```

### 4. Process File
```bash
curl -X POST "http://localhost:8000/api/v1/files/process" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "your-file-id",
    "ordernummer": "202012345",
    "mes": 4,
    "vdp_aantal": 2,
    "extra_etiketten": 10
  }'
```

## 📊 Required File Format

Your Excel/CSV files must contain these columns:
- `aantal` - Number of labels
- `Omschrijving` - Description
- `sluitbarcode` - Closing barcode
- `Artnr` - Article number
- `beeld` - Image/PDF filename (optional)

Example CSV:
```csv
aantal;Omschrijving;sluitbarcode;Artnr;beeld
100;Product A - Red Label;12345678;ART001;product_a.pdf
150;Product B - Blue Label;12345679;ART002;product_b.pdf
```

## 🛠️ Configuration

### Environment Variables
Create a `.env` file based on `.env.example`:

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
nano .env
```

Key settings:
- `MAX_FILE_SIZE` - Maximum upload size (default: 50MB)
- `UPLOAD_DIR` - Upload directory (default: uploads)
- `DEBUG` - Enable debug mode (default: true)

### CORS Configuration
The API supports CORS for web frontend integration. Default allowed origins:
- http://localhost:3000 (React)
- http://localhost:8080 (Vue)
- http://localhost:4200 (Angular)

## 🔒 Security Considerations

- File uploads are validated for type and size
- Uploaded files are stored with unique IDs
- No authentication is currently implemented (add as needed)
- Debug mode should be disabled in production

## 🧪 Testing

### Create Test Files
```bash
python create_test_excel.py
```

### Test with curl
```bash
# Upload test file
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -F "file=@test_files/test_labels.csv"

# Validate file (use file_id from upload response)
curl "http://localhost:8000/api/v1/files/validate/{file_id}"
```

## 🏗️ Architecture

### Project Structure
```
app/
├── main.py              # FastAPI application
├── core/
│   ├── config.py        # Configuration settings
│   └── business_logic.py # Core business logic
├── api/v1/
│   ├── endpoints/       # API endpoints
│   └── api.py          # Router aggregation
├── models/
│   ├── requests.py      # Request models
│   └── responses.py     # Response models
└── services/
    ├── file_service.py  # File operations
    └── calculation_service.py # Business logic
```

### Key Components
- **FastAPI**: Modern web framework with automatic API documentation
- **Pydantic**: Data validation and serialization
- **Pandas**: Data processing and Excel/CSV handling
- **Business Logic**: Existing calculation and processing functions

## 🔄 Integration with Frontend

The API is designed to work with web frontends:

### JavaScript/TypeScript Example
```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('/api/v1/files/upload', {
  method: 'POST',
  body: formData
});

const { file_id } = await uploadResponse.json();

// Process file
const processResponse = await fetch('/api/v1/files/process', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_id,
    ordernummer: '202012345',
    mes: 4,
    vdp_aantal: 2
  })
});
```

## 📝 Development

### Running in Development
```bash
# Start with auto-reload
python run_api.py

# Or use uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Adding New Endpoints
1. Create endpoint in `app/api/v1/endpoints/`
2. Add request/response models in `app/models/`
3. Add business logic in `app/services/`
4. Include router in `app/api/v1/api.py`

## 🚀 Deployment

### Production Considerations
- Set `DEBUG=false` in environment
- Use proper ASGI server (Gunicorn + Uvicorn)
- Configure reverse proxy (Nginx)
- Set up proper logging
- Implement authentication if needed
- Configure file cleanup policies

### Docker Deployment (Future)
```dockerfile
FROM python:3.10-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Create feature branch from `feature/fastapi-integration`
2. Make changes
3. Test thoroughly
4. Submit pull request

## 📞 Support

For questions or issues:
- Check the interactive API documentation at `/docs`
- Review the logs for error details
- Ensure file format requirements are met
