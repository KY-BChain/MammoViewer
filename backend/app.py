"""
MammoViewer - Flask application for DICOM to STL conversion.
"""

import os
import uuid
import shutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from loguru import logger

from backend import config
from backend.dicom_processor import DICOMProcessor
from backend.slicer_converter import SlicerConverter


# Initialize Flask app
app = Flask(__name__, static_folder='../frontend')
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE
CORS(app)

# Job storage
jobs: Dict[str, 'ConversionJob'] = {}
jobs_lock = threading.Lock()


@dataclass
class ConversionJob:
    """Represents a conversion job."""
    job_id: str
    upload_id: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    progress: int  # 0-100
    message: str
    stl_file: Optional[str] = None
    error: Optional[str] = None
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

    def update(self, status: str = None, progress: int = None,
               message: str = None, stl_file: str = None, error: str = None):
        """Update job fields."""
        if status:
            self.status = status
        if progress is not None:
            self.progress = progress
        if message:
            self.message = message
        if stl_file:
            self.stl_file = stl_file
        if error:
            self.error = error
        self.updated_at = datetime.now().isoformat()


def process_conversion_job(
    job_id: str,
    upload_dir: Path,
    output_file: Path,
    threshold: int,
    smoothing: bool,
    decimation: float
):
    """
    Background thread function to process DICOM to STL conversion.

    Args:
        job_id: Job identifier
        upload_dir: Directory containing uploaded DICOM files
        output_file: Output STL file path
        threshold: Threshold value for segmentation
        smoothing: Whether to apply smoothing
        decimation: Decimation rate
    """
    try:
        with jobs_lock:
            if job_id not in jobs:
                logger.error(f"Job {job_id} not found")
                return
            job = jobs[job_id]

        logger.info(f"Starting conversion job {job_id}")

        # Update job status
        job.update(status='processing', progress=5, message='Initializing...')

        # Initialize DICOM processor
        job.update(progress=10, message='Scanning DICOM files...')
        processor = DICOMProcessor(upload_dir)
        processor.discover_dicom_files()

        if not processor.dicom_files:
            raise ValueError("No DICOM files found in upload")

        job.update(progress=20, message=f'Found {len(processor.dicom_files)} DICOM files')

        # Organize by series
        job.update(progress=30, message='Organizing DICOM series...')
        series_dict = processor.organize_by_series()

        if not series_dict:
            raise ValueError("No valid DICOM series found")

        # Use first series
        series_uid = list(series_dict.keys())[0]
        metadata = processor.extract_metadata(series_uid)

        logger.info(f"Processing series: {series_uid}")
        logger.info(f"Series info: {metadata}")

        # Validate series
        job.update(progress=40, message='Validating DICOM series...')
        if not processor.validate_series(series_uid):
            raise ValueError("DICOM series validation failed")

        # Initialize Slicer converter
        job.update(progress=50, message='Initializing 3D Slicer converter...')
        converter = SlicerConverter()

        if not converter.validate_slicer():
            raise ValueError(
                f"3D Slicer not found at {converter.slicer_path}. "
                "Please install 3D Slicer and set SLICER_PATH environment variable."
            )

        # Progress callback
        def update_progress(progress: int, message: str):
            job.update(progress=progress, message=message)

        # Convert to STL
        job.update(progress=60, message='Converting to STL...')
        success, message = converter.convert_dicom_to_stl(
            dicom_dir=upload_dir,
            output_stl=output_file,
            threshold=threshold,
            smoothing=smoothing,
            decimation=decimation,
            progress_callback=update_progress
        )

        if not success:
            raise ValueError(f"Conversion failed: {message}")

        # Verify output file
        if not output_file.exists():
            raise ValueError("STL file was not created")

        file_size = output_file.stat().st_size
        logger.info(f"Conversion successful: {output_file} ({file_size} bytes)")

        # Update job as completed
        job.update(
            status='completed',
            progress=100,
            message=f'Conversion completed successfully ({file_size} bytes)',
            stl_file=output_file.name
        )

        logger.info(f"Job {job_id} completed successfully")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Job {job_id} failed: {error_msg}")

        with jobs_lock:
            if job_id in jobs:
                jobs[job_id].update(
                    status='failed',
                    message='Conversion failed',
                    error=error_msg
                )


def cleanup_old_files():
    """Remove old upload and output files."""
    try:
        logger.info("Running cleanup...")
        cutoff_time = datetime.now() - timedelta(hours=config.CLEANUP_AFTER_HOURS)

        for folder in [config.UPLOAD_FOLDER, config.OUTPUT_FOLDER, config.TEMP_FOLDER]:
            if not folder.exists():
                continue

            for item in folder.iterdir():
                try:
                    # Check modification time
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)

                    if mtime < cutoff_time:
                        if item.is_file():
                            item.unlink()
                            logger.debug(f"Deleted file: {item}")
                        elif item.is_dir():
                            shutil.rmtree(item)
                            logger.debug(f"Deleted directory: {item}")

                except Exception as e:
                    logger.warning(f"Error deleting {item}: {e}")

        logger.info("Cleanup completed")

    except Exception as e:
        logger.error(f"Cleanup error: {e}")


# API Routes

@app.route('/')
def index():
    """Serve the frontend."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def static_files(path):
    """Serve static files."""
    return send_from_directory(app.static_folder, path)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/upload', methods=['POST'])
def upload_files():
    """
    Upload DICOM files.

    Expects multipart/form-data with files.
    Returns: {'upload_id': str, 'file_count': int}
    """
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')

        if not files or len(files) == 0:
            return jsonify({'error': 'No files selected'}), 400

        if len(files) > config.MAX_FILES_PER_UPLOAD:
            return jsonify({
                'error': f'Too many files. Maximum {config.MAX_FILES_PER_UPLOAD} allowed'
            }), 400

        # Create upload directory
        upload_id = str(uuid.uuid4())
        upload_dir = config.UPLOAD_FOLDER / upload_id
        upload_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Upload {upload_id}: Receiving {len(files)} files")

        # Save files
        saved_count = 0
        for file in files:
            if file.filename == '':
                continue

            # Validate extension
            ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
            if ext not in config.ALLOWED_EXTENSIONS:
                logger.warning(f"Skipping invalid file: {file.filename}")
                continue

            # Save file
            filename = secure_filename(file.filename)
            file_path = upload_dir / filename
            file.save(str(file_path))
            saved_count += 1

        if saved_count == 0:
            # Clean up empty directory
            shutil.rmtree(upload_dir)
            return jsonify({'error': 'No valid DICOM files uploaded'}), 400

        logger.info(f"Upload {upload_id}: Saved {saved_count} files")

        return jsonify({
            'upload_id': upload_id,
            'file_count': saved_count,
            'message': f'Successfully uploaded {saved_count} files'
        }), 200

    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/convert', methods=['POST'])
def start_conversion():
    """
    Start DICOM to STL conversion.

    Expects JSON: {
        'upload_id': str,
        'threshold': int (optional),
        'smoothing': bool (optional),
        'decimation': float (optional)
    }
    Returns: {'job_id': str}
    """
    try:
        data = request.get_json()

        if not data or 'upload_id' not in data:
            return jsonify({'error': 'upload_id is required'}), 400

        upload_id = data['upload_id']
        upload_dir = config.UPLOAD_FOLDER / upload_id

        if not upload_dir.exists():
            return jsonify({'error': 'Upload not found'}), 404

        # Parse parameters
        threshold = int(data.get('threshold', config.THRESHOLD_DEFAULT))
        smoothing = bool(data.get('smoothing', True))
        decimation = float(data.get('decimation', config.DECIMATION_RATE))

        # Validate threshold
        if not (config.THRESHOLD_MIN <= threshold <= config.THRESHOLD_MAX):
            return jsonify({
                'error': f'Threshold must be between {config.THRESHOLD_MIN} and {config.THRESHOLD_MAX}'
            }), 400

        # Validate decimation
        if not (0.0 <= decimation <= 1.0):
            return jsonify({'error': 'Decimation must be between 0.0 and 1.0'}), 400

        # Create job
        job_id = str(uuid.uuid4())
        output_file = config.OUTPUT_FOLDER / f"{job_id}.stl"

        job = ConversionJob(
            job_id=job_id,
            upload_id=upload_id,
            status='pending',
            progress=0,
            message='Job created, waiting to start...'
        )

        with jobs_lock:
            jobs[job_id] = job

        logger.info(
            f"Created job {job_id} for upload {upload_id} "
            f"(threshold={threshold}, smoothing={smoothing}, decimation={decimation})"
        )

        # Start background thread
        thread = threading.Thread(
            target=process_conversion_job,
            args=(job_id, upload_dir, output_file, threshold, smoothing, decimation),
            daemon=True
        )
        thread.start()

        return jsonify({
            'job_id': job_id,
            'message': 'Conversion started'
        }), 200

    except Exception as e:
        logger.error(f"Conversion start error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<job_id>', methods=['GET'])
def get_job_status(job_id: str):
    """
    Get conversion job status.

    Returns: ConversionJob as JSON
    """
    with jobs_lock:
        if job_id not in jobs:
            return jsonify({'error': 'Job not found'}), 404

        job = jobs[job_id]
        return jsonify(asdict(job)), 200


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename: str):
    """
    Download STL file.

    Args:
        filename: Name of STL file to download
    """
    try:
        filename = secure_filename(filename)
        file_path = config.OUTPUT_FOLDER / filename

        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )

    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/preview/<filename>', methods=['GET'])
def preview_file(filename: str):
    """
    Preview STL file (send without forcing download).

    Args:
        filename: Name of STL file to preview
    """
    try:
        filename = secure_filename(filename)
        file_path = config.OUTPUT_FOLDER / filename

        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404

        return send_file(
            file_path,
            mimetype='application/sla'
        )

    except Exception as e:
        logger.error(f"Preview error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """
    List all conversion jobs.

    Returns: {'jobs': [ConversionJob, ...]}
    """
    with jobs_lock:
        job_list = [asdict(job) for job in jobs.values()]

    return jsonify({'jobs': job_list}), 200


@app.route('/api/cleanup', methods=['POST'])
def manual_cleanup():
    """Manually trigger cleanup of old files."""
    try:
        cleanup_old_files()
        return jsonify({'message': 'Cleanup completed'}), 200

    except Exception as e:
        logger.error(f"Manual cleanup error: {e}")
        return jsonify({'error': str(e)}), 500


# Error handlers

@app.errorhandler(400)
def bad_request(e):
    """Handle 400 errors."""
    return jsonify({'error': 'Bad request'}), 400


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(413)
def request_entity_too_large(e):
    """Handle 413 errors."""
    return jsonify({
        'error': f'File too large. Maximum size is {config.MAX_FILE_SIZE / (1024*1024):.0f}MB'
    }), 413


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    logger.error(f"Internal error: {e}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("Starting MammoViewer application")
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"Host: {config.HOST}:{config.PORT}")

    # Run cleanup on startup if enabled
    if config.AUTO_CLEANUP:
        cleanup_old_files()

    # Start Flask app
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        threaded=True
    )
