# MammoViewer API Documentation

Complete REST API reference for MammoViewer DICOM to STL converter.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, no authentication is required. For production deployments, implement appropriate authentication mechanisms.

## Rate Limiting

No rate limiting is currently enforced. Consider implementing rate limiting for production use.

## Response Format

All responses are in JSON format with appropriate HTTP status codes.

**Success Response:**
```json
{
    "key": "value",
    "data": {}
}
```

**Error Response:**
```json
{
    "error": "Error message description"
}
```

---

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint:** `GET /api/health`

**Request:**
```bash
curl http://localhost:5000/api/health
```

**Response:** `200 OK`
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00.123456",
    "version": "1.0.0"
}
```

**Example (Python):**
```python
import requests

response = requests.get('http://localhost:5000/api/health')
print(response.json())
```

**Example (JavaScript):**
```javascript
fetch('http://localhost:5000/api/health')
    .then(response => response.json())
    .then(data => console.log(data));
```

---

### 2. Upload DICOM Files

Upload DICOM files for conversion.

**Endpoint:** `POST /api/upload`

**Content-Type:** `multipart/form-data`

**Parameters:**
- `files` (required): List of DICOM files (max 100 files, 500MB total)

**Request:**
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "files=@scan1.dcm" \
  -F "files=@scan2.dcm" \
  -F "files=@scan3.dcm"
```

**Response:** `200 OK`
```json
{
    "upload_id": "550e8400-e29b-41d4-a716-446655440000",
    "file_count": 3,
    "message": "Successfully uploaded 3 files"
}
```

**Error Responses:**

`400 Bad Request` - No files provided
```json
{
    "error": "No files provided"
}
```

`400 Bad Request` - Too many files
```json
{
    "error": "Too many files. Maximum 100 allowed"
}
```

`413 Request Entity Too Large` - File size exceeds limit
```json
{
    "error": "File too large. Maximum size is 500MB"
}
```

**Example (Python):**
```python
import requests
from pathlib import Path

# Upload multiple files
files = []
dicom_dir = Path('path/to/dicom/files')
for dcm_file in dicom_dir.glob('*.dcm'):
    files.append(('files', open(dcm_file, 'rb')))

response = requests.post('http://localhost:5000/api/upload', files=files)
upload_data = response.json()
upload_id = upload_data['upload_id']
print(f"Upload ID: {upload_id}")

# Close file handles
for _, file_handle in files:
    file_handle.close()
```

**Example (JavaScript):**
```javascript
const formData = new FormData();
const fileInput = document.getElementById('file-input');

Array.from(fileInput.files).forEach(file => {
    formData.append('files', file);
});

fetch('http://localhost:5000/api/upload', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Upload ID:', data.upload_id);
});
```

---

### 3. Start Conversion

Start DICOM to STL conversion job.

**Endpoint:** `POST /api/convert`

**Content-Type:** `application/json`

**Request Body:**
```json
{
    "upload_id": "550e8400-e29b-41d4-a716-446655440000",
    "threshold": 100,
    "smoothing": true,
    "decimation": 0.75
}
```

**Parameters:**
- `upload_id` (required, string): Upload ID from upload endpoint
- `threshold` (optional, integer): Threshold value (10-1000, default: 100)
- `smoothing` (optional, boolean): Apply smoothing (default: true)
- `decimation` (optional, float): Decimation rate 0.0-1.0 (default: 0.75)

**Request:**
```bash
curl -X POST http://localhost:5000/api/convert \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": "550e8400-e29b-41d4-a716-446655440000",
    "threshold": 150,
    "smoothing": true,
    "decimation": 0.8
  }'
```

**Response:** `200 OK`
```json
{
    "job_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "message": "Conversion started"
}
```

**Error Responses:**

`400 Bad Request` - Missing upload_id
```json
{
    "error": "upload_id is required"
}
```

`404 Not Found` - Upload not found
```json
{
    "error": "Upload not found"
}
```

`400 Bad Request` - Invalid threshold
```json
{
    "error": "Threshold must be between 10 and 1000"
}
```

**Example (Python):**
```python
import requests

response = requests.post('http://localhost:5000/api/convert', json={
    'upload_id': upload_id,
    'threshold': 150,
    'smoothing': True,
    'decimation': 0.75
})

job_data = response.json()
job_id = job_data['job_id']
print(f"Job ID: {job_id}")
```

**Example (JavaScript):**
```javascript
fetch('http://localhost:5000/api/convert', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        upload_id: uploadId,
        threshold: 150,
        smoothing: true,
        decimation: 0.75
    })
})
.then(response => response.json())
.then(data => {
    console.log('Job ID:', data.job_id);
});
```

---

### 4. Get Job Status

Check the status of a conversion job.

**Endpoint:** `GET /api/status/<job_id>`

**Request:**
```bash
curl http://localhost:5000/api/status/7c9e6679-7425-40de-944b-e07fc1f90ae7
```

**Response:** `200 OK`

**During Processing:**
```json
{
    "job_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "upload_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "progress": 45,
    "message": "Converting to STL...",
    "stl_file": null,
    "error": null,
    "created_at": "2024-01-15T10:30:00.123456",
    "updated_at": "2024-01-15T10:31:30.654321"
}
```

**On Completion:**
```json
{
    "job_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "upload_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "progress": 100,
    "message": "Conversion completed successfully (1234567 bytes)",
    "stl_file": "7c9e6679-7425-40de-944b-e07fc1f90ae7.stl",
    "error": null,
    "created_at": "2024-01-15T10:30:00.123456",
    "updated_at": "2024-01-15T10:33:15.987654"
}
```

**On Failure:**
```json
{
    "job_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "upload_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "failed",
    "progress": 60,
    "message": "Conversion failed",
    "stl_file": null,
    "error": "3D Slicer not found at /path/to/Slicer",
    "created_at": "2024-01-15T10:30:00.123456",
    "updated_at": "2024-01-15T10:32:00.111222"
}
```

**Status Values:**
- `pending`: Job created, waiting to start
- `processing`: Conversion in progress
- `completed`: Conversion successful
- `failed`: Conversion failed

**Error Responses:**

`404 Not Found` - Job not found
```json
{
    "error": "Job not found"
}
```

**Example (Python) - Polling:**
```python
import requests
import time

def wait_for_completion(job_id, poll_interval=2):
    """Poll job status until completion or failure."""
    while True:
        response = requests.get(f'http://localhost:5000/api/status/{job_id}')
        job = response.json()

        print(f"Progress: {job['progress']}% - {job['message']}")

        if job['status'] == 'completed':
            return job
        elif job['status'] == 'failed':
            raise Exception(f"Conversion failed: {job['error']}")

        time.sleep(poll_interval)

# Use it
job = wait_for_completion(job_id)
print(f"STL file: {job['stl_file']}")
```

**Example (JavaScript) - Polling:**
```javascript
async function waitForCompletion(jobId) {
    while (true) {
        const response = await fetch(`http://localhost:5000/api/status/${jobId}`);
        const job = await response.json();

        console.log(`Progress: ${job.progress}% - ${job.message}`);

        if (job.status === 'completed') {
            return job;
        } else if (job.status === 'failed') {
            throw new Error(`Conversion failed: ${job.error}`);
        }

        await new Promise(resolve => setTimeout(resolve, 2000));
    }
}

// Use it
const job = await waitForCompletion(jobId);
console.log('STL file:', job.stl_file);
```

---

### 5. Download STL File

Download the converted STL file.

**Endpoint:** `GET /api/download/<filename>`

**Request:**
```bash
curl -O http://localhost:5000/api/download/7c9e6679-7425-40de-944b-e07fc1f90ae7.stl
```

**Response:** `200 OK`
- Content-Type: `application/octet-stream`
- Content-Disposition: `attachment; filename="..."`
- Binary STL file data

**Error Responses:**

`404 Not Found` - File not found
```json
{
    "error": "File not found"
}
```

**Example (Python):**
```python
import requests

# Download STL file
response = requests.get(f'http://localhost:5000/api/download/{stl_filename}')

if response.status_code == 200:
    with open('output.stl', 'wb') as f:
        f.write(response.content)
    print('STL file downloaded successfully')
```

**Example (JavaScript):**
```javascript
// Trigger browser download
const downloadUrl = `http://localhost:5000/api/download/${stlFilename}`;
const a = document.createElement('a');
a.href = downloadUrl;
a.download = 'model.stl';
a.click();
```

---

### 6. Preview STL File

Get STL file for preview (without forcing download).

**Endpoint:** `GET /api/preview/<filename>`

**Request:**
```bash
curl http://localhost:5000/api/preview/7c9e6679-7425-40de-944b-e07fc1f90ae7.stl
```

**Response:** `200 OK`
- Content-Type: `application/sla`
- Binary STL file data

**Example (JavaScript with Three.js):**
```javascript
const loader = new THREE.STLLoader();
loader.load(
    `http://localhost:5000/api/preview/${stlFilename}`,
    (geometry) => {
        const material = new THREE.MeshPhongMaterial({ color: 0x3b82f6 });
        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);
    }
);
```

---

### 7. List All Jobs

Get list of all conversion jobs.

**Endpoint:** `GET /api/jobs`

**Request:**
```bash
curl http://localhost:5000/api/jobs
```

**Response:** `200 OK`
```json
{
    "jobs": [
        {
            "job_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
            "upload_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "completed",
            "progress": 100,
            "message": "Conversion completed successfully",
            "stl_file": "7c9e6679-7425-40de-944b-e07fc1f90ae7.stl",
            "error": null,
            "created_at": "2024-01-15T10:30:00.123456",
            "updated_at": "2024-01-15T10:33:15.987654"
        },
        {
            "job_id": "abc12345-1234-1234-1234-123456789abc",
            "upload_id": "def67890-5678-5678-5678-567890abcdef",
            "status": "processing",
            "progress": 75,
            "message": "Applying smoothing...",
            "stl_file": null,
            "error": null,
            "created_at": "2024-01-15T11:00:00.000000",
            "updated_at": "2024-01-15T11:02:30.123456"
        }
    ]
}
```

**Example (Python):**
```python
import requests

response = requests.get('http://localhost:5000/api/jobs')
jobs = response.json()['jobs']

for job in jobs:
    print(f"Job {job['job_id']}: {job['status']} ({job['progress']}%)")
```

---

### 8. Manual Cleanup

Trigger manual cleanup of old files.

**Endpoint:** `POST /api/cleanup`

**Request:**
```bash
curl -X POST http://localhost:5000/api/cleanup
```

**Response:** `200 OK`
```json
{
    "message": "Cleanup completed"
}
```

**Example (Python):**
```python
import requests

response = requests.post('http://localhost:5000/api/cleanup')
print(response.json()['message'])
```

---

## Complete Workflow Example

### Python

```python
import requests
import time
from pathlib import Path

API_BASE = 'http://localhost:5000/api'

def convert_dicom_to_stl(dicom_dir, output_file, threshold=100):
    """Complete DICOM to STL conversion workflow."""

    # 1. Upload files
    print("Uploading DICOM files...")
    files = []
    for dcm_file in Path(dicom_dir).glob('*.dcm'):
        files.append(('files', open(dcm_file, 'rb')))

    response = requests.post(f'{API_BASE}/upload', files=files)
    upload_id = response.json()['upload_id']
    print(f"Upload ID: {upload_id}")

    # Close file handles
    for _, fh in files:
        fh.close()

    # 2. Start conversion
    print("Starting conversion...")
    response = requests.post(f'{API_BASE}/convert', json={
        'upload_id': upload_id,
        'threshold': threshold,
        'smoothing': True,
        'decimation': 0.75
    })
    job_id = response.json()['job_id']
    print(f"Job ID: {job_id}")

    # 3. Poll for completion
    print("Waiting for conversion...")
    while True:
        response = requests.get(f'{API_BASE}/status/{job_id}')
        job = response.json()

        print(f"  {job['progress']}% - {job['message']}")

        if job['status'] == 'completed':
            break
        elif job['status'] == 'failed':
            raise Exception(f"Conversion failed: {job['error']}")

        time.sleep(2)

    # 4. Download STL
    print("Downloading STL file...")
    stl_filename = job['stl_file']
    response = requests.get(f'{API_BASE}/download/{stl_filename}')

    with open(output_file, 'wb') as f:
        f.write(response.content)

    print(f"Success! STL saved to: {output_file}")

# Use it
convert_dicom_to_stl(
    dicom_dir='path/to/dicom/files',
    output_file='output.stl',
    threshold=150
)
```

### JavaScript

```javascript
async function convertDicomToStl(files, threshold = 100) {
    const API_BASE = 'http://localhost:5000/api';

    // 1. Upload files
    console.log('Uploading DICOM files...');
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    let response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData
    });
    const uploadData = await response.json();
    const uploadId = uploadData.upload_id;
    console.log('Upload ID:', uploadId);

    // 2. Start conversion
    console.log('Starting conversion...');
    response = await fetch(`${API_BASE}/convert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            upload_id: uploadId,
            threshold: threshold,
            smoothing: true,
            decimation: 0.75
        })
    });
    const convertData = await response.json();
    const jobId = convertData.job_id;
    console.log('Job ID:', jobId);

    // 3. Poll for completion
    console.log('Waiting for conversion...');
    while (true) {
        response = await fetch(`${API_BASE}/status/${jobId}`);
        const job = await response.json();

        console.log(`${job.progress}% - ${job.message}`);

        if (job.status === 'completed') {
            // 4. Trigger download
            const downloadUrl = `${API_BASE}/download/${job.stl_file}`;
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = 'model.stl';
            a.click();
            console.log('Success!');
            break;
        } else if (job.status === 'failed') {
            throw new Error(`Conversion failed: ${job.error}`);
        }

        await new Promise(resolve => setTimeout(resolve, 2000));
    }
}

// Use it
const fileInput = document.getElementById('file-input');
convertDicomToStl(Array.from(fileInput.files), 150);
```

---

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource not found |
| 413 | Request Entity Too Large - File size exceeded |
| 500 | Internal Server Error |

### Best Practices

1. **Always check response status**
2. **Implement exponential backoff for polling**
3. **Handle network errors gracefully**
4. **Validate input before sending**
5. **Close file handles after upload**

---

## Rate Limiting Recommendations

For production deployment, consider implementing:
- Max requests per minute per IP
- Max concurrent conversions per user
- Request queuing system

---

## Support

For questions or issues:
- Check [README.md](README.md) for general documentation
- Review [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for architecture details
- Report bugs via GitHub Issues
