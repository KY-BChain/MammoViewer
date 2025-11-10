"""
3D Slicer integration module for converting DICOM to STL.
"""

import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger

from backend import config


class SlicerConverter:
    """
    Handle DICOM to STL conversion using 3D Slicer.
    """

    def __init__(self, slicer_path: Optional[str] = None):
        """
        Initialize Slicer converter.

        Args:
            slicer_path: Path to 3D Slicer executable (uses config if not provided)
        """
        self.slicer_path = Path(slicer_path or config.SLICER_PATH)

        if not self.validate_slicer():
            logger.warning(
                f"3D Slicer not found at {self.slicer_path}. "
                "Conversion will fail until valid path is provided."
            )

        logger.info(f"Initialized Slicer converter with path: {self.slicer_path}")

    def validate_slicer(self) -> bool:
        """
        Check if 3D Slicer executable exists.

        Returns:
            True if Slicer exists, False otherwise
        """
        exists = self.slicer_path.exists()

        if exists:
            logger.info(f"3D Slicer validated at: {self.slicer_path}")
        else:
            logger.error(f"3D Slicer not found at: {self.slicer_path}")

        return exists

    def convert_dicom_to_stl(
        self,
        dicom_dir: Path,
        output_stl: Path,
        threshold: int = 100,
        smoothing: bool = True,
        decimation: float = 0.75,
        progress_callback: Optional[callable] = None
    ) -> Tuple[bool, str]:
        """
        Convert DICOM series to STL file using 3D Slicer.

        Args:
            dicom_dir: Directory containing DICOM files
            output_stl: Output STL file path
            threshold: Threshold value for segmentation
            smoothing: Whether to apply smoothing
            decimation: Decimation rate (0.0 to 1.0, where 0.75 = 75% reduction)
            progress_callback: Optional callback function for progress updates

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.validate_slicer():
            return False, f"3D Slicer not found at {self.slicer_path}"

        try:
            logger.info("Starting DICOM to STL conversion")
            logger.info(f"Input directory: {dicom_dir}")
            logger.info(f"Output STL: {output_stl}")
            logger.info(
                f"Parameters: threshold={threshold}, smoothing={smoothing}, "
                f"decimation={decimation}"
            )

            if progress_callback:
                progress_callback(10, "Preparing conversion script...")

            # Create conversion script
            script_path = self._create_conversion_script({
                'dicom_dir': str(dicom_dir),
                'output_stl': str(output_stl),
                'threshold': threshold,
                'smoothing': smoothing,
                'smoothing_iterations': config.SMOOTHING_ITERATIONS,
                'decimation': decimation
            })

            if progress_callback:
                progress_callback(20, "Running 3D Slicer conversion...")

            # Run Slicer script
            success, message = self._run_slicer_script(script_path, timeout=600)

            if success:
                if progress_callback:
                    progress_callback(90, "Conversion complete, finalizing...")

                # Verify output file exists
                if not output_stl.exists():
                    return False, "Conversion completed but STL file not found"

                file_size = output_stl.stat().st_size
                logger.info(f"STL file created: {output_stl} ({file_size} bytes)")

                if progress_callback:
                    progress_callback(100, "Conversion successful")

                return True, f"Successfully created STL file ({file_size} bytes)"
            else:
                return False, message

        except Exception as e:
            error_msg = f"Conversion error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _create_conversion_script(self, params: Dict) -> Path:
        """
        Create a Python script for 3D Slicer to execute.

        Args:
            params: Dictionary containing conversion parameters

        Returns:
            Path to created script file
        """
        script_content = f'''
import os
import sys
import DICOMLib
import slicer
from slicer import util

def main():
    """Main conversion function."""
    try:
        print("Starting DICOM to STL conversion...")

        # Parameters
        dicom_dir = r"{params['dicom_dir']}"
        output_stl = r"{params['output_stl']}"
        threshold = {params['threshold']}
        smoothing = {params['smoothing']}
        smoothing_iterations = {params['smoothing_iterations']}
        decimation_rate = {params['decimation']}

        print(f"DICOM directory: {{dicom_dir}}")
        print(f"Output STL: {{output_stl}}")
        print(f"Threshold: {{threshold}}")

        # Create temporary DICOM database
        dicom_database_dir = os.path.join(os.path.dirname(output_stl), "dicom_temp_db")
        os.makedirs(dicom_database_dir, exist_ok=True)

        # Initialize DICOM database
        dicom_db = slicer.dicomDatabase
        dicom_db.openDatabase(os.path.join(dicom_database_dir, "ctkDICOM.sql"))

        # Import DICOM files
        print("Importing DICOM files...")
        indexer = ctk.ctkDICOMIndexer()
        indexer.addDirectory(dicom_db, dicom_dir)
        indexer.waitForImportFinished()

        # Get patient UIDs
        patients = dicom_db.patients()
        if not patients:
            raise Exception("No DICOM data found in directory")

        print(f"Found {{len(patients)}} patient(s)")

        # Get first patient and series
        patient = patients[0]
        studies = dicom_db.studiesForPatient(patient)
        if not studies:
            raise Exception("No studies found")

        study = studies[0]
        series_list = dicom_db.seriesForStudy(study)
        if not series_list:
            raise Exception("No series found")

        series = series_list[0]
        print(f"Processing series: {{series}}")

        # Load DICOM series
        print("Loading DICOM series...")
        files = dicom_db.filesForSeries(series)
        loadable = DICOMLib.DICOMUtils.LoadSeriesWithArchetype(files, series)

        if not loadable:
            raise Exception("Failed to load DICOM series")

        # Get the loaded volume
        volume_node = slicer.util.getNode('*')
        if not volume_node:
            raise Exception("Failed to get volume node")

        print(f"Volume loaded: {{volume_node.GetName()}}")

        # Create segmentation
        print("Creating segmentation...")
        segmentation_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        segmentation_node.CreateDefaultDisplayNodes()
        segmentation_node.SetReferenceImageGeometryParameterFromVolumeNode(volume_node)

        # Add segment
        segment_id = segmentation_node.GetSegmentation().AddEmptySegment("tissue")

        # Create segment editor
        segment_editor_widget = slicer.qMRMLSegmentEditorWidget()
        segment_editor_widget.setMRMLScene(slicer.mrmlScene)
        segment_editor_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
        segment_editor_widget.setMRMLSegmentEditorNode(segment_editor_node)
        segment_editor_widget.setSegmentationNode(segmentation_node)
        segment_editor_widget.setSourceVolumeNode(volume_node)

        # Threshold segmentation
        print(f"Applying threshold: {{threshold}}")
        segment_editor_widget.setActiveEffectByName("Threshold")
        effect = segment_editor_widget.activeEffect()
        effect.setParameter("MinimumThreshold", str(threshold))
        effect.setParameter("MaximumThreshold", "3000")
        effect.self().onApply()

        # Morphological closing
        print("Applying morphological operations...")
        segment_editor_widget.setActiveEffectByName("Smoothing")
        effect = segment_editor_widget.activeEffect()
        effect.setParameter("SmoothingMethod", "MORPHOLOGICAL_CLOSING")
        effect.setParameter("KernelSizeMm", "3.0")
        effect.self().onApply()

        # Smoothing
        if smoothing:
            print(f"Applying smoothing ({{smoothing_iterations}} iterations)...")
            effect.setParameter("SmoothingMethod", "MEDIAN")
            effect.setParameter("KernelSizeMm", "3.0")
            for i in range(smoothing_iterations):
                effect.self().onApply()
                print(f"  Smoothing iteration {{i+1}}/{{smoothing_iterations}}")

        # Export to model
        print("Exporting to 3D model...")
        shell_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "shell")
        slicer.modules.segmentations.logic().ExportVisibleSegmentsToModelHierarchy(
            segmentation_node,
            shell_node
        )

        # Get the model node
        model_nodes = list(slicer.util.getNodesByClass("vtkMRMLModelNode"))
        model_node = None
        for node in model_nodes:
            if "tissue" in node.GetName().lower():
                model_node = node
                break

        if not model_node and model_nodes:
            model_node = model_nodes[-1]

        if not model_node:
            raise Exception("Failed to create model node")

        print(f"Model created: {{model_node.GetName()}}")

        # Apply decimation if requested
        if decimation_rate > 0.0:
            print(f"Applying decimation: {{decimation_rate*100}}% reduction")
            decimation_logic = slicer.vtkSlicerDecimationLogic()
            if decimation_logic:
                poly_data = model_node.GetPolyData()
                initial_points = poly_data.GetNumberOfPoints()
                print(f"  Initial points: {{initial_points}}")

                # Create decimation filter
                import vtk
                decimate = vtk.vtkQuadricDecimation()
                decimate.SetInputData(poly_data)
                decimate.SetTargetReduction(decimation_rate)
                decimate.Update()

                model_node.SetAndObservePolyData(decimate.GetOutput())
                final_points = model_node.GetPolyData().GetNumberOfPoints()
                print(f"  Final points: {{final_points}} ({{(1-final_points/initial_points)*100:.1f}}% reduction)")

        # Save STL
        print(f"Saving STL to: {{output_stl}}")
        os.makedirs(os.path.dirname(output_stl), exist_ok=True)

        success = slicer.util.saveNode(model_node, output_stl)

        if success:
            print("SUCCESS: STL file saved successfully")
            # Write success marker
            marker_file = output_stl + ".success"
            with open(marker_file, 'w') as f:
                f.write("success")
        else:
            raise Exception("Failed to save STL file")

        # Cleanup
        segment_editor_widget.setActiveEffect(None)
        slicer.mrmlScene.RemoveNode(segment_editor_node)

        print("Conversion complete!")
        return 0

    except Exception as e:
        print(f"ERROR: {{str(e)}}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        # Write error marker
        error_file = r"{params['output_stl']}" + ".error"
        with open(error_file, 'w') as f:
            f.write(str(e))
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''

        # Save script to file
        timestamp = int(time.time())
        script_path = config.SLICER_SCRIPT_DIR / f"convert_{timestamp}.py"

        with open(script_path, 'w') as f:
            f.write(script_content)

        logger.info(f"Created conversion script: {script_path}")
        return script_path

    def _run_slicer_script(
        self,
        script_path: Path,
        timeout: int = 600
    ) -> Tuple[bool, str]:
        """
        Execute a Python script in 3D Slicer.

        Args:
            script_path: Path to the Python script
            timeout: Maximum execution time in seconds

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            logger.info(f"Executing Slicer script: {script_path}")

            # Build command
            cmd = [
                str(self.slicer_path),
                '--python-script',
                str(script_path),
                '--no-splash',
                '--no-main-window'
            ]

            # Add Xvfb for headless Linux environments
            if config.os.name != 'nt' and config.os.uname().sysname == 'Linux':
                cmd = ['xvfb-run', '-a'] + cmd

            logger.debug(f"Command: {' '.join(cmd)}")

            # Run process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode

                # Log output
                if stdout:
                    logger.debug(f"Slicer stdout: {stdout}")
                if stderr:
                    logger.debug(f"Slicer stderr: {stderr}")

                # Check for success marker
                success_marker = Path(str(script_path).replace('.py', '') + '.success')
                error_marker = Path(str(script_path).replace('.py', '') + '.error')

                if return_code == 0 or "SUCCESS" in stdout:
                    logger.info("Slicer script executed successfully")
                    return True, "Conversion completed successfully"
                elif error_marker.exists():
                    with open(error_marker, 'r') as f:
                        error_msg = f.read()
                    return False, f"Slicer error: {error_msg}"
                else:
                    return False, f"Slicer script failed with code {return_code}"

            except subprocess.TimeoutExpired:
                process.kill()
                logger.error(f"Slicer script timed out after {timeout} seconds")
                return False, f"Conversion timed out after {timeout} seconds"

        except Exception as e:
            error_msg = f"Error running Slicer script: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def batch_convert(
        self,
        dicom_dirs: List[Path],
        output_dir: Path,
        **kwargs
    ) -> List[Tuple[Path, bool, str]]:
        """
        Convert multiple DICOM directories to STL files.

        Args:
            dicom_dirs: List of directories containing DICOM files
            output_dir: Output directory for STL files
            **kwargs: Additional arguments passed to convert_dicom_to_stl

        Returns:
            List of tuples (dicom_dir, success, message)
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        results = []

        for i, dicom_dir in enumerate(dicom_dirs):
            logger.info(f"Processing {i+1}/{len(dicom_dirs)}: {dicom_dir}")

            output_stl = output_dir / f"{dicom_dir.name}.stl"

            success, message = self.convert_dicom_to_stl(
                dicom_dir,
                output_stl,
                **kwargs
            )

            results.append((dicom_dir, success, message))

            if success:
                logger.info(f"  ✓ Success: {message}")
            else:
                logger.error(f"  ✗ Failed: {message}")

        # Summary
        successful = sum(1 for _, success, _ in results if success)
        logger.info(
            f"Batch conversion complete: {successful}/{len(dicom_dirs)} successful"
        )

        return results
