"""
DICOM file processing module for MammoViewer.
Handles DICOM file discovery, validation, and volume preparation.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pydicom
import SimpleITK as sitk
from loguru import logger


class DICOMProcessor:
    """
    Process and manage DICOM files for 3D conversion.
    """

    def __init__(self, dicom_dir: Path):
        """
        Initialize DICOM processor with a directory.

        Args:
            dicom_dir: Path to directory containing DICOM files
        """
        self.dicom_dir = Path(dicom_dir)
        self.dicom_files: List[Path] = []
        self.series_dict: Dict[str, List[Path]] = {}
        self.metadata_cache: Dict[str, Dict] = {}

        if not self.dicom_dir.exists():
            raise ValueError(f"DICOM directory does not exist: {dicom_dir}")

        logger.info(f"Initialized DICOM processor for: {dicom_dir}")

    def discover_dicom_files(self) -> List[Path]:
        """
        Walk through directory and discover all DICOM files.

        Returns:
            List of paths to DICOM files
        """
        logger.info("Discovering DICOM files...")
        self.dicom_files = []

        for file_path in self.dicom_dir.rglob('*'):
            if file_path.is_file() and self.is_dicom_file(file_path):
                self.dicom_files.append(file_path)

        logger.info(f"Found {len(self.dicom_files)} DICOM files")
        return self.dicom_files

    @staticmethod
    def is_dicom_file(path: Path) -> bool:
        """
        Check if a file is a valid DICOM file.

        Args:
            path: Path to file to check

        Returns:
            True if file is valid DICOM, False otherwise
        """
        try:
            pydicom.dcmread(str(path), stop_before_pixels=True)
            return True
        except Exception:
            return False

    def organize_by_series(self) -> Dict[str, List[Path]]:
        """
        Group DICOM files by SeriesInstanceUID.

        Returns:
            Dictionary mapping SeriesInstanceUID to list of file paths
        """
        logger.info("Organizing DICOM files by series...")
        self.series_dict = {}

        if not self.dicom_files:
            self.discover_dicom_files()

        for file_path in self.dicom_files:
            try:
                ds = pydicom.dcmread(str(file_path), stop_before_pixels=True)
                series_uid = str(ds.SeriesInstanceUID)

                if series_uid not in self.series_dict:
                    self.series_dict[series_uid] = []

                self.series_dict[series_uid].append(file_path)

            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
                continue

        logger.info(f"Found {len(self.series_dict)} unique series")
        return self.series_dict

    def extract_metadata(self, series_uid: str) -> Optional[Dict]:
        """
        Extract metadata from a DICOM series.

        Args:
            series_uid: SeriesInstanceUID to extract metadata from

        Returns:
            Dictionary containing metadata or None if error
        """
        if series_uid in self.metadata_cache:
            return self.metadata_cache[series_uid]

        if series_uid not in self.series_dict:
            logger.error(f"Series UID not found: {series_uid}")
            return None

        try:
            # Read first file to get metadata
            first_file = self.series_dict[series_uid][0]
            ds = pydicom.dcmread(str(first_file), stop_before_pixels=True)

            metadata = {
                'series_uid': series_uid,
                'patient_id': str(getattr(ds, 'PatientID', 'Unknown')),
                'patient_name': str(getattr(ds, 'PatientName', 'Unknown')),
                'study_date': str(getattr(ds, 'StudyDate', 'Unknown')),
                'study_description': str(getattr(ds, 'StudyDescription', 'Unknown')),
                'series_description': str(getattr(ds, 'SeriesDescription', 'Unknown')),
                'modality': str(getattr(ds, 'Modality', 'Unknown')),
                'manufacturer': str(getattr(ds, 'Manufacturer', 'Unknown')),
                'slice_count': len(self.series_dict[series_uid]),
                'rows': int(getattr(ds, 'Rows', 0)),
                'columns': int(getattr(ds, 'Columns', 0)),
                'pixel_spacing': list(getattr(ds, 'PixelSpacing', [1.0, 1.0])),
                'slice_thickness': float(getattr(ds, 'SliceThickness', 1.0))
            }

            self.metadata_cache[series_uid] = metadata
            logger.debug(f"Extracted metadata for series: {series_uid}")
            return metadata

        except Exception as e:
            logger.error(f"Error extracting metadata for {series_uid}: {e}")
            return None

    def validate_series(self, series_uid: str, min_slices: int = 10) -> bool:
        """
        Validate that a series is suitable for 3D conversion.

        Args:
            series_uid: SeriesInstanceUID to validate
            min_slices: Minimum number of slices required

        Returns:
            True if series is valid, False otherwise
        """
        if series_uid not in self.series_dict:
            logger.error(f"Series UID not found: {series_uid}")
            return False

        files = self.series_dict[series_uid]

        # Check minimum slice count
        if len(files) < min_slices:
            logger.warning(
                f"Series {series_uid} has only {len(files)} slices, "
                f"minimum {min_slices} required"
            )
            return False

        # Check consistency of dimensions
        try:
            first_ds = pydicom.dcmread(str(files[0]), stop_before_pixels=True)
            first_rows = first_ds.Rows
            first_cols = first_ds.Columns

            for file_path in files[1:]:
                ds = pydicom.dcmread(str(file_path), stop_before_pixels=True)
                if ds.Rows != first_rows or ds.Columns != first_cols:
                    logger.warning(
                        f"Inconsistent dimensions in series {series_uid}"
                    )
                    return False

            logger.info(f"Series {series_uid} validation successful")
            return True

        except Exception as e:
            logger.error(f"Error validating series {series_uid}: {e}")
            return False

    def load_series_as_volume(self, series_uid: str) -> Optional[sitk.Image]:
        """
        Load a DICOM series as a SimpleITK volume.

        Args:
            series_uid: SeriesInstanceUID to load

        Returns:
            SimpleITK Image or None if error
        """
        if series_uid not in self.series_dict:
            logger.error(f"Series UID not found: {series_uid}")
            return None

        try:
            # Sort files before loading
            sorted_files = self._sort_dicom_files(self.series_dict[series_uid])

            # Create reader
            reader = sitk.ImageSeriesReader()
            reader.SetFileNames([str(f) for f in sorted_files])
            reader.MetaDataDictionaryArrayUpdateOn()
            reader.LoadPrivateTagsOn()

            # Read the image
            image = reader.Execute()

            logger.info(
                f"Loaded series {series_uid}: "
                f"Size={image.GetSize()}, "
                f"Spacing={image.GetSpacing()}"
            )

            return image

        except Exception as e:
            logger.error(f"Error loading series {series_uid}: {e}")
            return None

    def _sort_dicom_files(self, files: List[Path]) -> List[Path]:
        """
        Sort DICOM files by InstanceNumber or SliceLocation.

        Args:
            files: List of DICOM file paths

        Returns:
            Sorted list of file paths
        """
        file_data = []

        for file_path in files:
            try:
                ds = pydicom.dcmread(str(file_path), stop_before_pixels=True)

                # Try InstanceNumber first
                sort_key = getattr(ds, 'InstanceNumber', None)

                # Fall back to SliceLocation if InstanceNumber not available
                if sort_key is None:
                    sort_key = getattr(ds, 'SliceLocation', 0)

                file_data.append((sort_key, file_path))

            except Exception as e:
                logger.warning(f"Error reading {file_path} for sorting: {e}")
                file_data.append((0, file_path))

        # Sort by the key
        file_data.sort(key=lambda x: x[0])

        return [f[1] for f in file_data]

    def preprocess_volume(
        self,
        image: sitk.Image,
        threshold: int = 100
    ) -> sitk.Image:
        """
        Preprocess volume with thresholding and morphological operations.

        Args:
            image: Input SimpleITK image
            threshold: Threshold value for binary segmentation

        Returns:
            Preprocessed SimpleITK image
        """
        logger.info(f"Preprocessing volume with threshold={threshold}")

        try:
            # Binary threshold
            binary = sitk.BinaryThreshold(
                image,
                lowerThreshold=threshold,
                upperThreshold=65535,
                insideValue=1,
                outsideValue=0
            )

            # Morphological closing to fill holes
            radius = 2
            binary = sitk.BinaryMorphologicalClosing(
                binary,
                [radius] * binary.GetDimension()
            )

            # Fill holes
            binary = sitk.BinaryFillhole(binary)

            logger.info("Volume preprocessing complete")
            return binary

        except Exception as e:
            logger.error(f"Error preprocessing volume: {e}")
            raise

    def save_volume(self, image: sitk.Image, path: Path) -> bool:
        """
        Save SimpleITK image to file.

        Args:
            image: SimpleITK image to save
            path: Output file path (NRRD format recommended)

        Returns:
            True if successful, False otherwise
        """
        try:
            sitk.WriteImage(image, str(path))
            logger.info(f"Saved volume to: {path}")
            return True

        except Exception as e:
            logger.error(f"Error saving volume to {path}: {e}")
            return False

    def get_series_info(self) -> List[Dict]:
        """
        Get information about all discovered series.

        Returns:
            List of dictionaries containing series information
        """
        if not self.series_dict:
            self.organize_by_series()

        series_info = []
        for series_uid in self.series_dict.keys():
            metadata = self.extract_metadata(series_uid)
            if metadata:
                series_info.append(metadata)

        return series_info

    def export_metadata_json(self, path: Path) -> bool:
        """
        Export metadata for all series to JSON file.

        Args:
            path: Output JSON file path

        Returns:
            True if successful, False otherwise
        """
        try:
            series_info = self.get_series_info()

            with open(path, 'w') as f:
                json.dump(series_info, f, indent=2, default=str)

            logger.info(f"Exported metadata to: {path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting metadata to {path}: {e}")
            return False
