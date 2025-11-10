"""
Configuration settings for MammoViewer DICOM to STL Converter.
"""

import os
from pathlib import Path
from typing import Set
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = BASE_DIR / 'uploads'
OUTPUT_FOLDER = BASE_DIR / 'outputs'
TEMP_FOLDER = BASE_DIR / 'temp'
LOG_FOLDER = BASE_DIR / 'logs'
SLICER_SCRIPT_DIR = BASE_DIR / 'slicer_scripts'
FRONTEND_FOLDER = BASE_DIR / 'frontend'

# Flask configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# Upload configuration
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB in bytes
ALLOWED_EXTENSIONS: Set[str] = {'dcm', 'dicom', 'DCM', 'DICOM'}
MAX_FILES_PER_UPLOAD = 100

# 3D Slicer configuration
# Default paths for different platforms
if os.name == 'nt':  # Windows
    DEFAULT_SLICER_PATH = r'C:\Program Files\Slicer 5.4.0\Slicer.exe'
elif os.uname().sysname == 'Darwin':  # macOS
    DEFAULT_SLICER_PATH = '/Applications/Slicer.app/Contents/MacOS/Slicer'
else:  # Linux
    DEFAULT_SLICER_PATH = '/opt/Slicer/Slicer'

SLICER_PATH = os.getenv('SLICER_PATH', DEFAULT_SLICER_PATH)

# Conversion parameters
THRESHOLD_DEFAULT = 100
THRESHOLD_MIN = 10
THRESHOLD_MAX = 1000
SMOOTHING_ITERATIONS = 15
DECIMATION_RATE = 0.75  # 75% reduction

# Cleanup configuration
AUTO_CLEANUP = os.getenv('AUTO_CLEANUP', 'True').lower() == 'true'
CLEANUP_AFTER_HOURS = int(os.getenv('CLEANUP_AFTER_HOURS', 24))

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_ROTATION = "100 MB"
LOG_RETENTION = "1 week"


def validate_config() -> bool:
    """
    Validate the configuration settings and create necessary directories.

    Returns:
        bool: True if configuration is valid, False otherwise
    """
    try:
        # Create directories if they don't exist
        directories = [
            UPLOAD_FOLDER,
            OUTPUT_FOLDER,
            TEMP_FOLDER,
            LOG_FOLDER,
            SLICER_SCRIPT_DIR
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory verified: {directory}")

        # Validate 3D Slicer path
        slicer_path = Path(SLICER_PATH)
        if not slicer_path.exists():
            logger.warning(
                f"3D Slicer not found at {SLICER_PATH}. "
                "Please set SLICER_PATH environment variable."
            )
        else:
            logger.info(f"3D Slicer found at: {SLICER_PATH}")

        # Validate file size limit
        if MAX_FILE_SIZE <= 0:
            logger.error("MAX_FILE_SIZE must be positive")
            return False

        # Validate threshold range
        if not (THRESHOLD_MIN < THRESHOLD_DEFAULT < THRESHOLD_MAX):
            logger.error("Invalid threshold configuration")
            return False

        logger.info("Configuration validation successful")
        return True

    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False


def setup_logging() -> None:
    """Configure loguru logging."""
    log_file = LOG_FOLDER / "mammoviewer_{time}.log"

    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        lambda msg: print(msg, end=''),
        level=LOG_LEVEL,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Add file handler
    logger.add(
        log_file,
        level=LOG_LEVEL,
        rotation=LOG_ROTATION,
        retention=LOG_RETENTION,
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    logger.info("Logging configured successfully")


# Initialize logging
setup_logging()

# Validate configuration on import
if not validate_config():
    logger.warning("Configuration validation failed, but continuing...")
