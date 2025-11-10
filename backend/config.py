"""
Configuration settings for DICOM to STL Converter
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
UPLOAD_FOLDER = BASE_DIR / 'uploads'
OUTPUT_FOLDER = BASE_DIR / 'outputs'
TEMP_FOLDER = BASE_DIR / 'temp'
LOG_FOLDER = BASE_DIR / 'logs'

# Create directories if they don't exist
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, TEMP_FOLDER, LOG_FOLDER]:
    folder.mkdir(exist_ok=True, parents=True)

# Flask Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5050))

# File Upload Configuration
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
ALLOWED_EXTENSIONS = {'dcm', 'dicom', 'DCM', 'DICOM'}
MAX_FILES_PER_UPLOAD = 100

# 3D Slicer Configuration
# IMPORTANT: Update this path to your 3D Slicer installation
SLICER_PATH = os.environ.get('SLICER_PATH', '/Applications/Slicer.app/Contents/MacOS/Slicer')
# Windows example: 'C:/Program Files/Slicer 5.4.0/Slicer.exe'
# Linux example: '/usr/local/Slicer-5.4.0-linux-amd64/Slicer'

SLICER_TIMEOUT = 300  # seconds
SLICER_SCRIPT_DIR = BASE_DIR / 'slicer_scripts'
SLICER_SCRIPT_DIR.mkdir(exist_ok=True)

# Conversion Parameters
THRESHOLD_DEFAULT = 100
THRESHOLD_MIN = 10
THRESHOLD_MAX = 1000

SMOOTHING_ITERATIONS = 15
DECIMATION_RATE = 0.75  # Reduce mesh complexity (0.0-1.0)

# Processing Configuration
ENABLE_ASYNC_PROCESSING = True
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Cleanup Configuration
AUTO_CLEANUP = True
CLEANUP_AFTER_HOURS = 24  # Delete files after 24 hours

# CORS Configuration
CORS_ORIGINS = ['http://localhost:5050', 'http://127.0.0.1:5050']

# Logging Configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"

# Database Configuration (for job tracking)
DATABASE_URL = os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR}/jobs.db')

# Processing Limits
MAX_CONCURRENT_JOBS = 3
JOB_TIMEOUT = 600  # seconds

# TCIA Integration (optional)
TCIA_API_URL = 'https://services.cancerimagingarchive.net/services/v4/TCIA/query'
TCIA_API_KEY = os.environ.get('TCIA_API_KEY', '')

# Security
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
SECURE_FILE_UPLOAD = True

# Feature Flags
ENABLE_BATCH_PROCESSING = True
ENABLE_3D_VIEWER = True
ENABLE_DOWNLOAD = True
ENABLE_PREVIEW = True

# Export Options
STL_FORMAT = 'binary'  # 'binary' or 'ascii'
STL_COORDINATE_SYSTEM = 'RAS'  # Right-Anterior-Superior

# Visualization Settings
PREVIEW_THUMBNAIL_SIZE = (400, 400)
PREVIEW_FORMAT = 'png'

# Performance
PROCESSING_THREADS = 2
MEMORY_LIMIT_MB = 2048

# Validation
VALIDATE_DICOM = True
VALIDATE_SERIES_CONSISTENCY = True
MIN_SLICES_FOR_3D = 10

# Error Messages
ERROR_MESSAGES = {
    'invalid_file': 'Invalid file format. Please upload DICOM files.',
    'file_too_large': f'File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024):.0f}MB.',
    'processing_error': 'An error occurred during processing. Please try again.',
    'slicer_not_found': '3D Slicer not found. Please check SLICER_PATH in config.',
    'insufficient_slices': f'Insufficient DICOM slices. Minimum {MIN_SLICES_FOR_3D} slices required.',
}

# Success Messages
SUCCESS_MESSAGES = {
    'upload_complete': 'Files uploaded successfully.',
    'conversion_started': 'Conversion started. Please wait...',
    'conversion_complete': 'Conversion completed successfully.',
}

def validate_config():
    """Validate critical configuration settings"""
    errors = []
    
    # Check 3D Slicer path
    slicer_path = Path(SLICER_PATH)
    if not slicer_path.exists():
        errors.append(f"3D Slicer not found at: {SLICER_PATH}")
    
    # Check write permissions
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, TEMP_FOLDER]:
        if not os.access(folder, os.W_OK):
            errors.append(f"No write permission for: {folder}")
    
    if errors:
        print("Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

if __name__ == '__main__':
    print("Configuration Check:")
    print(f"  Base Directory: {BASE_DIR}")
    print(f"  Upload Folder: {UPLOAD_FOLDER}")
    print(f"  Output Folder: {OUTPUT_FOLDER}")
    print(f"  3D Slicer Path: {SLICER_PATH}")
    print(f"\nValidation: {'✓ PASSED' if validate_config() else '✗ FAILED'}")