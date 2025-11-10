/**
 * MammoViewer - Frontend Application Logic
 */

// Global state
const state = {
    uploadedFiles: [],
    uploadId: null,
    jobId: null,
    stlFileName: null,
    pollInterval: null,
    scene: null,
    camera: null,
    renderer: null,
    controls: null,
    model: null
};

// API base URL
const API_BASE = window.location.origin;

// DOM elements
const elements = {
    dropZone: document.getElementById('drop-zone'),
    fileInput: document.getElementById('file-input'),
    fileList: document.getElementById('file-list'),
    uploadBtn: document.getElementById('upload-btn'),

    uploadSection: document.getElementById('upload-section'),
    parametersSection: document.getElementById('parameters-section'),
    progressSection: document.getElementById('progress-section'),
    resultsSection: document.getElementById('results-section'),
    viewerSection: document.getElementById('viewer-section'),
    errorSection: document.getElementById('error-section'),

    thresholdSlider: document.getElementById('threshold-slider'),
    thresholdValue: document.getElementById('threshold-value'),
    smoothingCheckbox: document.getElementById('smoothing-checkbox'),
    decimationSlider: document.getElementById('decimation-slider'),
    decimationValue: document.getElementById('decimation-value'),
    convertBtn: document.getElementById('convert-btn'),

    progressFill: document.getElementById('progress-fill'),
    progressText: document.getElementById('progress-text'),
    progressPercent: document.getElementById('progress-percent'),

    resultMessage: document.getElementById('result-message'),
    viewBtn: document.getElementById('view-btn'),
    downloadBtn: document.getElementById('download-btn'),
    newConversionBtn: document.getElementById('new-conversion-btn'),

    viewerCanvas: document.getElementById('viewer-canvas'),
    resetCameraBtn: document.getElementById('reset-camera-btn'),
    closeViewerBtn: document.getElementById('close-viewer-btn'),

    errorMessageText: document.getElementById('error-message-text'),
    retryBtn: document.getElementById('retry-btn')
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // File input
    elements.fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    elements.dropZone.addEventListener('click', () => elements.fileInput.click());
    elements.dropZone.addEventListener('dragover', handleDragOver);
    elements.dropZone.addEventListener('dragleave', handleDragLeave);
    elements.dropZone.addEventListener('drop', handleDrop);

    // Upload button
    elements.uploadBtn.addEventListener('click', uploadFilesToServer);

    // Parameter sliders
    elements.thresholdSlider.addEventListener('input', (e) => {
        elements.thresholdValue.textContent = e.target.value;
    });

    elements.decimationSlider.addEventListener('input', (e) => {
        elements.decimationValue.textContent = e.target.value;
    });

    // Convert button
    elements.convertBtn.addEventListener('click', startConversion);

    // Result buttons
    elements.viewBtn.addEventListener('click', () => {
        showSection('viewer');
        if (!state.model) {
            loadSTLModel();
        }
    });

    elements.downloadBtn.addEventListener('click', downloadSTL);
    elements.newConversionBtn.addEventListener('click', resetApplication);

    // Viewer buttons
    elements.resetCameraBtn.addEventListener('click', resetCamera);
    elements.closeViewerBtn.addEventListener('click', () => {
        showSection('results');
    });

    // Retry button
    elements.retryBtn.addEventListener('click', resetApplication);
});

// File Handling
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    processFiles(files);
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.dropZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.dropZone.classList.remove('drag-over');

    const files = Array.from(e.dataTransfer.files);
    processFiles(files);
}

function processFiles(files) {
    // Filter DICOM files
    const dicomFiles = files.filter(file => {
        const ext = file.name.split('.').pop().toLowerCase();
        return ['dcm', 'dicom'].includes(ext);
    });

    if (dicomFiles.length === 0) {
        showError('No valid DICOM files selected. Please select .dcm or .dicom files.');
        return;
    }

    if (dicomFiles.length > 100) {
        showError('Too many files. Maximum 100 files allowed.');
        return;
    }

    state.uploadedFiles = dicomFiles;
    displayFileList();
    elements.uploadBtn.style.display = 'block';
}

function displayFileList() {
    elements.fileList.innerHTML = '';

    if (state.uploadedFiles.length === 0) {
        return;
    }

    const totalSize = state.uploadedFiles.reduce((sum, file) => sum + file.size, 0);

    // Summary
    const summary = document.createElement('div');
    summary.className = 'file-item';
    summary.innerHTML = `
        <span class="file-item-name"><strong>${state.uploadedFiles.length} files selected</strong></span>
        <span class="file-item-size">${formatFileSize(totalSize)}</span>
    `;
    elements.fileList.appendChild(summary);

    // Individual files (show first 10)
    const filesToShow = state.uploadedFiles.slice(0, 10);
    filesToShow.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <span class="file-item-name">${file.name}</span>
            <span class="file-item-size">${formatFileSize(file.size)}</span>
        `;
        elements.fileList.appendChild(fileItem);
    });

    if (state.uploadedFiles.length > 10) {
        const moreItem = document.createElement('div');
        moreItem.className = 'file-item';
        moreItem.innerHTML = `<span class="file-item-name">... and ${state.uploadedFiles.length - 10} more files</span>`;
        elements.fileList.appendChild(moreItem);
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// API Calls
async function uploadFilesToServer() {
    try {
        elements.uploadBtn.disabled = true;
        elements.uploadBtn.textContent = 'Uploading...';

        const formData = new FormData();
        state.uploadedFiles.forEach(file => {
            formData.append('files', file);
        });

        const response = await fetch(`${API_BASE}/api/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }

        const data = await response.json();
        state.uploadId = data.upload_id;

        console.log('Upload successful:', data);

        // Show parameters section
        showSection('parameters');

    } catch (error) {
        console.error('Upload error:', error);
        showError(`Upload failed: ${error.message}`);
        elements.uploadBtn.disabled = false;
        elements.uploadBtn.textContent = 'Upload Files';
    }
}

async function startConversion() {
    try {
        elements.convertBtn.disabled = true;
        elements.convertBtn.textContent = 'Starting...';

        const threshold = parseInt(elements.thresholdSlider.value);
        const smoothing = elements.smoothingCheckbox.checked;
        const decimation = parseFloat(elements.decimationSlider.value) / 100;

        const response = await fetch(`${API_BASE}/api/convert`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                upload_id: state.uploadId,
                threshold: threshold,
                smoothing: smoothing,
                decimation: decimation
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Conversion failed to start');
        }

        const data = await response.json();
        state.jobId = data.job_id;

        console.log('Conversion started:', data);

        // Show progress section and start polling
        showSection('progress');
        startStatusPolling();

    } catch (error) {
        console.error('Conversion start error:', error);
        showError(`Failed to start conversion: ${error.message}`);
        elements.convertBtn.disabled = false;
        elements.convertBtn.textContent = 'Start Conversion';
    }
}

function startStatusPolling() {
    // Clear any existing interval
    if (state.pollInterval) {
        clearInterval(state.pollInterval);
    }

    // Poll every 2 seconds
    state.pollInterval = setInterval(checkJobStatus, 2000);

    // Check immediately
    checkJobStatus();
}

async function checkJobStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status/${state.jobId}`);

        if (!response.ok) {
            throw new Error('Failed to check status');
        }

        const job = await response.json();

        updateProgress(job.progress, job.message);

        if (job.status === 'completed') {
            clearInterval(state.pollInterval);
            state.stlFileName = job.stl_file;
            showSection('results');
            elements.resultMessage.textContent = job.message;

        } else if (job.status === 'failed') {
            clearInterval(state.pollInterval);
            showError(job.error || 'Conversion failed');
        }

    } catch (error) {
        console.error('Status check error:', error);
        // Continue polling unless we've had too many errors
    }
}

function updateProgress(progress, message) {
    elements.progressFill.style.width = `${progress}%`;
    elements.progressPercent.textContent = `${progress}%`;
    elements.progressText.textContent = message;
}

async function downloadSTL() {
    try {
        window.location.href = `${API_BASE}/api/download/${state.stlFileName}`;
    } catch (error) {
        console.error('Download error:', error);
        showError('Failed to download file');
    }
}

// 3D Viewer
function init3DViewer() {
    const container = elements.viewerCanvas.parentElement;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Scene
    state.scene = new THREE.Scene();
    state.scene.background = new THREE.Color(0x0f172a);

    // Camera
    state.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    state.camera.position.set(0, 0, 100);

    // Renderer
    state.renderer = new THREE.WebGLRenderer({
        canvas: elements.viewerCanvas,
        antialias: true
    });
    state.renderer.setSize(width, height);
    state.renderer.setPixelRatio(window.devicePixelRatio);

    // Controls
    state.controls = new THREE.OrbitControls(state.camera, state.renderer.domElement);
    state.controls.enableDamping = true;
    state.controls.dampingFactor = 0.05;

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    state.scene.add(ambientLight);

    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight1.position.set(1, 1, 1);
    state.scene.add(directionalLight1);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
    directionalLight2.position.set(-1, -1, -1);
    state.scene.add(directionalLight2);

    // Handle window resize
    window.addEventListener('resize', () => {
        const width = container.clientWidth;
        const height = container.clientHeight;

        state.camera.aspect = width / height;
        state.camera.updateProjectionMatrix();
        state.renderer.setSize(width, height);
    });

    // Start animation loop
    animate();
}

function loadSTLModel() {
    if (!state.scene) {
        init3DViewer();
    }

    // Remove existing model
    if (state.model) {
        state.scene.remove(state.model);
    }

    const loader = new THREE.STLLoader();

    loader.load(
        `${API_BASE}/api/preview/${state.stlFileName}`,
        (geometry) => {
            // Center geometry
            geometry.computeBoundingBox();
            const center = new THREE.Vector3();
            geometry.boundingBox.getCenter(center);
            geometry.translate(-center.x, -center.y, -center.z);

            // Compute normals
            geometry.computeVertexNormals();

            // Create material
            const material = new THREE.MeshPhongMaterial({
                color: 0x3b82f6,
                specular: 0x111111,
                shininess: 200
            });

            // Create mesh
            state.model = new THREE.Mesh(geometry, material);
            state.scene.add(state.model);

            // Adjust camera
            const box = new THREE.Box3().setFromObject(state.model);
            const size = box.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = state.camera.fov * (Math.PI / 180);
            let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
            cameraZ *= 1.5; // Add some padding

            state.camera.position.set(cameraZ, cameraZ, cameraZ);
            state.camera.lookAt(0, 0, 0);
            state.controls.update();

            console.log('STL model loaded successfully');
        },
        (progress) => {
            console.log('Loading progress:', (progress.loaded / progress.total * 100).toFixed(2) + '%');
        },
        (error) => {
            console.error('Error loading STL:', error);
            showError('Failed to load 3D model');
        }
    );
}

function animate() {
    requestAnimationFrame(animate);

    if (state.controls) {
        state.controls.update();
    }

    if (state.renderer && state.scene && state.camera) {
        state.renderer.render(state.scene, state.camera);
    }
}

function resetCamera() {
    if (state.camera && state.model) {
        const box = new THREE.Box3().setFromObject(state.model);
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = state.camera.fov * (Math.PI / 180);
        let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
        cameraZ *= 1.5;

        state.camera.position.set(cameraZ, cameraZ, cameraZ);
        state.camera.lookAt(0, 0, 0);
        state.controls.reset();
    }
}

// UI Control
function showSection(section) {
    // Hide all sections
    elements.uploadSection.style.display = 'none';
    elements.parametersSection.style.display = 'none';
    elements.progressSection.style.display = 'none';
    elements.resultsSection.style.display = 'none';
    elements.viewerSection.style.display = 'none';
    elements.errorSection.style.display = 'none';

    // Show requested section
    switch(section) {
        case 'upload':
            elements.uploadSection.style.display = 'block';
            break;
        case 'parameters':
            elements.parametersSection.style.display = 'block';
            break;
        case 'progress':
            elements.progressSection.style.display = 'block';
            break;
        case 'results':
            elements.resultsSection.style.display = 'block';
            break;
        case 'viewer':
            elements.viewerSection.style.display = 'block';
            break;
        case 'error':
            elements.errorSection.style.display = 'block';
            break;
    }
}

function showError(message) {
    elements.errorMessageText.textContent = message;
    showSection('error');
}

function resetApplication() {
    // Clear state
    state.uploadedFiles = [];
    state.uploadId = null;
    state.jobId = null;
    state.stlFileName = null;

    if (state.pollInterval) {
        clearInterval(state.pollInterval);
    }

    // Reset UI
    elements.fileList.innerHTML = '';
    elements.uploadBtn.style.display = 'none';
    elements.uploadBtn.disabled = false;
    elements.uploadBtn.textContent = 'Upload Files';
    elements.convertBtn.disabled = false;
    elements.convertBtn.textContent = 'Start Conversion';
    elements.fileInput.value = '';

    // Reset sliders
    elements.thresholdSlider.value = 100;
    elements.thresholdValue.textContent = '100';
    elements.smoothingCheckbox.checked = true;
    elements.decimationSlider.value = 75;
    elements.decimationValue.textContent = '75';

    // Show upload section
    showSection('upload');
}
