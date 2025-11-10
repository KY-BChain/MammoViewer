/**
 * MammoViewer - Frontend Application
 * Handles file upload, conversion, and 3D visualization
 */

// Configuration
const API_BASE_URL = window.location.origin;
const POLL_INTERVAL = 2000; // 2 seconds

// Global state
let uploadedFiles = [];
let uploadId = null;
let jobId = null;
let stlFileName = null;
let pollInterval = null;

// Three.js variables
let scene, camera, renderer, controls, stlMesh;

// DOM Elements
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const selectedFiles = document.getElementById('selectedFiles');
const fileList = document.getElementById('fileList');
const clearFilesBtn = document.getElementById('clearFiles');
const uploadInfo = document.getElementById('uploadInfo');
const uploadDetails = document.getElementById('uploadDetails');

const parametersSection = document.getElementById('parametersSection');
const thresholdSlider = document.getElementById('thresholdSlider');
const thresholdValue = document.getElementById('thresholdValue');
const decimationSlider = document.getElementById('decimationSlider');
const decimationValue = document.getElementById('decimationValue');
const smoothingCheckbox = document.getElementById('smoothingCheckbox');
const convertBtn = document.getElementById('convertBtn');

const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const progressDetails = document.getElementById('progressDetails');

const resultsSection = document.getElementById('resultsSection');
const viewModelBtn = document.getElementById('viewModelBtn');
const downloadBtn = document.getElementById('downloadBtn');
const newConversionBtn = document.getElementById('newConversionBtn');
const resultInfo = document.getElementById('resultInfo');

const viewerSection = document.getElementById('viewerSection');
const viewer3D = document.getElementById('viewer3D');
const closeViewerBtn = document.getElementById('closeViewerBtn');
const resetCameraBtn = document.getElementById('resetCameraBtn');

const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const retryBtn = document.getElementById('retryBtn');

const aboutLink = document.getElementById('aboutLink');
const aboutModal = document.getElementById('aboutModal');
const closeModal = document.getElementById('closeModal');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    checkServerHealth();
});

function initEventListeners() {
    // File input
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // Clear files
    clearFilesBtn.addEventListener('click', clearSelectedFiles);
    
    // Parameters
    thresholdSlider.addEventListener('input', (e) => {
        thresholdValue.textContent = e.target.value;
    });
    
    decimationSlider.addEventListener('input', (e) => {
        decimationValue.textContent = e.target.value;
    });
    
    // Convert button
    convertBtn.addEventListener('click', startConversion);
    
    // Results
    viewModelBtn.addEventListener('click', showViewer);
    downloadBtn.addEventListener('click', downloadSTL);
    newConversionBtn.addEventListener('click', resetApplication);
    
    // Viewer
    closeViewerBtn.addEventListener('click', hideViewer);
    resetCameraBtn.addEventListener('click', resetCamera);
    
    // Error
    retryBtn.addEventListener('click', resetApplication);
    
    // Modal
    aboutLink.addEventListener('click', (e) => {
        e.preventDefault();
        aboutModal.style.display = 'flex';
    });
    
    closeModal.addEventListener('click', () => {
        aboutModal.style.display = 'none';
    });
    
    aboutModal.addEventListener('click', (e) => {
        if (e.target === aboutModal) {
            aboutModal.style.display = 'none';
        }
    });
}

// File handling
function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    processFiles(files);
}

function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = Array.from(event.dataTransfer.files);
    processFiles(files);
}

function processFiles(files) {
    // Filter DICOM files
    uploadedFiles = files.filter(file => {
        const ext = file.name.split('.').pop().toLowerCase();
        return ['dcm', 'dicom'].includes(ext);
    });
    
    if (uploadedFiles.length === 0) {
        showError('No valid DICOM files selected. Please upload .dcm or .dicom files.');
        return;
    }
    
    if (uploadedFiles.length > 100) {
        showError('Too many files. Maximum 100 files allowed.');
        return;
    }
    
    displaySelectedFiles();
    uploadFilesToServer();
}

function displaySelectedFiles() {
    selectedFiles.style.display = 'block';
    fileList.innerHTML = '';
    
    uploadedFiles.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        const sizeKB = (file.size / 1024).toFixed(2);
        
        fileItem.innerHTML = `
            <span class="file-item-icon">📄</span>
            <span class="file-item-name">${file.name}</span>
            <span class="file-item-size">${sizeKB} KB</span>
        `;
        
        fileList.appendChild(fileItem);
    });
}

function clearSelectedFiles() {
    uploadedFiles = [];
    uploadId = null;
    selectedFiles.style.display = 'none';
    uploadInfo.style.display = 'none';
    parametersSection.style.display = 'none';
    fileInput.value = '';
}

// API calls
async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();
        
        if (!data.slicer_available) {
            console.warn('3D Slicer not available');
        }
    } catch (error) {
        console.error('Server health check failed:', error);
    }
}

async function uploadFilesToServer() {
    try {
        const formData = new FormData();
        uploadedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        convertBtn.disabled = true;
        convertBtn.innerHTML = '<span class="spinner"></span> Uploading...';
        
        const response = await fetch(`${API_BASE_URL}/api/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }
        
        const data = await response.json();
        uploadId = data.upload_id;
        
        displayUploadInfo(data);
        parametersSection.style.display = 'block';
        convertBtn.disabled = false;
        convertBtn.innerHTML = '🔄 Convert to STL';
        
    } catch (error) {
        showError(error.message);
        convertBtn.disabled = false;
        convertBtn.innerHTML = '🔄 Convert to STL';
    }
}

function displayUploadInfo(data) {
    uploadInfo.style.display = 'block';
    
    const info = data.dicom_info || {};
    const metadata = info.metadata || {};
    
    uploadDetails.innerHTML = `
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Files Uploaded</div>
                <div class="info-value">${info.num_files || 0}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Series Found</div>
                <div class="info-value">${info.num_series || 0}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Modality</div>
                <div class="info-value">${metadata.modality || 'Unknown'}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Body Part</div>
                <div class="info-value">${metadata.body_part || 'Unknown'}</div>
            </div>
        </div>
    `;
}

async function startConversion() {
    if (!uploadId) {
        showError('Please upload DICOM files first.');
        return;
    }
    
    try {
        const params = {
            upload_id: uploadId,
            threshold: parseInt(thresholdSlider.value),
            smoothing: smoothingCheckbox.checked,
            decimation: parseFloat(decimationSlider.value) / 100
        };
        
        const response = await fetch(`${API_BASE_URL}/api/convert`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Conversion failed');
        }
        
        const data = await response.json();
        jobId = data.job_id;
        
        // Hide previous sections
        parametersSection.style.display = 'none';
        selectedFiles.style.display = 'none';
        uploadInfo.style.display = 'none';
        
        // Show progress
        progressSection.style.display = 'block';
        
        // Start polling for status
        startStatusPolling();
        
    } catch (error) {
        showError(error.message);
    }
}

function startStatusPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    
    pollInterval = setInterval(checkJobStatus, POLL_INTERVAL);
    checkJobStatus(); // Check immediately
}

async function checkJobStatus() {
    if (!jobId) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/status/${jobId}`);
        
        if (!response.ok) {
            throw new Error('Failed to check status');
        }
        
        const data = await response.json();
        
        updateProgress(data);
        
        if (data.status === 'completed') {
            clearInterval(pollInterval);
            stlFileName = data.stl_file;
            showResults();
        } else if (data.status === 'failed') {
            clearInterval(pollInterval);
            showError(data.error || 'Conversion failed');
        }
        
    } catch (error) {
        console.error('Status check error:', error);
    }
}

function updateProgress(data) {
    const progress = data.progress || 0;
    progressFill.style.width = `${progress}%`;
    progressFill.textContent = `${progress}%`;
    progressText.textContent = data.message || 'Processing...';
    
    progressDetails.textContent = `Status: ${data.status} | Job ID: ${data.job_id}`;
}

function showResults() {
    progressSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    resultInfo.innerHTML = `
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Output File</div>
                <div class="info-value">${stlFileName}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Format</div>
                <div class="info-value">STL (Binary)</div>
            </div>
        </div>
    `;
}

async function downloadSTL() {
    if (!stlFileName) return;
    
    try {
        window.location.href = `${API_BASE_URL}/api/download/${stlFileName}`;
    } catch (error) {
        showError('Failed to download file');
    }
}

function showError(message) {
    errorSection.style.display = 'block';
    errorMessage.textContent = message;
    
    // Hide other sections
    progressSection.style.display = 'none';
    resultsSection.style.display = 'none';
}

function resetApplication() {
    // Clear state
    uploadedFiles = [];
    uploadId = null;
    jobId = null;
    stlFileName = null;
    
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    
    // Reset UI
    fileInput.value = '';
    selectedFiles.style.display = 'none';
    uploadInfo.style.display = 'none';
    parametersSection.style.display = 'none';
    progressSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    viewerSection.style.display = 'none';
    
    // Reset sliders
    thresholdSlider.value = 100;
    thresholdValue.textContent = '100';
    decimationSlider.value = 75;
    decimationValue.textContent = '75';
    smoothingCheckbox.checked = true;
    
    // Scroll to top
    window.scrollTo(0, 0);
}

// 3D Viewer
function showViewer() {
    if (!stlFileName) return;
    
    viewerSection.style.display = 'block';
    resultsSection.style.display = 'none';
    
    setTimeout(() => {
        init3DViewer();
        loadSTLModel();
    }, 100);
}

function hideViewer() {
    viewerSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    if (renderer) {
        renderer.dispose();
    }
}

function init3DViewer() {
    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1e293b);
    
    // Camera
    const width = viewer3D.clientWidth;
    const height = viewer3D.clientHeight;
    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 10000);
    camera.position.set(0, 0, 500);
    
    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    viewer3D.innerHTML = '';
    viewer3D.appendChild(renderer.domElement);
    
    // Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    
    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight1.position.set(1, 1, 1);
    scene.add(directionalLight1);
    
    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.3);
    directionalLight2.position.set(-1, -1, -1);
    scene.add(directionalLight2);
    
    // Grid
    const gridHelper = new THREE.GridHelper(500, 20, 0x444444, 0x222222);
    scene.add(gridHelper);
    
    // Axes helper
    const axesHelper = new THREE.AxesHelper(100);
    scene.add(axesHelper);
    
    // Animation loop
    animate();
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
}

function loadSTLModel() {
    const loader = new THREE.STLLoader();
    
    loader.load(
        `${API_BASE_URL}/api/preview/${stlFileName}`,
        (geometry) => {
            // Remove old mesh if exists
            if (stlMesh) {
                scene.remove(stlMesh);
            }
            
            // Compute normals
            geometry.computeVertexNormals();
            
            // Center geometry
            geometry.center();
            
            // Create material
            const material = new THREE.MeshPhongMaterial({
                color: 0xff69b4,
                specular: 0x111111,
                shininess: 200,
                side: THREE.DoubleSide
            });
            
            // Create mesh
            stlMesh = new THREE.Mesh(geometry, material);
            scene.add(stlMesh);
            
            // Adjust camera to fit model
            const boundingBox = new THREE.Box3().setFromObject(stlMesh);
            const center = boundingBox.getCenter(new THREE.Vector3());
            const size = boundingBox.getSize(new THREE.Vector3());
            
            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = camera.fov * (Math.PI / 180);
            let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
            cameraZ *= 1.5; // Add some padding
            
            camera.position.set(center.x, center.y, center.z + cameraZ);
            camera.lookAt(center);
            
            controls.target.copy(center);
            controls.update();
            
            console.log('STL model loaded successfully');
        },
        (progress) => {
            console.log('Loading progress:', (progress.loaded / progress.total * 100) + '%');
        },
        (error) => {
            console.error('Error loading STL:', error);
            showError('Failed to load 3D model for preview');
        }
    );
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

function onWindowResize() {
    if (!camera || !renderer) return;
    
    const width = viewer3D.clientWidth;
    const height = viewer3D.clientHeight;
    
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    
    renderer.setSize(width, height);
}

function resetCamera() {
    if (!stlMesh) return;
    
    const boundingBox = new THREE.Box3().setFromObject(stlMesh);
    const center = boundingBox.getCenter(new THREE.Vector3());
    const size = boundingBox.getSize(new THREE.Vector3());
    
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
    cameraZ *= 1.5;
    
    camera.position.set(center.x, center.y, center.z + cameraZ);
    camera.lookAt(center);
    
    controls.target.copy(center);
    controls.update();
}