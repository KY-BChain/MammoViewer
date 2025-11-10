# MammoViewer - DICOM to STL Converter

A complete web-based platform for converting DICOM mammography data from The Cancer Imaging Archive (TCIA) to STL 3D models using 3D Slicer.

![MammoViewer](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)

## 🌟 Features

- **📁 DICOM Upload** - Drag-and-drop or file picker interface
- **🔄 Automated Conversion** - 3D Slicer integration for DICOM→STL
- **📊 Real-time Progress** - Live status updates during processing
- **🎨 3D Visualization** - Interactive Three.js viewer with WebGL
- **⚙️ Parameter Control** - Adjustable threshold, smoothing, decimation
- **🔌 RESTful API** - Complete API for programmatic access
- **⚡ Background Processing** - Non-blocking conversions
- **🧹 Automatic Cleanup** - Scheduled file cleanup
- **🐳 Docker Support** - Containerized deployment
- **📱 Responsive Design** - Works on desktop and mobile

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **3D Slicer** - [Download](https://download.slicer.org/)

### Installation (5 minutes)
```bash
# 1. Clone repository
git clone https://github.com/KY-BChain/MammoViewer.git
cd MammoViewer

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Configure 3D Slicer path
# Edit backend/config.py and set SLICER_PATH

# 4. Start application
cd backend
python app.py

# 5. Open browser
# Navigate to http://localhost:5000
```

## 📦 Installation

### Detailed Installation Steps

#### 1. System Requirements

- **OS**: macOS, Windows, or Linux
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space
- **3D Slicer**: Version 5.0+

#### 2. Install Python Dependencies
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

#### 3. Install 3D Slicer

Download from: https://download.slicer.org/

**Installation paths:**
- **macOS**: `/Applications/Slicer.app/Contents/MacOS/Slicer`
- **Windows**: `C:\Program Files\Slicer 5.4.0\Slicer.exe`
- **Linux**: `/usr/local/Slicer-5.4.0-linux-amd64/Slicer`

#### 4. Create Required Directories
```bash
mkdir -p uploads outputs temp logs slicer_scripts
```

#### 5. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env
```

## ⚙️ Configuration

### Essential Configuration

Edit `backend/config.py`:
```python
# 3D Slicer Path (CRITICAL)
SLICER_PATH = '/Applications/Slicer.app/Contents/MacOS/Slicer'

# Server Configuration
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True

# File Upload Limits
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_FILES_PER_UPLOAD = 100

# Conversion Parameters
THRESHOLD_DEFAULT = 100
SMOOTHING_ITERATIONS = 15
DECIMATION_RATE = 0.75

# Cleanup
AUTO_CLEANUP = True
CLEANUP_AFTER_HOURS = 24
```

### Advanced Configuration

See `backend/config.py` for all available options:
- Processing limits
- Security settings
- Feature flags
- Logging configuration
- Database settings

## 📖 Usage

### Web Interface

1. **Start Server**
```bash
   cd backend
   python app.py
```

2. **Open Browser**
   - Navigate to `http://localhost:5000`

3. **Upload DICOM Files**
   - Drag-and-drop files or click "Choose DICOM Files"
   - Supports .dcm and .dicom formats

4. **Adjust Parameters**
   - **Threshold** (10-1000): Tissue density cutoff
   - **Smoothing**: Reduce surface roughness
   - **Mesh Simplification** (10-100%): File size vs quality

5. **Convert**
   - Click "Convert to STL"
   - Monitor real-time progress

6. **View & Download**
   - Interactive 3D viewer with rotation/zoom
   - Download STL file for 3D printing or analysis

### Command Line Usage
```bash
# Convert single DICOM directory
python backend/slicer_converter.py /path/to/dicom /path/to/output.stl

# With custom threshold
python backend/slicer_converter.py /path/to/dicom /path/to/output.stl 150
```

### API Usage
```python
import requests

# Upload DICOM files
files = [
    ('files', open('file1.dcm', 'rb')),
    ('files', open('file2.dcm', 'rb')),
]
response = requests.post('http://localhost:5000/api/upload', files=files)
upload_id = response.json()['upload_id']

# Start conversion
params = {
    'upload_id': upload_id,
    'threshold': 100,
    'smoothing': True,
    'decimation': 0.75
}
response = requests.post('http://localhost:5000/api/convert', json=params)
job_id = response.json()['job_id']

# Check status
response = requests.get(f'http://localhost:5000/api/status/{job_id}')
print(response.json())

# Download result
response = requests.get(f'http://localhost:5000/api/download/{stl_file}')
with open('output.stl', 'wb') as f:
    f.write(response.content)
```

## 🔌 API Documentation

### Endpoints

- `GET /api/health` - Health check
- `POST /api/upload` - Upload DICOM files
- `POST /api/convert` - Start conversion
- `GET /api/status/{job_id}` - Check job status
- `GET /api/download/{filename}` - Download STL
- `GET /api/preview/{filename}` - Preview STL
- `GET /api/jobs` - List all jobs
- `POST /api/cleanup` - Manual cleanup

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete details.

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Flask 3.0 - Web framework
- pydicom 2.4 - DICOM handling
- SimpleITK 2.3 - Image processing
- VTK 9.3 - 3D visualization
- 3D Slicer - Medical imaging platform

**Frontend:**
- HTML5/CSS3 - Structure and styling
- Vanilla JavaScript - Application logic
- Three.js r128 - 3D rendering

**Infrastructure:**
- Docker - Containerization
- Redis (optional) - Job queue

### Project Structure
```
MammoViewer/
├── backend/              # Flask application
│   ├── app.py           # Main server
│   ├── config.py        # Configuration
│   ├── dicom_processor.py
│   ├── slicer_converter.py
│   └── requirements.txt
├── frontend/            # Web interface
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── uploads/            # Temporary DICOM storage
├── outputs/            # Generated STL files
├── docs/              # Documentation
└── README.md
```

## 🐛 Troubleshooting

### Common Issues

#### 3D Slicer Not Found

**Error**: `3D Slicer not found at: /path/to/Slicer`

**Solution**:
1. Verify 3D Slicer is installed
2. Update `SLICER_PATH` in `backend/config.py`
3. On macOS, ensure path includes `.app/Contents/MacOS/Slicer`

#### Conversion Fails

**Error**: `Insufficient DICOM slices`

**Solution**:
- Ensure minimum 10 DICOM slices
- Verify DICOM files are valid
- Check all files are from same series

#### Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Change port in config.py
PORT = 5001

# Or kill process using port 5000
lsof -ti:5000 | xargs kill -9
```

#### Memory Issues

**Error**: `MemoryError` or crashes

**Solution**:
- Process smaller batches
- Increase mesh decimation (lower quality)
- Close other applications
- Increase system swap space

### Debug Mode

Enable detailed logging:
```python
# backend/config.py
DEBUG = True
LOG_LEVEL = 'DEBUG'
```

View logs:
```bash
tail -f logs/app.log
```

### Test Installation
```bash
python test_installation.py
```

## 📊 Getting DICOM Data

### From TCIA

1. Visit [The Cancer Imaging Archive](https://www.cancerimagingarchive.net/)
2. Search for mammography datasets
3. Download using NBIA Data Retriever
4. Upload to MammoViewer

### Supported Datasets

- Breast-Cancer-Screening-DBT
- CBIS-DDSM
- Any mammography DICOM data

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Access

- Web Interface: http://localhost:5000
- API: http://localhost:5000/api

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [3D Slicer](https://www.slicer.org/) - Medical imaging platform
- [The Cancer Imaging Archive](https://www.cancerimagingarchive.net/) - DICOM data source
- Open source community - All dependencies

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/KY-BChain/MammoViewer/issues)
- **Documentation**: See `/docs` folder
- **Discussions**: [GitHub Discussions](https://github.com/KY-BChain/MammoViewer/discussions)

## 🔗 Links

- **Repository**: https://github.com/KY-BChain/MammoViewer
- **3D Slicer**: https://www.slicer.org/
- **TCIA**: https://www.cancerimagingarchive.net/
- **pydicom**: https://pydicom.github.io/

## 📈 Roadmap

- [ ] User authentication
- [ ] Cloud storage integration
- [ ] Batch processing UI
- [ ] Multiple export formats (OBJ, PLY)
- [ ] AI-powered segmentation
- [ ] PACS integration

---

**Built with ❤️ for medical imaging research**