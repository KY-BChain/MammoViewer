# MammoViewer - File Reference

Complete file-by-file reference for the MammoViewer project.

## Table of Contents

1. [Backend Files](#backend-files)
2. [Frontend Files](#frontend-files)
3. [Configuration Files](#configuration-files)
4. [Documentation Files](#documentation-files)
5. [Setup Scripts](#setup-scripts)
6. [Directories](#directories)

---

## Backend Files

### backend/app.py

**Purpose**: Main Flask application and API server

**Lines**: ~400

**Key Components**:
- `ConversionJob` dataclass: Tracks conversion job state
- `process_conversion_job()`: Background thread for DICOM to STL conversion
- `cleanup_old_files()`: Scheduled cleanup of old uploads/outputs

**API Endpoints**:
1. `GET /` - Serve frontend
2. `GET /api/health` - Health check
3. `POST /api/upload` - Upload DICOM files
4. `POST /api/convert` - Start conversion
5. `GET /api/status/<job_id>` - Get job status
6. `GET /api/download/<filename>` - Download STL file
7. `GET /api/preview/<filename>` - Preview STL file
8. `GET /api/jobs` - List all jobs
9. `POST /api/cleanup` - Manual cleanup

**Dependencies**:
- Flask, Flask-CORS
- Threading for background processing
- config, dicom_processor, slicer_converter modules

**Error Handlers**: 400, 404, 413, 500

---

### backend/config.py

**Purpose**: Configuration settings and validation

**Lines**: ~150

**Key Components**:
- Path configuration (BASE_DIR, UPLOAD_FOLDER, OUTPUT_FOLDER, etc.)
- Flask settings (SECRET_KEY, DEBUG, HOST, PORT)
- Upload limits (MAX_FILE_SIZE, MAX_FILES_PER_UPLOAD, ALLOWED_EXTENSIONS)
- 3D Slicer path configuration
- Conversion parameters (threshold, smoothing, decimation)
- Cleanup settings (AUTO_CLEANUP, CLEANUP_AFTER_HOURS)
- Logging configuration

**Functions**:
- `validate_config()`: Validates settings and creates directories
- `setup_logging()`: Configures loguru logging

**Platform-specific**:
- Detects OS and sets appropriate default Slicer paths

---

### backend/dicom_processor.py

**Purpose**: DICOM file processing and validation

**Lines**: ~400

**Class**: `DICOMProcessor`

**Methods**:
- `__init__(dicom_dir)`: Initialize processor
- `discover_dicom_files()`: Find all DICOM files in directory
- `is_dicom_file(path)`: Static method to validate DICOM format
- `organize_by_series()`: Group files by SeriesInstanceUID
- `extract_metadata(series_uid)`: Get series metadata
- `validate_series(series_uid, min_slices)`: Validate series for conversion
- `load_series_as_volume(series_uid)`: Load as SimpleITK Image
- `_sort_dicom_files(files)`: Sort by InstanceNumber/SliceLocation
- `preprocess_volume(image, threshold)`: Apply thresholding and morphology
- `save_volume(image, path)`: Save volume to file
- `get_series_info()`: Get info for all series
- `export_metadata_json(path)`: Export metadata to JSON

**Dependencies**:
- pydicom: DICOM file reading
- SimpleITK: Medical image processing
- numpy: Array operations
- loguru: Logging

---

### backend/slicer_converter.py

**Purpose**: 3D Slicer integration for DICOM to STL conversion

**Lines**: ~450

**Class**: `SlicerConverter`

**Methods**:
- `__init__(slicer_path)`: Initialize converter
- `validate_slicer()`: Check if Slicer executable exists
- `convert_dicom_to_stl()`: Main conversion function
- `_create_conversion_script(params)`: Generate Python script for Slicer
- `_run_slicer_script(script_path, timeout)`: Execute script in Slicer
- `batch_convert(dicom_dirs, output_dir)`: Batch process multiple directories

**Generated Slicer Script Steps**:
1. Import DICOM database
2. Load series
3. Create segmentation
4. Apply threshold
5. Morphological operations (closing, smoothing)
6. Export to 3D model
7. Apply decimation
8. Save STL file
9. Write success/error markers

**Dependencies**:
- subprocess: Execute Slicer
- config: Configuration settings
- loguru: Logging

**Platform-specific**:
- Uses `xvfb-run` on Linux for headless operation

---

### backend/requirements.txt

**Purpose**: Python package dependencies

**Lines**: ~25

**Key Packages**:
- Flask==3.0.0 - Web framework
- Flask-CORS==4.0.0 - CORS support
- pydicom==2.4.4 - DICOM handling
- SimpleITK==2.3.1 - Medical image processing
- numpy==1.24.3 - Numerical operations
- vtk==9.3.0 - Visualization toolkit
- pyvista==0.43.0 - 3D visualization
- loguru==0.7.2 - Logging
- python-dotenv==1.0.0 - Environment variables

**Total Packages**: 23

---

## Frontend Files

### frontend/index.html

**Purpose**: Main web interface

**Lines**: ~250

**Sections**:
1. **Header**: Title and subtitle with gradient background
2. **Upload Section**: Drag-drop zone, file input, file list
3. **Parameters Section**: Threshold, smoothing, decimation controls
4. **Progress Section**: Progress bar and status text
5. **Results Section**: Success message, action buttons
6. **3D Viewer Section**: Three.js canvas with controls
7. **Error Section**: Error display and retry button
8. **Footer**: Credits and links
9. **About Modal**: Feature list and information

**External Libraries**:
- Three.js r128 (CDN)
- STLLoader.js (CDN)
- OrbitControls.js (CDN)

**Interactive Elements**:
- File drag-and-drop
- Range sliders
- Checkboxes
- Buttons
- 3D canvas

---

### frontend/styles.css

**Purpose**: Styling and visual design

**Lines**: ~600

**Features**:
- CSS variables for theming
- Gradient header (purple to blue)
- Card-based layout
- Drag-drop hover effects
- Custom range sliders
- Progress bar animations
- 3D viewer dark theme
- Button styles (primary, secondary, success)
- Modal styling
- Responsive design (@media queries)
- Smooth transitions and animations

**Color Scheme**:
- Primary: #2563eb (blue)
- Success: #10b981 (green)
- Error: #ef4444 (red)
- Background: #f8fafc (light gray)
- Viewer: #1e293b (dark blue)

**Responsive Breakpoints**:
- Mobile: < 768px

---

### frontend/app.js

**Purpose**: Frontend application logic

**Lines**: ~500

**Global State**:
- `uploadedFiles`: Selected files
- `uploadId`: Upload identifier
- `jobId`: Conversion job identifier
- `stlFileName`: Generated STL filename
- `scene`, `camera`, `renderer`, `controls`, `model`: Three.js objects

**Key Functions**:

**File Handling**:
- `handleFileSelect()`: Process file input
- `handleDragOver/Drop/Leave()`: Drag-and-drop handling
- `processFiles()`: Validate and store files
- `displayFileList()`: Show selected files
- `formatFileSize()`: Format bytes to human-readable

**API Communication**:
- `uploadFilesToServer()`: POST files to /api/upload
- `startConversion()`: POST to /api/convert
- `checkJobStatus()`: GET from /api/status
- `downloadSTL()`: Trigger file download

**Progress Tracking**:
- `startStatusPolling()`: Start 2-second polling
- `updateProgress()`: Update progress UI

**3D Viewer**:
- `init3DViewer()`: Initialize Three.js scene
- `loadSTLModel()`: Load and display STL
- `animate()`: Render loop
- `resetCamera()`: Reset view

**UI Control**:
- `showSection()`: Show/hide sections
- `showError()`: Display error message
- `resetApplication()`: Reset to initial state

---

## Configuration Files

### .gitignore

**Purpose**: Git ignore patterns

**Lines**: ~30

**Ignores**:
- Python: `__pycache__/`, `*.pyc`, `*.pyo`, `*.pyd`, `.Python`, `venv/`
- Project: `uploads/`, `outputs/`, `temp/`, `logs/`, `slicer_scripts/*.py`
- Environment: `.env`, `.env.local`
- IDE: `.vscode/`, `.idea/`, `*.swp`
- OS: `.DS_Store`, `Thumbs.db`
- Build: `build/`, `dist/`, `*.egg-info`

---

### .env.example

**Purpose**: Environment variable template

**Lines**: ~20

**Variables**:
```
# Flask
SECRET_KEY=change-this-to-a-random-secret-key
DEBUG=True
HOST=0.0.0.0
PORT=5000

# 3D Slicer paths (uncomment for your OS)
# macOS
#SLICER_PATH=/Applications/Slicer.app/Contents/MacOS/Slicer
# Windows
#SLICER_PATH=C:\Program Files\Slicer 5.4.0\Slicer.exe
# Linux
#SLICER_PATH=/opt/Slicer/Slicer

# Cleanup
AUTO_CLEANUP=True
CLEANUP_AFTER_HOURS=24

# Logging
LOG_LEVEL=INFO
```

---

### docker-compose.yml

**Purpose**: Docker orchestration configuration

**Lines**: ~40

**Services**:
1. **app**: Main Flask application
   - Build: Current directory
   - Ports: 5000:5000
   - Volumes: uploads, outputs, logs
   - Environment: Configuration variables
   - Depends on: redis (if needed)

2. **redis** (optional): Job queue backend
   - Image: redis:7-alpine
   - Ports: 6379:6379

**Volumes**:
- `uploads_data`
- `outputs_data`
- `logs_data`

**Networks**: `mammoviewer_network`

---

### Dockerfile

**Purpose**: Docker image definition

**Lines**: ~60

**Base Image**: Ubuntu 22.04

**Installation Steps**:
1. Update apt and install dependencies
2. Install Python 3.10
3. Install 3D Slicer (download and extract)
4. Install Xvfb for headless operation
5. Copy application files
6. Install Python dependencies
7. Create directories
8. Expose port 5000
9. Set environment variables
10. Run Flask application

**Volumes**: `/app/uploads`, `/app/outputs`, `/app/logs`

---

### LICENSE

**Purpose**: Software license

**Lines**: ~200

**License Type**: MIT License

**Content**:
- Copyright notice
- Permission grant
- Liability disclaimer
- Third-party license notices:
  - 3D Slicer (BSD-style)
  - Three.js (MIT)
  - Flask (BSD)
  - SimpleITK (Apache 2.0)

---

## Documentation Files

### README.md

**Purpose**: Main project documentation

**Lines**: ~500

**Sections**:
- Project overview and features
- Technology stack
- Prerequisites
- Installation (standard and Docker)
- Usage guide
- Configuration
- Testing data sources
- Project structure
- Troubleshooting
- Development guidelines
- Contributing
- License and acknowledgments

---

### QUICKSTART.md

**Purpose**: 5-minute setup guide

**Lines**: ~300

**Sections**:
- Prerequisites checklist
- 5-minute setup steps
- Sample data download
- First conversion walkthrough
- Docker quick start
- Installation verification
- Common issues and quick fixes
- Next steps
- Quick reference commands

---

### API_DOCUMENTATION.md

**Purpose**: Complete REST API reference

**Lines**: ~800

**Sections**:
- Base URL and authentication
- Response format
- All 8 API endpoints with:
  - Request format
  - Parameters
  - Response examples
  - Error responses
  - Code examples (Python and JavaScript)
- Complete workflow examples
- Error handling guide
- Rate limiting recommendations

---

### PROJECT_OVERVIEW.md

**Purpose**: Detailed architecture documentation

**Lines**: ~600

**Sections**:
- System architecture
- Component diagrams
- Data flow
- Technology stack details
- Security considerations
- Deployment options
- Performance optimization
- Scaling strategies

---

### FILE_REFERENCE.md

**Purpose**: File-by-file reference (this document)

**Lines**: ~800

**Sections**:
- Backend files
- Frontend files
- Configuration files
- Documentation files
- Setup scripts
- Directories

---

### PROJECT_SUMMARY.md

**Purpose**: Quick project overview

**Lines**: ~300

**Sections**:
- Overview
- Key features
- Technology stack
- Architecture diagram
- Getting started
- Core workflow
- API endpoints summary
- Configuration
- Use cases
- Performance metrics

---

## Setup Scripts

### setup.sh

**Purpose**: Linux/macOS setup automation

**Lines**: ~150

**Features**:
- Check Python version (3.8+)
- Create virtual environment
- Install dependencies from requirements.txt
- Create necessary directories
- Detect 3D Slicer installation
- Create .env file if not exists
- Display next steps

**Requirements**: bash, python3, pip

---

### setup.bat

**Purpose**: Windows setup automation

**Lines**: ~150

**Features**:
- Check Python version
- Create virtual environment
- Install dependencies
- Create directories
- Detect Slicer on Windows
- Create .env file
- Display next steps

**Requirements**: Windows command prompt, Python 3.8+

---

### test_installation.py

**Purpose**: Verify installation correctness

**Lines**: ~200

**Tests**:
1. Python version (>= 3.8)
2. Required packages installed
3. Directories exist and writable
4. Configuration valid
5. 3D Slicer path exists
6. Import all backend modules
7. Flask app imports correctly

**Output**: Pass/fail for each test with summary

**Usage**:
```bash
python test_installation.py
```

---

## Directories

### uploads/

**Purpose**: Store uploaded DICOM files

**Structure**:
```
uploads/
└── {upload_id}/
    ├── file1.dcm
    ├── file2.dcm
    └── ...
```

**Auto-created**: Yes
**Auto-cleanup**: After 24 hours (configurable)
**Gitignored**: Yes

---

### outputs/

**Purpose**: Store generated STL files

**Structure**:
```
outputs/
├── {job_id}.stl
└── {job_id}.stl.success  (marker)
```

**Auto-created**: Yes
**Auto-cleanup**: After 24 hours (configurable)
**Gitignored**: Yes

---

### temp/

**Purpose**: Temporary processing files

**Structure**:
```
temp/
└── {upload_id}/
    ├── dicom_temp_db/
    └── intermediate files
```

**Auto-created**: Yes
**Auto-cleanup**: After 24 hours
**Gitignored**: Yes

---

### logs/

**Purpose**: Application log files

**Structure**:
```
logs/
├── mammoviewer_2024-01-15_10-00-00.log
├── mammoviewer_2024-01-15_14-30-15.log
└── ...
```

**Auto-created**: Yes
**Rotation**: 100 MB
**Retention**: 1 week
**Gitignored**: Yes

---

### slicer_scripts/

**Purpose**: Generated 3D Slicer Python scripts

**Structure**:
```
slicer_scripts/
├── convert_1705320000.py
├── convert_1705320123.py
└── ...
```

**Auto-created**: Yes
**Auto-cleanup**: After execution
**Gitignored**: Yes (*.py files)

---

### frontend/

**Purpose**: Frontend web application files

**Structure**:
```
frontend/
├── index.html
├── styles.css
└── app.js
```

**Served by**: Flask static file handler
**Gitignored**: No

---

### backend/

**Purpose**: Backend Python application

**Structure**:
```
backend/
├── __init__.py  (empty, makes it a package)
├── app.py
├── config.py
├── dicom_processor.py
├── slicer_converter.py
└── requirements.txt
```

**Gitignored**: `__pycache__/`, `*.pyc`

---

## File Statistics

### Total Files: 22

**By Category**:
- Backend: 5 files
- Frontend: 3 files
- Documentation: 6 files
- Configuration: 5 files
- Setup: 3 files

**By Type**:
- Python (`.py`): 5 files
- Markdown (`.md`): 6 files
- JavaScript (`.js`): 1 file
- HTML (`.html`): 1 file
- CSS (`.css`): 1 file
- Config (`.yml`, `.env`, etc.): 5 files
- Shell (`.sh`, `.bat`): 2 files
- Text (`.txt`): 2 files

### Total Lines of Code: ~5,500

**By Category**:
- Python: ~1,600 lines
- JavaScript: ~500 lines
- HTML: ~250 lines
- CSS: ~600 lines
- Documentation: ~2,500 lines
- Configuration: ~200 lines

---

## Dependencies Graph

```
app.py
├── config.py
│   └── loguru
├── dicom_processor.py
│   ├── pydicom
│   ├── SimpleITK
│   └── numpy
├── slicer_converter.py
│   ├── config.py
│   └── subprocess
└── Flask ecosystem
    ├── Flask
    ├── Flask-CORS
    └── werkzeug
```

---

## Build & Deployment Files

Not included but recommended for production:

- `.dockerignore` - Docker build exclusions
- `gunicorn_config.py` - Gunicorn WSGI server config
- `nginx.conf` - Nginx reverse proxy config
- `.github/workflows/` - CI/CD pipelines
- `requirements-dev.txt` - Development dependencies
- `pytest.ini` - Test configuration
- `pyproject.toml` - Python project metadata

---

## Maintenance

**Regular Tasks**:
1. Update dependencies: `pip install -r backend/requirements.txt --upgrade`
2. Check logs: `tail -f logs/mammoviewer_*.log`
3. Monitor disk usage: `du -sh uploads outputs temp`
4. Run tests: `python test_installation.py`

**Backup Priority**:
- Critical: `.env`, configuration files
- Important: Documentation
- Optional: Logs, temporary files
- Never: `venv/`, `__pycache__/`, uploads/outputs (unless needed)

---

For detailed information about specific files, see their inline comments and docstrings.
