#!/usr/bin/env python3
"""
Test script for the FastAPI endpoints
"""
import requests
import json
import time
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_file_upload():
    """Test file upload"""
    print("📤 Testing file upload...")
    
    # Use the test CSV file
    test_file = Path("test_files/test_labels.csv")
    if not test_file.exists():
        print("❌ Test file not found. Run 'python create_test_excel.py' first.")
        return None
    
    with open(test_file, 'rb') as f:
        files = {'file': ('test_labels.csv', f, 'text/csv')}
        response = requests.post(f"{API_BASE}/files/upload", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    print()
    
    if response.status_code == 200:
        return result['file_id']
    return None

def test_file_validation(file_id):
    """Test file validation"""
    print(f"✅ Testing file validation for {file_id}...")
    response = requests.get(f"{API_BASE}/files/validate/{file_id}")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Columns: {result.get('columns', [])}")
    print(f"Shape: {result.get('shape', [])}")
    print(f"Data preview: {len(result.get('data', []))} records")
    print()

def test_wikkel_calculation():
    """Test wikkel calculation"""
    print("🧮 Testing wikkel calculation...")
    data = {
        "aantal_per_rol": 100,
        "formaat_hoogte": 80,
        "kern": 76
    }
    response = requests.post(f"{API_BASE}/calculations/wikkel", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Wikkel value: {result.get('wikkel_value')}")
    print(f"Response: {json.dumps(result, indent=2)}")
    print()

def test_file_metrics(file_id):
    """Test file metrics"""
    print(f"📊 Testing file metrics for {file_id}...")
    response = requests.get(f"{API_BASE}/calculations/metrics/{file_id}")
    print(f"Status: {response.status_code}")
    result = response.json()
    if 'metrics' in result:
        metrics = result['metrics']
        print(f"Total records: {metrics['file_info']['records']}")
        print(f"Total labels: {metrics['data_metrics']['total_aantal']}")
        print(f"Unique articles: {metrics['data_metrics']['unique_articles']}")
    print()

def test_data_split(file_id):
    """Test data splitting"""
    print(f"✂️ Testing data split for {file_id}...")
    data = {
        "mes": 4,
        "aantal_vdps": 2,
        "sluitbarcode_posities": 8,
        "afwijking_waarde": 0,
        "wikkel": 1,
        "extra_etiketten": 10,
        "pdf_sluitetiket": True
    }
    response = requests.post(f"{API_BASE}/calculations/split/{file_id}", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    if response.status_code == 200:
        print(f"Total lanes: {result.get('total_lanes')}")
        print(f"Lanes created: {result.get('lanes_created')}")
        print(f"Summary data: {len(result.get('summary_data', []))} lanes")
    else:
        print(f"Error: {result}")
    print()

def test_summary_generation(file_id):
    """Test summary generation"""
    print(f"📋 Testing summary generation for {file_id}...")
    data = {
        "mes": 4,
        "aantal_vdps": 2,
        "extra_etiketten": 10,
        "titel": "Test Summary"
    }
    response = requests.post(f"{API_BASE}/summaries/generate/{file_id}", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    if response.status_code == 200:
        print(f"Total items: {result.get('total_items')}")
        print(f"Total labels: {result.get('total_labels')}")
        print(f"VDP count: {result.get('vdp_count')}")
    else:
        print(f"Error: {result}")
    print()

def test_file_processing(file_id):
    """Test complete file processing"""
    print(f"⚙️ Testing complete file processing for {file_id}...")
    data = {
        "ordernummer": "202012345",
        "mes": 4,
        "vdp_aantal": 2,
        "sluitbarcode_uitvul_waarde": "01409468",
        "posities_sluitbarcode": 8,
        "afwijkings_waarde": 0,
        "kern": 76,
        "formaat_breedte": 80,
        "formaat_hoogte": 80,
        "y_waarde": 10,
        "wikkel_handmatig": True,
        "wikkel_handmatige_invoer": 1,
        "extra_etiketten": 10,
        "pdf_sluitetiket": True,
        "opmerkingen": "API Test"
    }
    response = requests.post(f"{API_BASE}/files/process", 
                           params={"file_id": file_id}, 
                           json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    if response.status_code == 200:
        print(f"Job ID: {result.get('job_id')}")
        print(f"Input file: {result.get('input_file')}")
        metrics = result.get('metrics', {})
        print(f"Input records: {metrics.get('input_records')}")
        print(f"Total labels: {metrics.get('total_labels')}")
        print(f"Lanes created: {metrics.get('lanes_created')}")
    else:
        print(f"Error: {result}")
    print()

def test_file_cleanup(file_id):
    """Test file deletion"""
    print(f"🗑️ Testing file cleanup for {file_id}...")
    response = requests.delete(f"{API_BASE}/files/{file_id}")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result.get('message')}")
    print()

def main():
    """Run all tests"""
    print("🧪 Starting FastAPI Tests")
    print("=" * 50)
    
    # Test health
    test_health()
    
    # Test file upload
    file_id = test_file_upload()
    if not file_id:
        print("❌ File upload failed. Cannot continue with other tests.")
        return
    
    # Test file validation
    test_file_validation(file_id)
    
    # Test wikkel calculation
    test_wikkel_calculation()
    
    # Test file metrics
    test_file_metrics(file_id)
    
    # Test data split
    test_data_split(file_id)
    
    # Test summary generation
    test_summary_generation(file_id)
    
    # Test complete file processing
    test_file_processing(file_id)
    
    # Test file cleanup
    test_file_cleanup(file_id)
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
