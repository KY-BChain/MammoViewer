"""
3D Slicer Converter Module
Integrates with 3D Slicer for DICOM to STL conversion
"""
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Tuple
import json
import time
from loguru import logger
import config

class SlicerConverter:
    """Convert DICOM to STL using 3D Slicer"""
    
    def __init__(self, slicer_path: str = None):
        """
        Initialize Slicer converter
        
        Args:
            slicer_path: Path to 3D Slicer executable
        """
        self.slicer_path = slicer_path or config.SLICER_PATH
        self.script_dir = config.SLICER_SCRIPT_DIR
        self.validate_slicer()
    
    def validate_slicer(self) -> bool:
        """
        Validate that 3D Slicer is installed and accessible
        
        Returns:
            True if Slicer is valid, False otherwise
        """
        slicer_path = Path(self.slicer_path)
        
        if not slicer_path.exists():
            logger.error(f"3D Slicer not found at: {self.slicer_path}")
            logger.info("Please update SLICER_PATH in config.py")
            return False
        
        logger.info(f"3D Slicer found at: {self.slicer_path}")
        return True
    
    def convert_dicom_to_stl(self,
                            dicom_dir: Path,
                            output_stl: Path,
                            threshold: int = 100,
                            smoothing: bool = True,
                            decimation: float = 0.75) -> Tuple[bool, str]:
        """
        Convert DICOM series to STL using 3D Slicer
        
        Args:
            dicom_dir: Directory containing DICOM files
            output_stl: Output STL file path
            threshold: Segmentation threshold
            smoothing: Apply smoothing to mesh
            decimation: Mesh decimation rate (0.0-1.0)
            
        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Converting DICOM to STL: {dicom_dir} -> {output_stl}")
        
        # Create conversion script
        script_path = self._create_conversion_script(
            dicom_dir=dicom_dir,
            output_stl=output_stl,
            threshold=threshold,
            smoothing=smoothing,
            decimation=decimation
        )
        
        try:
            # Run 3D Slicer with the script
            result = self._run_slicer_script(script_path)
            
            if result['success']:
                if output_stl.exists():
                    file_size = output_stl.stat().st_size / (1024 * 1024)
                    logger.info(f"STL created successfully: {file_size:.2f} MB")
                    return True, f"Conversion successful. Output size: {file_size:.2f} MB"
                else:
                    return False, "STL file was not created"
            else:
                return False, result.get('error', 'Unknown error')
                
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return False, str(e)
        finally:
            # Clean up script
            if script_path.exists():
                script_path.unlink()
    
    def _create_conversion_script(self,
                                 dicom_dir: Path,
                                 output_stl: Path,
                                 threshold: int,
                                 smoothing: bool,
                                 decimation: float) -> Path:
        """
        Create a Python script for 3D Slicer to execute
        
        Args:
            dicom_dir: DICOM directory
            output_stl: Output STL path
            threshold: Segmentation threshold
            smoothing: Enable smoothing
            decimation: Decimation rate
            
        Returns:
            Path to the created script
        """
        script_content = f'''
import slicer
import os
import json
from pathlib import Path

# Parameters
dicom_dir = r"{dicom_dir}"
output_stl = r"{output_stl}"
threshold = {threshold}
smoothing = {smoothing}
decimation = {decimation}

print(f"Starting DICOM to STL conversion...")
print(f"DICOM Directory: {{dicom_dir}}")
print(f"Output STL: {{output_stl}}")
print(f"Threshold: {{threshold}}")

try:
    # Clear the scene
    slicer.mrmlScene.Clear(0)
    
    # Import DICOM database
    print("Loading DICOM files...")
    from DICOMLib import DICOMUtils
    
    # Load DICOM files
    loadedNodeIDs = []
    
    # Get list of DICOM files
    dicom_files = []
    for root, dirs, files in os.walk(dicom_dir):
        for file in files:
            if file.lower().endswith(('.dcm', '.dicom')):
                dicom_files.append(os.path.join(root, file))
    
    print(f"Found {{len(dicom_files)}} DICOM files")
    
    if not dicom_files:
        raise Exception("No DICOM files found in directory")
    
    # Import DICOM files
    dicomBrowser = slicer.modules.DICOMWidget.browserWidget.dicomBrowser
    dicomDatabase = dicomBrowser.database()
    
    # Add files to database
    indexer = ctk.ctkDICOMIndexer()
    indexer.addDirectory(dicomDatabase, dicom_dir)
    indexer.waitForImportFinished()
    
    # Get patient UIDs
    patients = dicomDatabase.patients()
    print(f"Found {{len(patients)}} patient(s)")
    
    if not patients:
        raise Exception("No patients found in DICOM database")
    
    # Load first patient's first series
    patient = patients[0]
    studies = dicomDatabase.studiesForPatient(patient)
    
    if not studies:
        raise Exception("No studies found")
    
    study = studies[0]
    series = dicomDatabase.seriesForStudy(study)
    
    if not series:
        raise Exception("No series found")
    
    # Load the series
    print(f"Loading series...")
    seriesUID = series[0]
    loadedNodeIDs = DICOMUtils.loadSeriesByUID([seriesUID])
    
    if not loadedNodeIDs:
        raise Exception("Failed to load DICOM series")
    
    volumeNode = slicer.mrmlScene.GetNodeByID(loadedNodeIDs[0])
    print(f"Loaded volume: {{volumeNode.GetName()}}")
    
    # Create segmentation
    print("Creating segmentation...")
    segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
    segmentationNode.CreateDefaultDisplayNodes()
    segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(volumeNode)
    
    # Add segment
    segmentId = segmentationNode.GetSegmentation().AddEmptySegment("Tissue")
    
    # Set up segmentation editor
    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
    segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(segmentationNode)
    segmentEditorWidget.setSourceVolumeNode(volumeNode)
    
    # Perform thresholding
    print(f"Applying threshold: {{threshold}}")
    segmentEditorWidget.setActiveEffectByName("Threshold")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("MinimumThreshold", str(threshold))
    effect.setParameter("MaximumThreshold", "3000")
    effect.self().onApply()
    
    # Apply morphological operations to clean up
    print("Applying morphological operations...")
    segmentEditorWidget.setActiveEffectByName("Smoothing")
    effect = segmentEditorWidget.activeEffect()
    effect.setParameter("SmoothingMethod", "CLOSING")
    effect.setParameter("KernelSizeMm", "3")
    effect.self().onApply()
    
    if smoothing:
        print("Applying additional smoothing...")
        effect.setParameter("SmoothingMethod", "MEDIAN")
        effect.setParameter("KernelSizeMm", "2")
        effect.self().onApply()
    
    # Export to STL
    print("Exporting to STL...")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_stl)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Export segmentation to model
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    exportFolderItemId = shNode.CreateFolderItem(shNode.GetSceneItemID(), "Segments")
    slicer.modules.segmentations.logic().ExportAllSegmentsToModels(segmentationNode, exportFolderItemId)
    
    # Get the model node
    modelNode = None
    collection = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    collection.InitTraversal()
    for i in range(collection.GetNumberOfItems()):
        node = collection.GetNextItemAsObject()
        if node and not node.GetHideFromEditors():
            modelNode = node
            break
    
    if not modelNode:
        raise Exception("Failed to create model from segmentation")
    
    print(f"Model created: {{modelNode.GetName()}}")
    
    # Apply decimation if requested
    if decimation < 1.0:
        print(f"Applying mesh decimation: {{decimation}}")
        parameters = {{}}
        parameters["inputModel"] = modelNode.GetID()
        parameters["outputModel"] = modelNode.GetID()
        parameters["reductionFactor"] = decimation
        parameters["method"] = "FastQuadric"
        
        decimation_module = slicer.modules.decimation
        slicer.cli.runSync(decimation_module, None, parameters)
    
    # Save to STL
    print(f"Saving STL to: {{output_stl}}")
    success = slicer.util.saveNode(modelNode, output_stl)
    
    if success:
        print("SUCCESS: STL file created successfully")
        
        # Write success marker
        success_file = output_stl + ".success"
        with open(success_file, 'w') as f:
            json.dump({{"status": "success", "output": output_stl}}, f)
    else:
        raise Exception("Failed to save STL file")
    
    # Clean up
    slicer.mrmlScene.Clear(0)
    
except Exception as e:
    print(f"ERROR: {{str(e)}}")
    import traceback
    traceback.print_exc()
    
    # Write error marker
    error_file = output_stl + ".error"
    with open(error_file, 'w') as f:
        json.dump({{"status": "error", "message": str(e)}}, f)
    
    raise

print("Script completed")
'''
        
        # Save script to temporary file
        script_path = self.script_dir / f"convert_{int(time.time())}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        logger.info(f"Created Slicer script: {script_path}")
        return script_path
    
    def _run_slicer_script(self, script_path: Path, timeout: int = None) -> Dict:
        """
        Run a 3D Slicer Python script
        
        Args:
            script_path: Path to the Python script
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with execution results
        """
        timeout = timeout or config.SLICER_TIMEOUT
        
        cmd = [
            str(self.slicer_path),
            '--no-splash',
            '--no-main-window',
            '--python-script',
            str(script_path)
        ]
        
        logger.info(f"Running Slicer command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = result.stdout
            error = result.stderr
            
            logger.info(f"Slicer output:\n{output}")
            
            if result.returncode == 0 and 'SUCCESS' in output:
                return {
                    'success': True,
                    'output': output,
                    'returncode': result.returncode
                }
            else:
                logger.error(f"Slicer error:\n{error}")
                return {
                    'success': False,
                    'error': error or output,
                    'returncode': result.returncode
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"Slicer script timed out after {timeout} seconds")
            return {
                'success': False,
                'error': f"Script execution timed out after {timeout} seconds"
            }
        except Exception as e:
            logger.error(f"Error running Slicer script: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def batch_convert(self, 
                     dicom_dirs: list,
                     output_dir: Path,
                     **kwargs) -> Dict:
        """
        Batch convert multiple DICOM series to STL
        
        Args:
            dicom_dirs: List of DICOM directories
            output_dir: Output directory for STL files
            **kwargs: Additional conversion parameters
            
        Returns:
            Dictionary with batch conversion results
        """
        results = []
        output_dir.mkdir(exist_ok=True, parents=True)
        
        for i, dicom_dir in enumerate(dicom_dirs):
            logger.info(f"Processing {i+1}/{len(dicom_dirs)}: {dicom_dir}")
            
            output_stl = output_dir / f"model_{i+1}.stl"
            
            success, message = self.convert_dicom_to_stl(
                dicom_dir=Path(dicom_dir),
                output_stl=output_stl,
                **kwargs
            )
            
            results.append({
                'dicom_dir': str(dicom_dir),
                'output_stl': str(output_stl) if success else None,
                'success': success,
                'message': message
            })
        
        successful = sum(1 for r in results if r['success'])
        
        return {
            'total': len(dicom_dirs),
            'successful': successful,
            'failed': len(dicom_dirs) - successful,
            'results': results
        }


def convert_directory(dicom_dir: str, output_stl: str, threshold: int = 100) -> bool:
    """
    Convenience function to convert a DICOM directory to STL
    
    Args:
        dicom_dir: Path to DICOM directory
        output_stl: Path to output STL file
        threshold: Segmentation threshold
        
    Returns:
        True if successful, False otherwise
    """
    converter = SlicerConverter()
    success, message = converter.convert_dicom_to_stl(
        dicom_dir=Path(dicom_dir),
        output_stl=Path(output_stl),
        threshold=threshold
    )
    
    logger.info(message)
    return success


if __name__ == '__main__':
    # Test the converter
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python slicer_converter.py <dicom_directory> <output_stl>")
        sys.exit(1)
    
    dicom_dir = sys.argv[1]
    output_stl = sys.argv[2]
    threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    
    logger.info(f"Converting {dicom_dir} to {output_stl}")
    success = convert_directory(dicom_dir, output_stl, threshold)
    
    if success:
        print(f"\n✓ Conversion successful!")
        print(f"  Output: {output_stl}")
    else:
        print(f"\n✗ Conversion failed")
        sys.exit(1)