"""
Flask Application for MammoViewer DICOM to STL Converter
Main web server with API endpoints
"""
import os
import uuid
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from loguru import logger
import threading
import time

# Import modules
import config
from dicom_processor import DICOMProcessor, process_dicom_directory
from slicer_converter import SlicerConverter

# Configure logging
logger.add(
    config.LOG_FOLDER / "app.log",
    rotation="500 MB",
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT
)

# Initialize Flask app
app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend')

app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = config.OUTPUT_FOLDER

# Enable CORS
CORS(app, origins=config.CORS_ORIGINS)

# Job tracking
jobs = {}
jobs_lock = threading.Lock()


class ConversionJob:
    """Track conversion job status"""
    
    def __init__(self, job_id: str, upload_id: str):
        self.job_id = job_id
        self.upload_id = upload_id
        self.status = 'queued'
        self.progress = 0
        self.message = 'Job queued'
        self.stl_file = None
        self.error = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update(self, status=None, progress=None, message=None, stl_file=None, error=None):
        """Update job status"""
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
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'job_id': self.job_id,
            'upload_id': self.upload_id,
            'status': self.status,
            'progress': self.progress,
            'message': self.message,
            'stl_file': self.stl_file,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


def cleanup_old_files():
    """Clean up old uploaded and output files"""
    if not config.AUTO_CLEANUP:
        return
    
    cutoff_time = datetime.now() - timedelta(hours=config.CLEANUP_AFTER_HOURS)
    
    for folder in [config.UPLOAD_FOLDER, config.OUTPUT_FOLDER]:
        for item in folder.iterdir():
            if item.is_file() or item.is_dir():
                # Check modification time
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                if mtime < cutoff_time:
                    try:
                        if item.is_file():
                            item.unlink()
                        else:
                            shutil.rmtree(item)
                        logger.info(f"Cleaned up: {item}")
                    except Exception as e:
                        logger.error(f"Cleanup error for {item}: {e}")


def process_conversion_job(job_id: str, upload_dir: Path, params: dict):
    """
    Process DICOM to STL conversion in background
    
    Args:
        job_id: Job ID
        upload_dir: Directory containing uploaded DICOM files
        params: Conversion parameters
    """
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            return
    
    try:
        # Update job status
        job.update(status='processing', progress=10, message='Processing DICOM files...')
        
        # Process DICOM directory
        logger.info(f"Processing DICOM directory: {upload_dir}")
        processor = DICOMProcessor(upload_dir)
        processor.discover_dicom_files()
        processor.organize_by_series()
        
        if not processor.dicom_files:
            raise Exception("No valid DICOM files found")
        
        job.update(progress=30, message=f'Found {len(processor.dicom_files)} DICOM files')
        
        # Get metadata
        metadata = processor.extract_metadata()
        
        # Validate series
        if processor.series_data:
            series_uid = list(processor.series_data.keys())[0]
            valid, error_msg = processor.validate_series(series_uid, min_slices=config.MIN_SLICES_FOR_3D)
            
            if not valid:
                raise Exception(error_msg)
        
        job.update(progress=50, message='Converting to STL...')
        
        # Convert to STL
        converter = SlicerConverter()
        
        output_filename = f"{job.upload_id}.stl"
        output_path = config.OUTPUT_FOLDER / output_filename
        
        threshold = params.get('threshold', config.THRESHOLD_DEFAULT)
        smoothing = params.get('smoothing', True)
        decimation = params.get('decimation', config.DECIMATION_RATE)
        
        logger.info(f"Converting with params: threshold={threshold}, smoothing={smoothing}")
        
        success, message = converter.convert_dicom_to_stl(
            dicom_dir=upload_dir,
            output_stl=output_path,
            threshold=threshold,
            smoothing=smoothing,
            decimation=decimation
        )
        
        if success:
            job.update(
                status='completed',
                progress=100,
                message='Conversion completed successfully',
                stl_file=output_filename
            )
            logger.info(f"Job {job_id} completed successfully")
        else:
            raise Exception(message)
            
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        job.update(
            status='failed',
            progress=0,
            message='Conversion failed',
            error=str(e)
        )


# Routes

@app.route('/')
def index():
    """Serve the main page"""
    return send_file('../frontend/index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'slicer_available': Path(config.SLICER_PATH).exists()
    })


@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Upload DICOM files"""
    try:
        # Check if files are present
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'No files selected'}), 400
        
        # Validate file count
        if len(files) > config.MAX_FILES_PER_UPLOAD:
            return jsonify({'error': f'Too many files. Maximum {config.MAX_FILES_PER_UPLOAD} allowed'}), 400
        
        # Create upload directory
        upload_id = str(uuid.uuid4())
        upload_dir = config.UPLOAD_FOLDER / upload_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save files
        saved_files = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                
                # Check file extension
                if not allowed_file(filename):
                    continue
                
                filepath = upload_dir / filename
                file.save(filepath)
                saved_files.append(filename)
                logger.info(f"Saved file: {filepath}")
        
        if not saved_files:
            shutil.rmtree(upload_dir)
            return jsonify({'error': 'No valid DICOM files uploaded'}), 400
        
        # Process DICOM directory to get info
        result = process_dicom_directory(upload_dir)
        
        return jsonify({
            'success': True,
            'upload_id': upload_id,
            'message': f'Uploaded {len(saved_files)} files',
            'files': saved_files,
            'dicom_info': result
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/convert', methods=['POST'])
def convert_to_stl():
    """Start DICOM to STL conversion"""
    try:
        data = request.get_json()
        
        if not data or 'upload_id' not in data:
            return jsonify({'error': 'Missing upload_id'}), 400
        
        upload_id = data['upload_id']
        upload_dir = config.UPLOAD_FOLDER / upload_id
        
        if not upload_dir.exists():
            return jsonify({'error': 'Upload not found'}), 404
        
        # Get parameters
        params = {
            'threshold': data.get('threshold', config.THRESHOLD_DEFAULT),
            'smoothing': data.get('smoothing', True),
            'decimation': data.get('decimation', config.DECIMATION_RATE)
        }
        
        # Validate threshold
        if not config.THRESHOLD_MIN <= params['threshold'] <= config.THRESHOLD_MAX:
            return jsonify({'error': f'Threshold must be between {config.THRESHOLD_MIN} and {config.THRESHOLD_MAX}'}), 400
        
        # Create job
        job_id = str(uuid.uuid4())
        job = ConversionJob(job_id, upload_id)
        
        with jobs_lock:
            jobs[job_id] = job
        
        # Start conversion in background thread
        thread = threading.Thread(
            target=process_conversion_job,
            args=(job_id, upload_dir, params)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Conversion started'
        })
        
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get conversion job status"""
    with jobs_lock:
        job = jobs.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job.to_dict())


@app.route('/api/download/<filename>', methods=['GET'])
def download_stl(filename):
    """Download STL file"""
    try:
        filepath = config.OUTPUT_FOLDER / secure_filename(filename)
        
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/sla'
        )
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/preview/<filename>', methods=['GET'])
def preview_stl(filename):
    """Serve STL file for preview"""
    try:
        filepath = config.OUTPUT_FOLDER / secure_filename(filename)
        
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(filepath, mimetype='application/sla')
        
    except Exception as e:
        logger.error(f"Preview error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    with jobs_lock:
        job_list = [job.to_dict() for job in jobs.values()]
    
    return jsonify({
        'jobs': job_list,
        'count': len(job_list)
    })


@app.route('/api/cleanup', methods=['POST'])
def trigger_cleanup():
    """Manually trigger cleanup"""
    try:
        cleanup_old_files()
        return jsonify({
            'success': True,
            'message': 'Cleanup completed'
        })
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(413)
def file_too_large(e):
    """Handle file size exceeded"""
    return jsonify({
        'error': f'File too large. Maximum size is {config.MAX_FILE_SIZE / (1024*1024):.0f}MB'
    }), 413


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    logger.error(f"Internal error: {e}")
    return jsonify({'error': 'Internal server error'}), 500


# Background cleanup task
def schedule_cleanup():
    """Schedule periodic cleanup"""
    while True:
        time.sleep(3600)  # Run every hour
        try:
            cleanup_old_files()
        except Exception as e:
            logger.error(f"Scheduled cleanup error: {e}")


if __name__ == '__main__':
    # Validate configuration
    if not config.validate_config():
        logger.error("Configuration validation failed. Please check config.py")
        exit(1)
    
    logger.info("Starting MammoViewer DICOM to STL Converter")
    logger.info(f"Upload folder: {config.UPLOAD_FOLDER}")
    logger.info(f"Output folder: {config.OUTPUT_FOLDER}")
    logger.info(f"3D Slicer path: {config.SLICER_PATH}")
    
    # Start cleanup thread
    if config.AUTO_CLEANUP:
        cleanup_thread = threading.Thread(target=schedule_cleanup)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        logger.info("Auto-cleanup enabled")
    
    # Run Flask app
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        threaded=True
    )