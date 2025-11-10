# Quick Start Guide - MammoViewer

Get up and running in 5 minutes!

## ⚡ Prerequisites (2 minutes)

### 1. Install Python 3.8+
```bash
python3 --version
```
If not installed: https://www.python.org/downloads/

### 2. Install 3D Slicer
Download from: https://download.slicer.org/

**Note the installation path** - you'll need it!

## 🚀 Setup (3 minutes)

### Option A: Automated Setup (Recommended)

**macOS/Linux:**
```bash
cd MammoViewer
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
cd MammoViewer
setup.bat
```

### Option B: Manual Setup
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# 2. Install dependencies
cd backend
pip install -r requirements.txt
cd ..

# 3. Create directories
mkdir -p uploads outputs temp logs slicer_scripts

# 4. Configure Slicer path
nano backend/config.py
# Set SLICER_PATH to your Slicer installation
```

## ⚙️ Configure

Edit `backend/config.py`:
```python
# Update this line with YOUR Slicer path
SLICER_PATH = '/Applications/Slicer.app/Contents/MacOS/Slicer'  # macOS
# SLICER_PATH = 'C:/Program Files/Slicer 5.4.0/Slicer.exe'  # Windows
# SLICER_PATH = '/usr/local/Slicer-5.4.0-linux-amd64/Slicer'  # Linux
```

## ▶️ Start Application
```bash
cd backend
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

## 🌐 Use the Application

1. **Open Browser**: http://localhost:5000

2. **Upload DICOM Files**:
   - Drag-and-drop or click "Choose DICOM Files"
   - Select your DICOM mammography files

3. **Adjust Parameters** (optional):
   - Threshold: 100 (default, good for most cases)
   - Smoothing: ✓ Checked
   - Mesh Simplification: 75%

4. **Convert**:
   - Click "Convert to STL"
   - Wait 30 seconds - 2 minutes

5. **View & Download**:
   - Click "View 3D Model" for interactive viewer
   - Click "Download STL File" to save

## 📊 Get Test Data

### From TCIA

1. Visit: https://www.cancerimagingarchive.net/
2. Search: "Breast" or "Mammography"
3. Download: Use NBIA Data Retriever
4. Upload: Use the files in MammoViewer

### Sample Datasets

- **Breast-Cancer-Screening-DBT**: Digital breast tomosynthesis
- **CBIS-DDSM**: Curated breast imaging subset

## 🐛 Common Issues

### "3D Slicer not found"
→ Update `SLICER_PATH` in `backend/config.py`

### "Port 5000 already in use"
→ Change `PORT = 5001` in `backend/config.py`

### "No valid DICOM files"
→ Ensure files have `.dcm` or `.dicom` extension

### "Insufficient slices"
→ Need minimum 10 DICOM slices for 3D reconstruction

## ✅ Test Installation
```bash
python test_installation.py
```

This checks:
- ✓ Python version
- ✓ Dependencies installed
- ✓ Directories created
- ✓ 3D Slicer found
- ✓ Configuration valid

## 💡 Tips

### For Best Results

**Mammography Data:**
- Dense tissue: Threshold 150-300
- Mixed density: Threshold 100-150
- Fatty tissue: Threshold 50-100

**Performance:**
- Higher decimation = faster, smaller files
- Lower decimation = better quality, larger files

### Keyboard Shortcuts in 3D Viewer

- **Rotate**: Left click + drag
- **Pan**: Right click + drag
- **Zoom**: Scroll wheel

## 📚 Next Steps

- Read [README.md](README.md) for complete documentation
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API usage
- Review [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for architecture

## 🆘 Getting Help

1. Run `python test_installation.py`
2. Check `logs/app.log`
3. Review browser console (F12)
4. Check [GitHub Issues](https://github.com/KY-BChain/MammoViewer/issues)

---

**Ready to convert!** 🎉

**Questions?** See README.md or open an issue.