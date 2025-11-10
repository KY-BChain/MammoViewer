# MammoViewer - Quick Start Guide

Get up and running with MammoViewer in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] 3D Slicer 5.0+ installed ([download here](https://www.slicer.org/))
- [ ] Git installed (optional)

## 5-Minute Setup

### Step 1: Get the Code (30 seconds)

```bash
# Option A: Clone with git
git clone https://github.com/yourusername/MammoViewer.git
cd MammoViewer

# Option B: Download ZIP
# Download from GitHub and extract
cd MammoViewer
```

### Step 2: Run Setup Script (2 minutes)

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```batch
setup.bat
```

The script will:
- ✓ Check Python version
- ✓ Create virtual environment
- ✓ Install dependencies
- ✓ Create necessary directories
- ✓ Detect 3D Slicer installation

### Step 3: Configure Slicer Path (30 seconds)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set your Slicer path
```

**Common Slicer Paths:**

| OS | Default Path |
|----|--------------|
| **macOS** | `/Applications/Slicer.app/Contents/MacOS/Slicer` |
| **Windows** | `C:\Program Files\Slicer 5.4.0\Slicer.exe` |
| **Linux** | `/opt/Slicer/Slicer` |

**Quick Edit (Linux/macOS):**
```bash
echo "SLICER_PATH=/Applications/Slicer.app/Contents/MacOS/Slicer" >> .env
```

**Quick Edit (Windows - PowerShell):**
```powershell
Add-Content .env "SLICER_PATH=C:\Program Files\Slicer 5.4.0\Slicer.exe"
```

### Step 4: Start the Application (10 seconds)

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Start server
python backend/app.py
```

### Step 5: Open Browser (10 seconds)

Open your browser and navigate to:
```
http://localhost:5000
```

## Test with Sample Data

### Download Free DICOM Data (2 minutes)

1. Visit [The Cancer Imaging Archive (TCIA)](https://www.cancerimagingarchive.net/)
2. Search for "CBIS-DDSM" (Curated Breast Imaging Subset of DDSM)
3. Download a small series (look for datasets < 50 MB)
4. Extract the DICOM files

### Convert Your First File (1 minute)

1. **Upload**: Drag DICOM files to the upload area
2. **Adjust**: Use default settings (threshold: 100, smoothing: on, decimation: 75%)
3. **Convert**: Click "Start Conversion"
4. **Wait**: Conversion takes 1-3 minutes depending on file size
5. **View**: Click "View 3D Model" to see your result!

## Docker Quick Start (Alternative)

If you prefer Docker:

```bash
# Build and run
docker-compose up --build

# Access application
# http://localhost:5000
```

## Verify Installation

Run the test script:

```bash
python test_installation.py
```

Expected output:
```
✓ Python version: 3.10.x
✓ All required packages installed
✓ Directories created
✓ Configuration valid
✓ 3D Slicer found
✓ All tests passed!
```

## Common Issues & Quick Fixes

### Issue: "Python not found"

**Fix:**
```bash
# macOS (install Homebrew first)
brew install python

# Ubuntu/Debian
sudo apt-get install python3 python3-pip

# Windows
# Download from python.org
```

### Issue: "3D Slicer not found"

**Fix:**
1. Download Slicer from [slicer.org](https://www.slicer.org/)
2. Install to default location
3. Update `.env` with correct path
4. Test: Run `ls /Applications/Slicer.app/Contents/MacOS/Slicer` (macOS)

### Issue: "Permission denied: setup.sh"

**Fix:**
```bash
chmod +x setup.sh
./setup.sh
```

### Issue: "Port 5000 already in use"

**Fix:**
```bash
# Option 1: Kill process on port 5000
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000   # Windows (then kill PID)

# Option 2: Use different port
# Add to .env:
echo "PORT=5001" >> .env
```

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Fix:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Issue: Linux - "Display not found"

**Fix:**
```bash
# Install virtual framebuffer
sudo apt-get install xvfb

# The application automatically uses xvfb-run on Linux
```

## Next Steps

### Learn More
- Read [README.md](README.md) for detailed documentation
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API usage
- Review [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for architecture

### Customize Settings
Edit `backend/config.py` or `.env`:
- Upload limits
- Conversion defaults
- Auto-cleanup settings
- Logging level

### Production Deployment
- Set `DEBUG=False` in `.env`
- Use a production WSGI server (gunicorn, uWSGI)
- Set up reverse proxy (nginx, Apache)
- Configure SSL/TLS
- Set strong `SECRET_KEY`

### API Integration
```python
import requests

# Your first API call
response = requests.get('http://localhost:5000/api/health')
print(response.json())
# {'status': 'healthy', 'timestamp': '...', 'version': '1.0.0'}
```

## Quick Reference Commands

### Start/Stop

```bash
# Start (development)
python backend/app.py

# Start (production with gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app

# Docker
docker-compose up -d        # Start
docker-compose stop         # Stop
docker-compose down         # Stop and remove
docker-compose logs -f      # View logs
```

### Maintenance

```bash
# View logs
tail -f logs/mammoviewer_*.log

# Clear uploads/outputs
rm -rf uploads/* outputs/*

# Update dependencies
pip install -r backend/requirements.txt --upgrade

# Check disk usage
du -sh uploads outputs temp
```

## Support

- **Quick Questions**: Check [README.md](README.md) troubleshooting section
- **API Questions**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Bug Reports**: GitHub Issues
- **Architecture**: [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

## Success!

You should now have MammoViewer running at `http://localhost:5000`

**First-time tips:**
1. Start with small DICOM datasets (< 50 files)
2. Use default parameters for first conversion
3. Watch the progress bar - conversions take 1-5 minutes
4. Try the 3D viewer with mouse controls
5. Download the STL and open in your favorite 3D viewer

**Happy converting!** 🎉
