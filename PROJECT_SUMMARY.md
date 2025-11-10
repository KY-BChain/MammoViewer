# MammoViewer - Project Summary

## Overview

MammoViewer is a professional web application that converts mammography DICOM medical images into 3D printable STL models using 3D Slicer.

## Key Features

- **Drag-and-Drop Upload**: Easy DICOM file upload (up to 100 files, 500MB)
- **Customizable Conversion**: Adjustable threshold, smoothing, and decimation parameters
- **Real-time Progress**: Live conversion progress tracking
- **3D Preview**: Interactive Three.js-based 3D model viewer
- **RESTful API**: Complete REST API for programmatic access
- **Docker Support**: Containerized deployment
- **Auto Cleanup**: Automatic removal of old files

## Technology Stack

### Backend
- **Python 3.8+** with Flask web framework
- **SimpleITK** for medical image processing
- **pydicom** for DICOM file handling
- **3D Slicer** for 3D reconstruction and STL export
- **VTK** for visualization

### Frontend
- **HTML5/CSS3/JavaScript** with modern responsive design
- **Three.js** for 3D model rendering and interaction
- **Fetch API** for asynchronous requests

### Infrastructure
- **Docker** and Docker Compose for containerization
- **Xvfb** for headless Linux environments
- **loguru** for structured logging

## Architecture

```
┌─────────────────┐
│   Web Browser   │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  Flask Server   │
│   (Backend)     │
└────────┬────────┘
         │
    ┌────┴─────┐
    ▼          ▼
┌────────┐  ┌─────────┐
│ DICOM  │  │   3D    │
│Process │  │ Slicer  │
└────────┘  └─────────┘
                │
                ▼
            ┌────────┐
            │  STL   │
            │  File  │
            └────────┘
```

## Directory Structure

```
MammoViewer/
├── backend/           # Python Flask application
├── frontend/          # HTML/CSS/JS web interface
├── uploads/           # Uploaded DICOM files
├── outputs/           # Generated STL files
├── temp/              # Temporary processing files
├── logs/              # Application logs
└── slicer_scripts/    # Generated Slicer scripts
```

## Getting Started

### Quick Install

```bash
# 1. Clone repository
git clone https://github.com/yourusername/MammoViewer.git
cd MammoViewer

# 2. Run setup
./setup.sh  # macOS/Linux
setup.bat   # Windows

# 3. Configure Slicer path
cp .env.example .env
# Edit .env with your Slicer path

# 4. Start application
source venv/bin/activate
python backend/app.py

# 5. Open browser
# http://localhost:5000
```

### Docker Install

```bash
docker-compose up --build
# http://localhost:5000
```

## Core Workflow

1. **Upload**: User uploads DICOM files via web interface or API
2. **Process**: Backend organizes files and validates DICOM series
3. **Convert**: 3D Slicer converts DICOM to 3D model with specified parameters
4. **Output**: STL file generated and available for download/preview
5. **View**: Interactive 3D preview in browser using Three.js

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/upload` | Upload DICOM files |
| POST | `/api/convert` | Start conversion |
| GET | `/api/status/<job_id>` | Check job status |
| GET | `/api/download/<filename>` | Download STL |
| GET | `/api/preview/<filename>` | Preview STL |
| GET | `/api/jobs` | List all jobs |
| POST | `/api/cleanup` | Manual cleanup |

## Configuration

### Environment Variables

```bash
# Flask
SECRET_KEY=your-secret-key
DEBUG=False
HOST=0.0.0.0
PORT=5000

# 3D Slicer
SLICER_PATH=/path/to/Slicer

# Conversion
THRESHOLD_DEFAULT=100
SMOOTHING_ITERATIONS=15
DECIMATION_RATE=0.75

# Cleanup
AUTO_CLEANUP=True
CLEANUP_AFTER_HOURS=24
```

## Use Cases

### Medical Research
- Create 3D models from mammography scans for research
- Visualize tissue structures in 3D
- Educational demonstrations

### 3D Printing
- Generate printable models from medical imaging
- Create physical models for surgical planning
- Patient education with tactile models

### Software Integration
- Embed DICOM conversion in medical imaging workflows
- Batch process large datasets via API
- Integrate with PACS systems

## Performance

**Typical Conversion Times:**
- Small series (20-30 slices): 1-2 minutes
- Medium series (50-80 slices): 2-4 minutes
- Large series (100+ slices): 4-8 minutes

*Times vary based on hardware, file size, and conversion parameters*

## Security Considerations

- **Input Validation**: All file uploads validated for type and size
- **File Isolation**: Each upload gets unique directory
- **Auto Cleanup**: Old files removed automatically
- **Path Security**: Uses `secure_filename()` to prevent path traversal
- **Production**: Set `DEBUG=False`, use HTTPS, implement authentication

## Testing Data Sources

Download public mammography datasets:
- [The Cancer Imaging Archive (TCIA)](https://www.cancerimagingarchive.net/)
- CBIS-DDSM (Curated Breast Imaging Subset of DDSM)
- Other public breast imaging collections

## Dependencies

**Critical Dependencies:**
- Python 3.8+
- 3D Slicer 5.0+
- Flask 3.0+
- SimpleITK 2.3+
- pydicom 2.4+

**See `backend/requirements.txt` for complete list**

## File Count

- **Total Files**: 22
- **Backend**: 5 files
- **Frontend**: 3 files
- **Documentation**: 6 files
- **Configuration**: 5 files
- **Scripts**: 3 files

## Lines of Code (Approximate)

- Backend Python: ~1,200 lines
- Frontend JavaScript: ~500 lines
- Frontend HTML/CSS: ~600 lines
- Total: ~2,300 lines

## License

MIT License - Free for commercial and non-commercial use

## Third-Party Components

- **3D Slicer**: BSD-style license
- **Three.js**: MIT License
- **Flask**: BSD License
- **SimpleITK**: Apache 2.0 License
- **pydicom**: MIT License

## Support & Documentation

- **README.md**: Comprehensive documentation
- **QUICKSTART.md**: 5-minute setup guide
- **API_DOCUMENTATION.md**: Complete API reference
- **PROJECT_OVERVIEW.md**: Detailed architecture
- **FILE_REFERENCE.md**: File-by-file descriptions

## Development Status

**Current Version**: 1.0.0

**Features:**
- ✅ DICOM upload and validation
- ✅ 3D Slicer integration
- ✅ STL generation
- ✅ 3D preview
- ✅ RESTful API
- ✅ Docker support
- ✅ Auto cleanup

**Future Enhancements:**
- [ ] Multi-user support with authentication
- [ ] Database for job persistence
- [ ] Advanced segmentation options
- [ ] Multiple output formats (OBJ, PLY)
- [ ] Cloud storage integration
- [ ] Batch API endpoints

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Contact & Support

- **GitHub**: Report issues and feature requests
- **Documentation**: See docs/ directory
- **Email**: [Your contact info]

---

**Disclaimer**: This software is for research and educational purposes only. Not intended for clinical diagnosis or treatment.

**Created**: 2024
**Version**: 1.0.0
**Status**: Production Ready
