# API Documentation - MammoViewer

Complete REST API reference for programmatic access.

## Base URL
```
http://localhost:5000/api
```

## Authentication

Currently no authentication required. For production, implement JWT or OAuth.

---

## Endpoints

### Health Check

#### GET /api/health

Check server status and 3D Slicer availability.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-10T10:30:00.000Z",
  "slicer_available": true
}
```

**Example:**
```bash
curl http://localhost:5000/api/health
```

---

### Upload DICOM Files

#### POST /api/upload

Upload DICOM files for processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body: DICOM files

**Response:**
```json
{
  "success": true,
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Uploaded 10 files",
  "files": ["file1.dcm", "file2.dcm"],
  "dicom_info": {
    "success": true,
    "num_files": 10,
    "num_series": 1,
    "metadata": {
      "patient_id": "Anonymous",
      "modality": "MG",
      "number_of_slices": 10
    }
  }
}
```

**Python Example:**
```python
import requests

files = [
    ('files', open('file1.dcm', 'rb')),
    ('files', open('file2.dcm', 'rb'))
]
response = requests.post('http://localhost:5000/api/upload', files=files)
upload_id = response.json()['upload_id']
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "files=@file1.dcm" \
  -F "files=@file2.dcm"
```

---

### Start Conversion

#### POST /api/convert

Start DICOM to STL conversion.

**Request:**
```json
{
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "threshold": 100,
  "smoothing": true,
  "decimation": 0.75
}
```

**Parameters:**
- `upload_id` (required): Upload ID from /api/upload
- `threshold` (optional): 10-1000, default 100
- `smoothing` (optional): boolean, default true
- `decimation` (optional): 0.0-1.0, default 0.75

**Response:**
```json
{
  "success": true,
  "job_id": "660e8400-e29b-41d4-a716-446655440001",
  "message": "Conversion started"
}
```

**Example:**
```python
params = {
    'upload_id': upload_id,
    'threshold': 100,
    'smoothing': True,
    'decimation': 0.75
}
response = requests.post('http://localhost:5000/api/convert', json=params)
job_id = response.json()['job_id']
```

---

### Check Job Status

#### GET /api/status/{job_id}

Poll for conversion job status.

**Response (Processing):**
```json
{
  "job_id": "660e8400-e29b-41d4-a716-446655440001",
  "upload_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 50,
  "message": "Converting to STL...",
  "stl_file": null,
  "error": null
}
```

**Response (Completed):**
```json
{
  "job_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "completed",
  "progress": 100,
  "message": "Conversion completed successfully",
  "stl_file": "550e8400.stl"
}
```

**Status Values:**
- `queued` - Waiting to start
- `processing` - Currently processing
- `completed` - Successfully completed
- `failed` - Failed with error

**Example:**
```python
import time

while True:
    response = requests.get(f'http://localhost:5000/api/status/{job_id}')
    data = response.json()
    
    if data['status'] == 'completed':
        stl_file = data['stl_file']
        break
    elif data['status'] == 'failed':
        print(f"Error: {data['error']}")
        break
    
    time.sleep(2)
```

---

### Download STL File

#### GET /api/download/{filename}

Download converted STL file.

**Response:** Binary STL file

**Example:**
```python
response = requests.get(f'http://localhost:5000/api/download/{stl_file}')
with open('output.stl', 'wb') as f:
    f.write(response.content)
```

---

### Preview STL File

#### GET /api/preview/{filename}

Get STL file for preview (not as attachment).

**Response:** Binary STL file

**Example:**
```javascript
const url = `http://localhost:5000/api/preview/${stlFile}`;
loader.load(url, (geometry) => {
    // Three.js rendering
});
```

---

### List All Jobs

#### GET /api/jobs

List all conversion jobs.

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "660e8400-e29b-41d4-a716-446655440001",
      "status": "completed",
      "progress": 100,
      "stl_file": "550e8400.stl"
    }
  ],
  "count": 1
}
```

---

### Manual Cleanup

#### POST /api/cleanup

Trigger manual cleanup of old files.

**Response:**
```json
{
  "success": true,
  "message": "Cleanup completed"
}
```

---

## Complete Workflow Example

### Python
```python
import requests
import time

base_url = 'http://localhost:5000/api'

# 1. Upload DICOM files
files = [('files', open(f'file{i}.dcm', 'rb')) for i in range(1, 11)]
response = requests.post(f'{base_url}/upload', files=files)
upload_id = response.json()['upload_id']
print(f"Upload ID: {upload_id}")

# 2. Start conversion
params = {
    'upload_id': upload_id,
    'threshold': 100,
    'smoothing': True,
    'decimation': 0.75
}
response = requests.post(f'{base_url}/convert', json=params)
job_id = response.json()['job_id']
print(f"Job ID: {job_id}")

# 3. Poll for status
while True:
    response = requests.get(f'{base_url}/status/{job_id}')
    data = response.json()
    print(f"Status: {data['status']} - {data['progress']}%")
    
    if data['status'] == 'completed':
        stl_file = data['stl_file']
        print(f"Completed! File: {stl_file}")
        break
    elif data['status'] == 'failed':
        print(f"Failed: {data['error']}")
        break
    
    time.sleep(2)

# 4. Download STL
response = requests.get(f'{base_url}/download/{stl_file}')
with open(f'output_{stl_file}', 'wb') as f:
    f.write(response.content)
print(f"Downloaded: output_{stl_file}")
```

### JavaScript
```javascript
const baseUrl = 'http://localhost:5000/api';

async function convertDICOM() {
  // 1. Upload files
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));
  
  const uploadRes = await fetch(`${baseUrl}/upload`, {
    method: 'POST',
    body: formData
  });
  const { upload_id } = await uploadRes.json();
  
  // 2. Start conversion
  const convertRes = await fetch(`${baseUrl}/convert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      upload_id,
      threshold: 100,
      smoothing: true,
      decimation: 0.75
    })
  });
  const { job_id } = await convertRes.json();
  
  // 3. Poll for status
  let stl_file;
  while (true) {
    const statusRes = await fetch(`${baseUrl}/status/${job_id}`);
    const data = await statusRes.json();
    
    if (data.status === 'completed') {
      stl_file = data.stl_file;
      break;
    }
    await new Promise(r => setTimeout(r, 2000));
  }
  
  // 4. Download
  window.location.href = `${baseUrl}/download/${stl_file}`;
}
```

---

## Error Responses

All endpoints may return errors:
```json
{
  "error": "Error message"
}
```

**Common Status Codes:**
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource doesn't exist)
- `413` - Payload Too Large (file size exceeded)
- `500` - Internal Server Error

---

## Rate Limits

Currently no rate limits. For production, implement:
- 100 requests per hour per IP
- 10 concurrent conversions per user

---

## Best Practices

1. **Poll Responsibly**: Use 2-second intervals for status polling
2. **Handle Errors**: Always check response status codes
3. **Cleanup**: Delete files after download if not needed
4. **Validate Input**: Check DICOM files before upload
5. **Timeout**: Set reasonable timeouts (5 minutes for conversion)

---

## Support

- GitHub Issues: https://github.com/KY-BChain/MammoViewer/issues
- Documentation: See README.md