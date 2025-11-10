# MammoViewer - Project Overview

Comprehensive architecture and design documentation for the MammoViewer DICOM to STL converter.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Component Details](#component-details)
3. [Data Flow](#data-flow)
4. [Technology Stack](#technology-stack)
5. [Security](#security)
6. [Deployment](#deployment)
7. [Performance](#performance)
8. [Scalability](#scalability)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Web Browser                         │
│  ┌───────────┐  ┌──────────┐  ┌────────────────────────┐   │
│  │   HTML    │  │   CSS    │  │     JavaScript         │   │
│  │           │  │          │  │  - File upload         │   │
│  │ - Upload  │  │ - Styles │  │  - API calls           │   │
│  │ - Config  │  │ - Layout │  │  - Progress polling    │   │
│  │ - Results │  │          │  │  - 3D viewer (Three.js)│   │
│  └───────────┘  └──────────┘  └────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
                       │ (JSON + multipart/form-data)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      Flask Web Server                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    app.py (Main)                     │   │
│  │  - Route handlers                                    │   │
│  │  - Job management (threading)                        │   │
│  │  - File serving                                      │   │
│  └───────┬─────────────────────────┬────────────────────┘   │
│          │                         │                         │
│  ┌───────▼────────┐       ┌────────▼─────────┐              │
│  │ config.py      │       │  Background      │              │
│  │ - Settings     │       │  Worker Thread   │              │
│  │ - Validation   │       │  - Conversion    │              │
│  │ - Logging      │       │  - Status update │              │
│  └────────────────┘       └──────┬───────────┘              │
└──────────────────────────────────┼──────────────────────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
            ▼                      ▼                      ▼
┌───────────────────┐  ┌───────────────────┐  ┌──────────────────┐
│ dicom_processor.py│  │slicer_converter.py│  │   File System    │
│                   │  │                   │  │                  │
│ - DICOM reading   │  │ - Script gen      │  │ - uploads/       │
│ - Series grouping │  │ - Slicer exec     │  │ - outputs/       │
│ - Validation      │  │ - STL output      │  │ - temp/          │
│ - Preprocessing   │  │                   │  │ - logs/          │
└─────────┬─────────┘  └─────────┬─────────┘  └──────────────────┘
          │                      │
          │                      │
          ▼                      ▼
┌───────────────────┐  ┌──────────────────────────┐
│    SimpleITK      │  │      3D Slicer           │
│    pydicom        │  │                          │
│                   │  │ - DICOM import           │
│ - Image loading   │  │ - Segmentation           │
│ - Thresholding    │  │ - Morphological ops      │
│ - Morphology      │  │ - Model creation         │
└───────────────────┘  │ - Decimation             │
                       │ - STL export             │
                       └──────────────────────────┘
```

### Component Layers

**Layer 1: Presentation (Frontend)**
- HTML5 user interface
- CSS3 styling and animations
- JavaScript application logic
- Three.js 3D rendering

**Layer 2: Application (Backend)**
- Flask web framework
- RESTful API endpoints
- Request validation
- Response formatting

**Layer 3: Business Logic**
- DICOM processing
- 3D Slicer integration
- Job management
- File management

**Layer 4: Data Processing**
- SimpleITK image processing
- 3D Slicer segmentation
- VTK visualization

**Layer 5: Storage**
- File system storage
- Temporary file management
- Log file rotation

---

## Component Details

### Frontend Components

#### 1. Upload Interface
- **File**: `frontend/index.html`, `frontend/app.js`
- **Features**:
  - Drag-and-drop support
  - Multiple file selection
  - File validation
  - Progress indication
- **Technology**: Native JavaScript File API

#### 2. Parameter Controls
- **File**: `frontend/index.html`, `frontend/styles.css`
- **Controls**:
  - Threshold slider (10-1000)
  - Smoothing toggle
  - Decimation slider (10-100%)
- **Validation**: Client-side range checking

#### 3. Progress Tracker
- **File**: `frontend/app.js`
- **Features**:
  - Real-time progress bar
  - Status message display
  - Percentage indicator
- **Update Frequency**: 2-second polling

#### 4. 3D Viewer
- **File**: `frontend/app.js`
- **Library**: Three.js r128
- **Features**:
  - STL model loading
  - Orbit controls
  - Lighting and materials
  - Camera reset
- **Performance**: WebGL-accelerated

### Backend Components

#### 1. Flask Application (`app.py`)

**Responsibilities**:
- HTTP request handling
- Multipart file upload processing
- Job queue management
- Background thread coordination
- Static file serving

**Threading Model**:
```python
Main Thread                 Worker Threads
    │                            │
    ├─ Handle requests           │
    │                            │
    ├─ Create job ──────────────►├─ Process DICOM
    │                            ├─ Call Slicer
    ├─ Return job_id             ├─ Generate STL
    │                            ├─ Update job status
    ├─ Poll status ◄─────────────┤
    │                            │
    └─ Return results            └─ Thread exits
```

**Job States**:
1. `pending`: Job created, waiting to start
2. `processing`: Active conversion
3. `completed`: Successful conversion
4. `failed`: Error occurred

#### 2. Configuration (`config.py`)

**Configuration Categories**:

```python
# Paths
BASE_DIR, UPLOAD_FOLDER, OUTPUT_FOLDER, TEMP_FOLDER, LOG_FOLDER

# Flask
SECRET_KEY, DEBUG, HOST, PORT

# Upload limits
MAX_FILE_SIZE = 500MB
MAX_FILES_PER_UPLOAD = 100
ALLOWED_EXTENSIONS = {dcm, dicom, DCM, DICOM}

# 3D Slicer
SLICER_PATH (platform-dependent)

# Conversion
THRESHOLD_DEFAULT = 100
SMOOTHING_ITERATIONS = 15
DECIMATION_RATE = 0.75

# Cleanup
AUTO_CLEANUP = True
CLEANUP_AFTER_HOURS = 24
```

**Validation**:
- Directory creation
- Path existence checks
- Value range validation

#### 3. DICOM Processor (`dicom_processor.py`)

**Processing Pipeline**:

```
DICOM Files
    │
    ├─► discover_dicom_files()
    │       └─► is_dicom_file() for each
    │
    ├─► organize_by_series()
    │       └─► Group by SeriesInstanceUID
    │
    ├─► validate_series()
    │       ├─► Check min slices
    │       └─► Check dimension consistency
    │
    ├─► load_series_as_volume()
    │       ├─► Sort files
    │       └─► SimpleITK.ImageSeriesReader
    │
    └─► preprocess_volume()
            ├─► BinaryThreshold
            ├─► MorphologicalClosing
            └─► FillHoles
```

**Metadata Extraction**:
- PatientID, PatientName
- StudyDate, StudyDescription
- SeriesDescription, Modality
- Manufacturer
- Dimensions (rows, columns, slices)
- Spacing (pixel spacing, slice thickness)

#### 4. Slicer Converter (`slicer_converter.py`)

**Conversion Workflow**:

```
1. Create Python script for Slicer
   ├─► Set parameters
   ├─► Define DICOM import
   ├─► Configure segmentation
   └─► Set export options

2. Execute Slicer in batch mode
   ├─► Run with --python-script flag
   ├─► Use --no-splash, --no-main-window
   └─► (Linux) Wrap with xvfb-run

3. Monitor execution
   ├─► Capture stdout/stderr
   ├─► Check for timeout (600s default)
   └─► Look for success/error markers

4. Verify output
   ├─► Check STL file exists
   ├─► Validate file size
   └─► Return success/failure
```

**Slicer Script Operations**:
1. Initialize DICOM database
2. Import DICOM files
3. Load series
4. Create segmentation
5. Apply threshold
6. Morphological closing (kernel: 3mm)
7. Median smoothing (15 iterations)
8. Export to 3D model
9. Quadric decimation
10. Save as STL

---

## Data Flow

### Complete Conversion Flow

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │ 1. Select DICOM files
       ▼
┌─────────────────┐
│ Frontend        │
│ - Validate files│
│ - Create FormData
└──────┬──────────┘
       │ 2. POST /api/upload
       ▼
┌─────────────────┐
│ Flask           │
│ - Receive files │
│ - Save to disk  │
│ - Return upload_id
└──────┬──────────┘
       │ 3. upload_id
       ▼
┌─────────────────┐
│ Frontend        │
│ - Show parameters
│ - User adjusts  │
└──────┬──────────┘
       │ 4. POST /api/convert
       ▼
┌─────────────────┐
│ Flask           │
│ - Create job    │
│ - Start thread  │
│ - Return job_id │
└──────┬──────────┘
       │ 5. job_id
       ▼
┌─────────────────┐        ┌──────────────────┐
│ Frontend        │        │ Worker Thread    │
│ - Poll status   │◄───────┤ - Process DICOM  │
│   every 2s      │  updates│ - Call Slicer   │
└─────────────────┘        │ - Generate STL   │
       │                   └──────────────────┘
       │ 6. status: completed
       ▼
┌─────────────────┐
│ Frontend        │
│ - Show results  │
│ - Enable download
└──────┬──────────┘
       │ 7. GET /api/download
       ▼
┌─────────────────┐
│ Flask           │
│ - Send STL file │
└─────────────────┘
```

### File System Data Flow

```
Upload:
DICOM files → uploads/{upload_id}/file*.dcm

Processing:
uploads/{upload_id}/ → DICOM Processor
                     → temp/{upload_id}/dicom_temp_db/
                     → 3D Slicer
                     → outputs/{job_id}.stl

Download:
outputs/{job_id}.stl → User's browser

Cleanup (after 24h):
uploads/{upload_id}/ → deleted
outputs/{job_id}.stl → deleted
temp/{upload_id}/    → deleted
```

---

## Technology Stack

### Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Core language |
| Flask | 3.0.0 | Web framework |
| Flask-CORS | 4.0.0 | CORS handling |
| pydicom | 2.4.4 | DICOM file parsing |
| SimpleITK | 2.3.1 | Medical image processing |
| numpy | 1.24.3 | Numerical operations |
| VTK | 9.3.0 | Visualization toolkit |
| 3D Slicer | 5.0+ | 3D reconstruction |
| loguru | 0.7.2 | Structured logging |
| werkzeug | 3.0.1 | WSGI utilities |

### Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| HTML5 | - | Structure |
| CSS3 | - | Styling |
| JavaScript | ES6+ | Logic |
| Three.js | r128 | 3D rendering |
| Fetch API | - | HTTP requests |

### Infrastructure

| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |
| Xvfb | Headless display (Linux) |
| Nginx | Reverse proxy (production) |
| Gunicorn | WSGI server (production) |

---

## Security

### Input Validation

**File Upload**:
```python
# Size validation
MAX_FILE_SIZE = 500MB

# Extension validation
ALLOWED_EXTENSIONS = {'dcm', 'dicom', 'DCM', 'DICOM'}

# Filename sanitization
from werkzeug.utils import secure_filename
filename = secure_filename(file.filename)
```

**Parameter Validation**:
```python
# Threshold range
THRESHOLD_MIN <= threshold <= THRESHOLD_MAX

# Decimation range
0.0 <= decimation <= 1.0
```

### File System Security

**Path Isolation**:
- Each upload gets unique UUID directory
- No user-provided paths accepted
- All paths use `Path.resolve()` to prevent traversal

**File Permissions**:
- Upload directories: 0755
- Output files: 0644
- Temp files: Auto-cleanup

### Network Security

**CORS**:
- Configured via Flask-CORS
- Production: Whitelist specific origins

**HTTPS**:
- Recommended for production
- Use reverse proxy (nginx) for SSL termination

**Authentication** (not implemented):
- Recommend: JWT tokens
- API keys for programmatic access
- Rate limiting per user/IP

### Data Privacy

**DICOM Anonymization**:
- Not implemented by default
- Recommend: Remove PHI before upload
- Consider: Automatic anonymization module

**Storage**:
- Auto-cleanup after 24 hours
- No permanent storage of PHI
- Logs: Exclude patient data

---

## Deployment

### Development Deployment

```bash
# Local development
python backend/app.py

# Configuration
DEBUG=True
HOST=localhost
PORT=5000
```

### Production Deployment

#### Option 1: Traditional Server

```bash
# Install dependencies
pip install -r backend/requirements.txt
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app

# Configure nginx reverse proxy
nginx.conf:
  location / {
    proxy_pass http://localhost:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
```

**Production Settings**:
```
DEBUG=False
SECRET_KEY=<strong-random-key>
SLICER_PATH=/opt/Slicer/Slicer
AUTO_CLEANUP=True
LOG_LEVEL=WARNING
```

#### Option 2: Docker

```bash
# Build and run
docker-compose up -d

# Scale workers
docker-compose up -d --scale app=4

# View logs
docker-compose logs -f
```

#### Option 3: Cloud Platform

**AWS Elastic Beanstalk**:
- Use Docker platform
- Configure autoscaling
- S3 for file storage
- CloudFront for static assets

**Google Cloud Run**:
- Containerized deployment
- Auto-scaling
- Cloud Storage for files
- Load balancer

**Heroku**:
- Use Docker deployment
- Dyno sizing for workers
- Temporary file system (ephemeral)

### System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 4 GB
- Disk: 20 GB
- 3D Slicer installed

**Recommended**:
- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 100+ GB SSD
- GPU: Optional (for faster rendering)

---

## Performance

### Optimization Strategies

#### Backend Optimizations

**1. Async Processing**:
- Background threads for conversion
- Non-blocking API responses
- Status polling instead of blocking

**2. Caching**:
- DICOM metadata caching
- Series information caching
- Static file caching (browser)

**3. File Handling**:
- Streaming large file uploads
- Chunked file downloads
- Efficient file system operations

#### Frontend Optimizations

**1. Asset Loading**:
- CDN for Three.js libraries
- Minified CSS/JS (production)
- Lazy loading for 3D viewer

**2. API Calls**:
- Debounced status polling
- Request batching
- Abort on component unmount

**3. 3D Rendering**:
- STL decimation to reduce polygon count
- Level-of-detail rendering
- WebGL optimization

### Performance Metrics

**Typical Conversion Times**:
| Dataset Size | Slices | Time (approx) |
|--------------|--------|---------------|
| Small | 20-30 | 1-2 minutes |
| Medium | 50-80 | 2-4 minutes |
| Large | 100+ | 4-8 minutes |

**Factors Affecting Performance**:
- CPU speed
- Available RAM
- Disk I/O speed
- File size
- Conversion parameters (smoothing, decimation)

### Monitoring

**Metrics to Track**:
- Request rate (requests/minute)
- Conversion success rate
- Average conversion time
- Disk usage
- Memory usage
- Error rate

**Tools**:
- Application logs (loguru)
- System monitoring (top, htop)
- Docker stats
- APM tools (New Relic, Datadog)

---

## Scalability

### Horizontal Scaling

**Load Balancer Architecture**:

```
                    ┌──────────────┐
                    │Load Balancer │
                    │   (nginx)    │
                    └───────┬──────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Flask App 1  │    │ Flask App 2  │    │ Flask App 3  │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │  Shared NFS   │
                   │   Storage     │
                   └───────────────┘
```

**Requirements**:
- Shared file storage (NFS, S3)
- Session affinity or distributed sessions
- Shared job queue (Redis, RabbitMQ)

### Vertical Scaling

**Resource Allocation**:
- Add more CPU cores (parallel processing)
- Increase RAM (larger datasets)
- Faster disk (SSD/NVMe)
- GPU acceleration (future enhancement)

### Queue-Based Architecture

**For High Volume**:

```
Upload → Redis Queue → Worker Pool → Output
                      ↓
                   Job Status DB
```

**Implementation**:
- Use Celery for task queue
- Redis/RabbitMQ as message broker
- Multiple worker processes
- Job persistence in database

### Database Integration

**For Job Persistence**:

```python
# Replace in-memory jobs dict with database
# Using SQLAlchemy

class ConversionJob(Base):
    __tablename__ = 'jobs'
    job_id = Column(String, primary_key=True)
    upload_id = Column(String)
    status = Column(String)
    progress = Column(Integer)
    # ... etc
```

**Benefits**:
- Job history
- Analytics
- Crash recovery
- Multi-instance coordination

### Cloud Storage

**For Large Scale**:

```python
# Replace local file system with S3

import boto3
s3 = boto3.client('s3')

# Upload
s3.upload_file(local_file, bucket, key)

# Download
s3.download_file(bucket, key, local_file)
```

**Benefits**:
- Unlimited storage
- High availability
- Durability
- CDN integration

---

## Future Enhancements

### Planned Features

1. **Authentication & Authorization**
   - User accounts
   - API keys
   - Role-based access

2. **Advanced Segmentation**
   - Multiple threshold regions
   - Machine learning segmentation
   - Manual editing tools

3. **Additional Output Formats**
   - OBJ, PLY, OFF formats
   - Colored models
   - Texture mapping

4. **Batch Processing API**
   - Multiple series at once
   - Scheduled conversions
   - Webhook notifications

5. **Analytics Dashboard**
   - Conversion statistics
   - Resource usage graphs
   - User activity logs

6. **Cloud Integration**
   - AWS S3 storage
   - Google Cloud Storage
   - Azure Blob Storage

### Architecture Evolution

**Phase 1**: Current (Monolithic)
- Single Flask application
- File system storage
- In-memory job tracking

**Phase 2**: Microservices
- Separate upload service
- Conversion service
- Viewer service
- API gateway

**Phase 3**: Serverless
- Lambda functions for conversion
- S3 for storage
- DynamoDB for jobs
- CloudFront for delivery

---

## Troubleshooting

### Common Issues

**Issue**: 3D Slicer not found
**Solution**: Set correct SLICER_PATH in .env

**Issue**: Conversion timeout
**Solution**: Increase timeout in slicer_converter.py

**Issue**: Out of memory
**Solution**: Reduce dataset size or increase decimation

**Issue**: Port already in use
**Solution**: Change PORT in .env or kill process

### Debug Mode

Enable debug logging:
```python
# In .env
DEBUG=True
LOG_LEVEL=DEBUG
```

View detailed logs:
```bash
tail -f logs/mammoviewer_*.log
```

---

## Contributing

See [README.md](README.md) for contribution guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**Document Version**: 1.0
**Last Updated**: 2024-01-15
**Maintained By**: MammoViewer Development Team
