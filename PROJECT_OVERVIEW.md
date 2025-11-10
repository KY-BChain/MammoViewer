# Project Overview - MammoViewer

Complete architecture and design documentation.

## Executive Summary

MammoViewer is a production-ready web application for converting DICOM mammography data to STL 3D models using 3D Slicer. Features modern web interface, RESTful API, real-time progress tracking, and interactive 3D visualization.

## System Architecture
```
┌─────────────────────────────────────────────────────────┐
│                     User Browser                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │   Upload   │  │ Parameters │  │ 3D Viewer  │        │
│  └────────────┘  └────────────┘  └────────────┘        │
└────────────────────────┬─────────────────────────────────┘
                         │ HTTP/REST API
┌────────────────────────┴─────────────────────────────────┐
│                    Flask Web Server                       │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              API Endpoints (9 routes)                │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   DICOM      │  │   Slicer     │  │   Job         │  │
│  │   Processor  │  │   Converter  │  │   Manager     │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────┴─────────────────────────────────┐
│                    3D Slicer Engine                       │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Load → Segment → Generate Mesh → Export STL        │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Flask 3.0** - Web framework
- **pydicom 2.4** - DICOM handling
- **SimpleITK 2.3** - Medical image processing
- **VTK 9.3** - 3D visualization toolkit
- **3D Slicer** - Medical imaging platform

### Frontend
- **HTML5/CSS3** - Structure and styling
- **Vanilla JavaScript** - Application logic
- **Three.js r128** - 3D rendering

### Infrastructure
- **Docker** - Containerization
- **Redis** (optional) - Job queue

## Component Details

### Backend Components

#### Flask Application (app.py)
- 9 RESTful API endpoints
- Background job processing with threading
- File upload/download handling
- Automatic cleanup scheduling
- Error handling and logging

#### DICOM Processor (dicom_processor.py)
- DICOM file discovery and validation
- Series organization by UID
- Metadata extraction
- Volume loading with SimpleITK
- Preprocessing (thresholding, morphology)

#### Slicer Converter (slicer_converter.py)
- 3D Slicer automation
- Dynamic Python script generation
- Segmentation with thresholding
- Mesh smoothing and decimation
- STL export

#### Configuration (config.py)
- Centralized settings
- Environment variable support
- Validation functions
- Feature flags

### Frontend Components

#### User Interface (index.html)
- Drag-and-drop file upload
- Parameter controls (sliders, checkboxes)
- Progress tracking with animations
- Results display
- 3D viewer integration
- Modal dialogs

#### Styling (styles.css)
- Modern gradient design
- Responsive layout
- Card-based UI
- Custom form controls
- Smooth animations

#### Application Logic (app.js)
- State management
- API integration with fetch
- Progress polling (2-second interval)
- Three.js 3D viewer setup
- STL loading and rendering
- Camera controls

## Data Flow

### Upload Flow
```
Browser File → FormData → Flask Upload → Disk Storage
    ↓
DICOM Processor → Metadata → JSON Response → UI Update
```

### Conversion Flow
```
Convert Request → Job Creation → Background Thread
    ↓
DICOM Directory → Slicer Script → 3D Slicer
    ↓
Progress Updates → Status Polling → UI Updates
    ↓
STL File → Storage → Completion → Download
```

## Processing Pipeline

1. **Upload & Validation**
   - File type checking
   - Size validation
   - DICOM format verification

2. **DICOM Processing**
   - Series organization
   - Metadata extraction
   - Consistency validation

3. **3D Slicer Conversion**
   - Script generation
   - DICOM loading
   - Segmentation
   - Mesh generation
   - STL export

4. **Delivery**
   - File storage
   - Preview generation
   - Download link

## Security Considerations

### Current Implementation
- ✅ File type validation
- ✅ Secure filename handling
- ✅ Size limits
- ✅ Input sanitization
- ✅ Temporary file cleanup

### Production Recommendations
- 🔒 Add authentication (JWT/OAuth)
- 🔒 Implement rate limiting
- 🔒 Use HTTPS/TLS
- 🔒 Add CSRF protection
- 🔒 Implement audit logging
- 🔒 Add virus scanning
- 🔒 Database for persistence

## Performance

### Current Optimizations
- Background processing
- Mesh decimation
- Efficient file handling
- Automatic cleanup

### Scaling Options
- Celery for distributed processing
- Redis job queue
- Load balancing
- CDN for static assets
- Database connection pooling

## Deployment Options

### Local Development
```bash
python backend/app.py
```

### Docker
```bash
docker-compose up
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### Cloud Platforms
- AWS Elastic Beanstalk
- Google Cloud Run
- Azure App Service
- Heroku

## Monitoring & Logging

### Logging
- **INFO**: Normal operations
- **WARNING**: Potential issues
- **ERROR**: Failed operations
- **DEBUG**: Detailed diagnostics

### Locations
- Application: `logs/app.log`
- Console: Standard output

### Metrics
- Request rate
- Conversion success rate
- Processing time
- Error rate
- Disk usage

## Extension Points

### Possible Extensions
1. **User Management** - Authentication, projects
2. **Enhanced Processing** - AI segmentation, batch UI
3. **Visualization** - Multi-view, measurements
4. **Integration** - PACS, cloud storage
5. **Export** - Multiple formats (OBJ, PLY, PDF)

## Known Limitations

1. Processing time: Large datasets take several minutes
2. Memory usage: Limited by system memory
3. Concurrent jobs: Limited to prevent overload
4. File size: Maximum 500MB per upload
5. Browser support: Requires modern browser for 3D

## License

MIT License - Open source and free to use.

---

**Built with ❤️ for medical imaging research**