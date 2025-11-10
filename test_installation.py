#!/usr/bin/env python3
"""
Test script for MammoViewer
Verifies installation and configuration
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_success(text):
    """Print success message"""
    print(f"✓ {text}")

def print_error(text):
    """Print error message"""
    print(f"✗ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠ {text}")

def test_python_version():
    """Test Python version"""
    print_header("Testing Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 8):
        print_success("Python version is compatible")
        return True
    else:
        print_error("Python 3.8 or higher is required")
        return False

def test_imports():
    """Test required imports"""
    print_header("Testing Python Dependencies")
    
    required_packages = [
        ('flask', 'Flask'),
        ('pydicom', 'pydicom'),
        ('SimpleITK', 'SimpleITK'),
        ('numpy', 'NumPy'),
        ('vtk', 'VTK'),
    ]
    
    all_ok = True
    for module, name in required_packages:
        try:
            __import__(module)
            print_success(f"{name} installed")
        except ImportError:
            print_error(f"{name} not installed")
            all_ok = False
    
    return all_ok

def test_directories():
    """Test required directories"""
    print_header("Testing Directory Structure")
    
    required_dirs = [
        'backend',
        'frontend',
        'uploads',
        'outputs',
        'temp',
        'logs',
        'slicer_scripts'
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print_success(f"{dir_name}/ exists")
        else:
            print_error(f"{dir_name}/ does not exist")
            all_ok = False
    
    return all_ok

def test_config():
    """Test configuration"""
    print_header("Testing Configuration")
    
    try:
        import config
        print_success("config.py loaded")
        
        # Check Slicer path
        slicer_path = Path(config.SLICER_PATH)
        if slicer_path.exists():
            print_success(f"3D Slicer found at: {config.SLICER_PATH}")
        else:
            print_error(f"3D Slicer not found at: {config.SLICER_PATH}")
            print("  Please update SLICER_PATH in backend/config.py")
            return False
        
        # Check other settings
        print(f"\nConfiguration:")
        print(f"  Upload folder: {config.UPLOAD_FOLDER}")
        print(f"  Output folder: {config.OUTPUT_FOLDER}")
        print(f"  Max file size: {config.MAX_FILE_SIZE / (1024*1024):.0f} MB")
        print(f"  Debug mode: {config.DEBUG}")
        print(f"  Port: {config.PORT}")
        
        return True
        
    except Exception as e:
        print_error(f"Configuration error: {e}")
        return False

def test_dicom_processor():
    """Test DICOM processor"""
    print_header("Testing DICOM Processor")
    
    try:
        from dicom_processor import DICOMProcessor
        print_success("DICOMProcessor imported")
        
        # Create test instance
        test_dir = Path('uploads')
        processor = DICOMProcessor(test_dir)
        print_success("DICOMProcessor instantiated")
        
        return True
        
    except Exception as e:
        print_error(f"DICOMProcessor error: {e}")
        return False

def test_slicer_converter():
    """Test Slicer converter"""
    print_header("Testing Slicer Converter")
    
    try:
        from slicer_converter import SlicerConverter
        print_success("SlicerConverter imported")
        
        # Create test instance
        converter = SlicerConverter()
        
        # Validate Slicer
        if converter.validate_slicer():
            print_success("3D Slicer validation passed")
            return True
        else:
            print_error("3D Slicer validation failed")
            return False
        
    except Exception as e:
        print_error(f"SlicerConverter error: {e}")
        return False

def test_flask_app():
    """Test Flask application"""
    print_header("Testing Flask Application")
    
    try:
        from app import app
        print_success("Flask app imported")
        
        # Check routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        print(f"\nAvailable routes: {len(routes)}")
        for route in sorted(routes):
            if not route.startswith('/static'):
                print(f"  {route}")
        
        return True
        
    except Exception as e:
        print_error(f"Flask app error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  MammoViewer - Installation Test  ".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    tests = [
        ("Python Version", test_python_version),
        ("Python Dependencies", test_imports),
        ("Directory Structure", test_directories),
        ("Configuration", test_config),
        ("DICOM Processor", test_dicom_processor),
        ("Slicer Converter", test_slicer_converter),
        ("Flask Application", test_flask_app),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print_error(f"Unexpected error in {name}: {e}")
            results[name] = False
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "=" * 60)
        print("🎉 All tests passed! Your installation is ready.")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Start the server: cd backend && python app.py")
        print("2. Open http://localhost:5000 in your browser")
        print("3. Upload DICOM files and convert to STL")
        return True
    else:
        print("\n" + "=" * 60)
        print("⚠ Some tests failed. Please fix the issues above.")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("1. Check README.md for installation instructions")
        print("2. Run setup.sh (Linux/Mac) or setup.bat (Windows)")
        print("3. Verify 3D Slicer is installed correctly")
        print("4. Update SLICER_PATH in backend/config.py")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)