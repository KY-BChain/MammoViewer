# MammoViewer - DICOM to STL Converter

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A professional web application for converting mammography DICOM images to 3D printable STL models using 3D Slicer.

## Features

- **DICOM Upload**: Drag-and-drop interface for uploading DICOM files (up to 100 files, 500MB total)
- **Customizable Parameters**: Adjust threshold, smoothing, and decimation settings
- **Real-time Progress**: Live progress tracking during conversion
- **3D Preview**: Interactive 3D model viewer using Three.js
- **Batch Processing**: Convert multiple DICOM series
- **RESTful API**: Complete REST API for integration
- **Docker Support**: Containerized deployment with Docker
- **Auto Cleanup**: Automatic cleanup of old files

## Technology Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **SimpleITK** - Medical image processing
- **pydicom** - DICOM file handling
- **3D Slicer** - 3D reconstruction and STL export
- **VTK** - Visualization toolkit

### Frontend
- **HTML5/CSS3/JavaScript**
- **Three.js** - 3D model rendering
- **Modern responsive design**

## Prerequisites

1. **Python 3.8 or higher**
2. **3D Slicer 5.0+** - Download from [slicer.org](https://www.slicer.org/)
3. **pip** - Python package manager
4. **(Optional) Docker** - For containerized deployment

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.

## Installation

### Standard Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/MammoViewer.git
   cd MammoViewer
   ```

2. **Run the setup script**

   **Linux/macOS:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   **Windows:**
   ```batch
   setup.bat
   ```

3. **Configure 3D Slicer path**

   Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your Slicer path:
   ```
   # macOS
   SLICER_PATH=/Applications/Slicer.app/Contents/MacOS/Slicer

   # Windows
   SLICER_PATH=C:\Program Files\Slicer 5.4.0\Slicer.exe

   # Linux
   SLICER_PATH=/opt/Slicer/Slicer
   ```

4. **Activate virtual environment**
   ```bash
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

5. **Run the application**
   ```bash
   python backend/app.py
   ```

6. **Open browser**
   ```
   http://localhost:5000
   ```

### Docker Installation

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   ```
   http://localhost:5000
   ```

## Usage

### Web Interface

1. **Upload DICOM Files**
   - Drag and drop DICOM files or click to browse
   - Supports .dcm and .dicom files
   - Upload up to 100 files at once

2. **Adjust Parameters**
   - **Threshold** (10-1000): Controls tissue density threshold
   - **Smoothing**: Enable/disable surface smoothing
   - **Decimation** (0-100%): Reduce polygon count for smaller files

3. **Convert**
   - Click "Start Conversion"
   - Monitor real-time progress
   - View or download the STL file when complete

4. **3D Preview**
   - Rotate: Left mouse button + drag
   - Pan: Right mouse button + drag
   - Zoom: Mouse wheel

### API Usage

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference.

**Example: Upload and Convert**

```python
import requests

# Upload files
files = [('files', open('scan1.dcm', 'rb')), ...]
response = requests.post('http://localhost:5000/api/upload', files=files)
upload_id = response.json()['upload_id']

# Start conversion
response = requests.post('http://localhost:5000/api/convert', json={
    'upload_id': upload_id,
    'threshold': 100,
    'smoothing': True,
    'decimation': 0.75
})
job_id = response.json()['job_id']

# Check status
response = requests.get(f'http://localhost:5000/api/status/{job_id}')
status = response.json()

# Download STL
if status['status'] == 'completed':
    stl_file = requests.get(f'http://localhost:5000/api/download/{status["stl_file"]}')
    with open('output.stl', 'wb') as f:
        f.write(stl_file.content)
```

## Configuration

Edit `backend/config.py` or use environment variables:

```python
# Flask
SECRET_KEY=your-secret-key
DEBUG=False
HOST=0.0.0.0
PORT=5000

# Upload
MAX_FILE_SIZE=524288000  # 500MB
MAX_FILES_PER_UPLOAD=100

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

## Testing Data

Download public mammography datasets from:
- [The Cancer Imaging Archive (TCIA)](https://www.cancerimagingarchive.net/)
- Search for "mammography" or "breast" collections

## Project Structure

```
MammoViewer/
├── backend/                 # Backend application
│   ├── app.py              # Flask application
│   ├── config.py           # Configuration
│   ├── dicom_processor.py  # DICOM processing
│   ├── slicer_converter.py # 3D Slicer integration
│   └── requirements.txt    # Python dependencies
├── frontend/               # Frontend application
│   ├── index.html         # Main HTML
│   ├── styles.css         # Styling
│   └── app.js             # JavaScript logic
├── uploads/               # Uploaded DICOM files
├── outputs/               # Generated STL files
├── temp/                  # Temporary files
├── logs/                  # Application logs
├── slicer_scripts/        # Generated Slicer scripts
├── docker-compose.yml     # Docker orchestration
├── Dockerfile             # Docker image definition
├── setup.sh              # Linux/macOS setup script
├── setup.bat             # Windows setup script
├── test_installation.py  # Installation test
└── README.md             # This file
```

## Troubleshooting

### 3D Slicer Not Found

**Error:** `3D Slicer not found at /path/to/Slicer`

**Solution:**
1. Install 3D Slicer from [slicer.org](https://www.slicer.org/)
2. Set `SLICER_PATH` in `.env` file
3. Verify path is correct for your OS

### Conversion Fails

**Error:** `Conversion failed: No valid DICOM series found`

**Solution:**
- Ensure files are valid DICOM format
- Check that series has at least 10 slices
- Verify all slices have consistent dimensions

### Memory Issues

**Error:** `MemoryError` during conversion

**Solution:**
- Reduce number of files
- Increase decimation rate
- Add more RAM or use Docker with memory limits

### Port Already in Use

**Error:** `Address already in use: 5000`

**Solution:**
```bash
# Change port in .env
PORT=5001

# Or kill process using port 5000
lsof -ti:5000 | xargs kill -9  # Linux/macOS
```

### Linux Headless Environment

For Linux servers without display:

```bash
# Install Xvfb
sudo apt-get install xvfb

# Slicer will automatically use xvfb-run
```

## Development

### Running Tests

```bash
# Test installation
python test_installation.py

# Run backend tests
pytest backend/tests/

# Run with coverage
pytest --cov=backend
```

### Code Style

```bash
# Format code
black backend/

# Lint
pylint backend/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Third-Party Licenses

- **3D Slicer**: BSD-style license
- **Three.js**: MIT License
- **Flask**: BSD License
- **SimpleITK**: Apache 2.0 License

## Support

- **Documentation**: See [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- **API Reference**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Issues**: GitHub Issues

## Acknowledgments

- **3D Slicer** community for the powerful medical imaging platform
- **The Cancer Imaging Archive (TCIA)** for public medical imaging datasets
- **SimpleITK** developers for the medical image processing library

## Authors

MammoViewer Development Team

## Version History

- **1.0.0** (2024) - Initial release
  - DICOM to STL conversion
  - Web interface with 3D preview
  - RESTful API
  - Docker support

---

**Disclaimer**: This software is for research and educational purposes only. Not intended for clinical diagnosis or treatment. Always consult qualified medical professionals for medical imaging interpretation.
