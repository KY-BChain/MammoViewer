"""
DICOM Processing Module
Handles DICOM file validation, reading, and preprocessing for STL conversion
"""
import os
import pydicom
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import SimpleITK as sitk
from loguru import logger
import json

class DICOMProcessor:
    """Process and validate DICOM files for conversion"""
    
    def __init__(self, dicom_dir: Path):
        """
        Initialize DICOM processor
        
        Args:
            dicom_dir: Directory containing DICOM files
        """
        self.dicom_dir = Path(dicom_dir)
        self.dicom_files = []
        self.series_data = {}
        self.metadata = {}
        
    def discover_dicom_files(self) -> List[Path]:
        """
        Discover all DICOM files in the directory
        
        Returns:
            List of DICOM file paths
        """
        logger.info(f"Discovering DICOM files in {self.dicom_dir}")
        dicom_files = []
        
        for root, dirs, files in os.walk(self.dicom_dir):
            for file in files:
                file_path = Path(root) / file
                if self.is_dicom_file(file_path):
                    dicom_files.append(file_path)
        
        self.dicom_files = dicom_files
        logger.info(f"Found {len(dicom_files)} DICOM files")
        return dicom_files
    
    @staticmethod
    def is_dicom_file(file_path: Path) -> bool:
        """
        Check if a file is a valid DICOM file
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if valid DICOM, False otherwise
        """
        try:
            pydicom.dcmread(str(file_path), stop_before_pixels=True)
            return True
        except:
            return False
    
    def organize_by_series(self) -> Dict[str, List[Path]]:
        """
        Organize DICOM files by series UID
        
        Returns:
            Dictionary mapping series UID to list of file paths
        """
        logger.info("Organizing DICOM files by series")
        series_dict = {}
        
        for file_path in self.dicom_files:
            try:
                dcm = pydicom.dcmread(str(file_path), stop_before_pixels=True)
                series_uid = getattr(dcm, 'SeriesInstanceUID', 'unknown')
                
                if series_uid not in series_dict:
                    series_dict[series_uid] = []
                
                series_dict[series_uid].append(file_path)
                
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
        
        self.series_data = series_dict
        logger.info(f"Found {len(series_dict)} series")
        return series_dict
    
    def extract_metadata(self, series_uid: Optional[str] = None) -> Dict:
        """
        Extract metadata from DICOM files
        
        Args:
            series_uid: Specific series to extract metadata from (optional)
            
        Returns:
            Dictionary containing metadata
        """
        if not self.dicom_files:
            self.discover_dicom_files()
        
        if series_uid and series_uid in self.series_data:
            files = self.series_data[series_uid]
        else:
            files = self.dicom_files
        
        if not files:
            return {}
        
        try:
            # Read first file for metadata
            dcm = pydicom.dcmread(str(files[0]))
            
            metadata = {
                'patient_id': str(getattr(dcm, 'PatientID', 'Unknown')),
                'study_date': str(getattr(dcm, 'StudyDate', 'Unknown')),
                'modality': str(getattr(dcm, 'Modality', 'Unknown')),
                'series_description': str(getattr(dcm, 'SeriesDescription', 'Unknown')),
                'manufacturer': str(getattr(dcm, 'Manufacturer', 'Unknown')),
                'number_of_slices': len(files),
                'image_type': str(getattr(dcm, 'ImageType', 'Unknown')),
                'body_part': str(getattr(dcm, 'BodyPartExamined', 'Unknown')),
            }
            
            # Add spatial information if available
            if hasattr(dcm, 'PixelSpacing'):
                metadata['pixel_spacing'] = [float(x) for x in dcm.PixelSpacing]
            
            if hasattr(dcm, 'SliceThickness'):
                metadata['slice_thickness'] = float(dcm.SliceThickness)
            
            if hasattr(dcm, 'ImagePositionPatient'):
                metadata['image_position'] = [float(x) for x in dcm.ImagePositionPatient]
            
            self.metadata = metadata
            logger.info(f"Extracted metadata: {metadata}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}
    
    def validate_series(self, series_uid: str, min_slices: int = 10) -> Tuple[bool, str]:
        """
        Validate a DICOM series for 3D reconstruction
        
        Args:
            series_uid: Series UID to validate
            min_slices: Minimum number of slices required
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if series_uid not in self.series_data:
            return False, "Series not found"
        
        files = self.series_data[series_uid]
        
        # Check minimum slices
        if len(files) < min_slices:
            return False, f"Insufficient slices: {len(files)} < {min_slices}"
        
        try:
            # Check consistency
            first_dcm = pydicom.dcmread(str(files[0]))
            
            rows = first_dcm.Rows
            cols = first_dcm.Columns
            
            for file_path in files[1:]:
                dcm = pydicom.dcmread(str(file_path))
                if dcm.Rows != rows or dcm.Columns != cols:
                    return False, "Inconsistent image dimensions"
            
            return True, "Valid series"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def load_series_as_volume(self, series_uid: str) -> Optional[sitk.Image]:
        """
        Load a DICOM series as a 3D volume using SimpleITK
        
        Args:
            series_uid: Series UID to load
            
        Returns:
            SimpleITK Image object or None if failed
        """
        if series_uid not in self.series_data:
            logger.error(f"Series {series_uid} not found")
            return None
        
        files = self.series_data[series_uid]
        
        try:
            logger.info(f"Loading {len(files)} DICOM slices...")
            
            # Sort files by instance number or slice location
            sorted_files = self._sort_dicom_files(files)
            
            # Read the series
            reader = sitk.ImageSeriesReader()
            reader.SetFileNames([str(f) for f in sorted_files])
            reader.MetaDataDictionaryArrayUpdateOn()
            reader.LoadPrivateTagsOn()
            
            image = reader.Execute()
            
            logger.info(f"Loaded volume with size: {image.GetSize()}")
            logger.info(f"Spacing: {image.GetSpacing()}")
            
            return image
            
        except Exception as e:
            logger.error(f"Error loading series: {e}")
            return None
    
    def _sort_dicom_files(self, files: List[Path]) -> List[Path]:
        """
        Sort DICOM files by instance number or image position
        
        Args:
            files: List of DICOM file paths
            
        Returns:
            Sorted list of file paths
        """
        file_info = []
        
        for file_path in files:
            try:
                dcm = pydicom.dcmread(str(file_path), stop_before_pixels=True)
                
                # Try instance number first
                if hasattr(dcm, 'InstanceNumber'):
                    sort_key = int(dcm.InstanceNumber)
                # Try slice location
                elif hasattr(dcm, 'SliceLocation'):
                    sort_key = float(dcm.SliceLocation)
                # Try image position (use Z coordinate)
                elif hasattr(dcm, 'ImagePositionPatient'):
                    sort_key = float(dcm.ImagePositionPatient[2])
                else:
                    sort_key = 0
                
                file_info.append((sort_key, file_path))
                
            except Exception as e:
                logger.warning(f"Could not get sort key for {file_path}: {e}")
                file_info.append((0, file_path))
        
        # Sort by the key
        file_info.sort(key=lambda x: x[0])
        
        return [f[1] for f in file_info]
    
    def preprocess_volume(self, image: sitk.Image, threshold: int = 100) -> sitk.Image:
        """
        Preprocess volume for STL conversion
        
        Args:
            image: SimpleITK image
            threshold: Intensity threshold for segmentation
            
        Returns:
            Preprocessed SimpleITK image
        """
        logger.info(f"Preprocessing volume with threshold: {threshold}")
        
        # Apply threshold
        binary = sitk.BinaryThreshold(image, 
                                       lowerThreshold=threshold,
                                       upperThreshold=65535,
                                       insideValue=1,
                                       outsideValue=0)
        
        # Fill holes
        logger.info("Filling holes...")
        binary = sitk.BinaryFillhole(binary)
        
        # Morphological operations to clean up
        logger.info("Applying morphological operations...")
        binary = sitk.BinaryMorphologicalClosing(binary, [3, 3, 3])
        binary = sitk.BinaryMorphologicalOpening(binary, [2, 2, 2])
        
        return binary
    
    def save_volume(self, image: sitk.Image, output_path: Path) -> bool:
        """
        Save volume as NRRD or other format
        
        Args:
            image: SimpleITK image
            output_path: Path to save the volume
            
        Returns:
            True if successful, False otherwise
        """
        try:
            sitk.WriteImage(image, str(output_path))
            logger.info(f"Saved volume to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving volume: {e}")
            return False
    
    def get_series_info(self) -> List[Dict]:
        """
        Get information about all discovered series
        
        Returns:
            List of dictionaries with series information
        """
        series_info = []
        
        for series_uid, files in self.series_data.items():
            try:
                first_dcm = pydicom.dcmread(str(files[0]), stop_before_pixels=True)
                
                info = {
                    'series_uid': series_uid,
                    'num_files': len(files),
                    'description': str(getattr(first_dcm, 'SeriesDescription', 'Unknown')),
                    'modality': str(getattr(first_dcm, 'Modality', 'Unknown')),
                    'study_date': str(getattr(first_dcm, 'StudyDate', 'Unknown')),
                }
                
                series_info.append(info)
                
            except Exception as e:
                logger.warning(f"Could not get info for series {series_uid}: {e}")
        
        return series_info
    
    def export_metadata_json(self, output_path: Path) -> bool:
        """
        Export metadata to JSON file
        
        Args:
            output_path: Path to save JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            metadata = {
                'series_info': self.get_series_info(),
                'metadata': self.metadata,
                'total_files': len(self.dicom_files),
                'total_series': len(self.series_data),
            }
            
            with open(output_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Exported metadata to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting metadata: {e}")
            return False


def process_dicom_directory(dicom_dir: Path, threshold: int = 100) -> Dict:
    """
    Main function to process a DICOM directory
    
    Args:
        dicom_dir: Directory containing DICOM files
        threshold: Intensity threshold for segmentation
        
    Returns:
        Dictionary with processing results
    """
    processor = DICOMProcessor(dicom_dir)
    
    # Discover files
    processor.discover_dicom_files()
    
    # Organize by series
    processor.organize_by_series()
    
    # Extract metadata
    metadata = processor.extract_metadata()
    
    # Get series info
    series_info = processor.get_series_info()
    
    return {
        'success': True,
        'num_files': len(processor.dicom_files),
        'num_series': len(processor.series_data),
        'metadata': metadata,
        'series_info': series_info,
    }


if __name__ == '__main__':
    # Test the processor
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python dicom_processor.py <dicom_directory>")
        sys.exit(1)
    
    dicom_dir = Path(sys.argv[1])
    
    if not dicom_dir.exists():
        print(f"Directory not found: {dicom_dir}")
        sys.exit(1)
    
    logger.info(f"Processing DICOM directory: {dicom_dir}")
    result = process_dicom_directory(dicom_dir)
    
    print("\nProcessing Results:")
    print(f"  Total Files: {result['num_files']}")
    print(f"  Total Series: {result['num_series']}")
    print(f"\nMetadata:")
    for key, value in result['metadata'].items():
        print(f"  {key}: {value}")