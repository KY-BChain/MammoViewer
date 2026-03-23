#!/usr/bin/env python3
"""
ACR Platform - DICOM-Bayesian Integration
Extracts patient features from DICOM files and feeds into Bayesian engine

Author: ACR Development Team
Date: 2025-11-11
"""

import pydicom
from pathlib import Path
from typing import Dict, List, Optional
import re
from datetime import datetime

from acr_bayesian_engine import PatientFeatures, BayesianReasoningEngine


class DICOMBayesianIntegrator:
    """
    Integrates DICOM mammography data with Bayesian reasoning engine
    """
    
    def __init__(self):
        self.bayesian_engine = BayesianReasoningEngine()
    
    def extract_patient_from_dicom(
        self,
        dicom_file_path: str
    ) -> PatientFeatures:
        """
        Extract patient features from DICOM file
        
        Args:
            dicom_file_path: Path to DICOM file
            
        Returns:
            PatientFeatures object
        """
        dcm = pydicom.dcmread(dicom_file_path)
        
        # Extract demographics
        age = self._extract_age(dcm)
        
        # Extract clinical data from DICOM tags
        patient = PatientFeatures(age=age)
        
        # Standard DICOM tags
        patient.ethnicity = self._safe_get(dcm, 'EthnicGroup', None)
        
        # Imaging findings
        patient.mammogram_birad = self._extract_birad_category(dcm)
        
        # Try to extract biomarkers from private tags or structured reports
        biomarkers = self._extract_biomarkers_from_dicom(dcm)
        if biomarkers:
            patient.er_status = biomarkers.get('ER')
            patient.er_percentage = biomarkers.get('ER_percentage')
            patient.pr_status = biomarkers.get('PR')
            patient.pr_percentage = biomarkers.get('PR_percentage')
            patient.her2_status = biomarkers.get('HER2')
            patient.ki67_index = biomarkers.get('Ki67')
        
        # Extract tumor measurements from structured report
        measurements = self._extract_measurements_from_sr(dcm)
        if measurements:
            patient.tumor_size_mm = measurements.get('tumor_size')
        
        return patient
    
    def process_dicom_directory(
        self,
        directory_path: str
    ) -> Dict:
        """
        Process all DICOM files in directory and perform Bayesian analysis
        
        Args:
            directory_path: Path to directory containing DICOM files
            
        Returns:
            Dictionary with combined analysis results
        """
        directory = Path(directory_path)
        dicom_files = list(directory.glob('**/*.dcm'))
        
        if not dicom_files:
            dicom_files = list(directory.glob('**/*'))
            # Filter only actual DICOM files
            dicom_files = [f for f in dicom_files if self._is_dicom_file(f)]
        
        # Extract features from all files and merge
        patient = None
        for dcm_file in dicom_files:
            try:
                current = self.extract_patient_from_dicom(str(dcm_file))
                if patient is None:
                    patient = current
                else:
                    patient = self._merge_patient_features(patient, current)
            except Exception as e:
                print(f"Warning: Could not process {dcm_file}: {e}")
                continue
        
        if patient is None:
            raise ValueError("No valid DICOM files found")
        
        # Perform Bayesian analysis
        results = self.bayesian_engine.compute_full_analysis(patient)
        
        return {
            'patient_features': patient,
            'bayesian_results': results,
            'dicom_files_processed': len(dicom_files)
        }
    
    def _extract_age(self, dcm: pydicom.Dataset) -> int:
        """Extract patient age from DICOM"""
        # Try PatientAge tag
        if hasattr(dcm, 'PatientAge'):
            age_str = dcm.PatientAge
            # Parse formats like "052Y" or "52Y"
            match = re.match(r'(\d+)Y', age_str)
            if match:
                return int(match.group(1))
        
        # Calculate from birth date and study date
        if hasattr(dcm, 'PatientBirthDate') and hasattr(dcm, 'StudyDate'):
            try:
                birth = datetime.strptime(dcm.PatientBirthDate, '%Y%m%d')
                study = datetime.strptime(dcm.StudyDate, '%Y%m%d')
                age = (study - birth).days // 365
                return age
            except:
                pass
        
        # Default if cannot determine
        return 50  # Use median age as default
    
    def _extract_birad_category(self, dcm: pydicom.Dataset) -> Optional[int]:
        """Extract BI-RADS category from DICOM"""
        # Check for BI-RADS in various possible locations
        
        # Private tags (varies by vendor)
        private_tags = [
            (0x0019, 0x1008),  # Some manufacturers use this
            (0x0021, 0x1019),
        ]
        
        for tag in private_tags:
            if tag in dcm:
                value = str(dcm[tag].value)
                # Extract number from strings like "BI-RADS 4" or "BIRADS 4"
                match = re.search(r'(\d)', value)
                if match:
                    return int(match.group(1))
        
        # Check in ContentSequence if structured report
        if hasattr(dcm, 'ContentSequence'):
            for item in dcm.ContentSequence:
                if hasattr(item, 'ConceptNameCodeSequence'):
                    concept = item.ConceptNameCodeSequence[0]
                    if 'BIRAD' in str(concept).upper():
                        if hasattr(item, 'TextValue'):
                            match = re.search(r'(\d)', item.TextValue)
                            if match:
                                return int(match.group(1))
        
        return None
    
    def _extract_biomarkers_from_dicom(
        self,
        dcm: pydicom.Dataset
    ) -> Optional[Dict]:
        """
        Extract biomarker information from DICOM structured report
        """
        biomarkers = {}
        
        # This is highly dependent on how biomarkers are encoded
        # Common approaches:
        # 1. Structured Report (SR) with coded entries
        # 2. Private tags from mammography workstations
        # 3. Text annotations
        
        if hasattr(dcm, 'ContentSequence'):
            for item in dcm.ContentSequence:
                concept_name = self._get_concept_name(item)
                value = self._get_concept_value(item)
                
                if concept_name and value:
                    # Map concept names to biomarkers
                    if 'ER' in concept_name.upper() or 'ESTROGEN' in concept_name.upper():
                        biomarkers['ER'] = value
                        # Try to extract percentage
                        match = re.search(r'(\d+)%', value)
                        if match:
                            biomarkers['ER_percentage'] = float(match.group(1))
                    
                    elif 'PR' in concept_name.upper() or 'PROGESTERONE' in concept_name.upper():
                        biomarkers['PR'] = value
                        match = re.search(r'(\d+)%', value)
                        if match:
                            biomarkers['PR_percentage'] = float(match.group(1))
                    
                    elif 'HER2' in concept_name.upper():
                        biomarkers['HER2'] = value
                    
                    elif 'KI67' in concept_name.upper() or 'KI-67' in concept_name.upper():
                        match = re.search(r'(\d+\.?\d*)%?', value)
                        if match:
                            biomarkers['Ki67'] = float(match.group(1))
        
        return biomarkers if biomarkers else None
    
    def _extract_measurements_from_sr(
        self,
        dcm: pydicom.Dataset
    ) -> Optional[Dict]:
        """Extract tumor measurements from structured report"""
        measurements = {}
        
        if hasattr(dcm, 'ContentSequence'):
            for item in dcm.ContentSequence:
                concept_name = self._get_concept_name(item)
                
                if concept_name and 'SIZE' in concept_name.upper():
                    # Try to extract numeric value with units
                    if hasattr(item, 'MeasuredValueSequence'):
                        for measure in item.MeasuredValueSequence:
                            if hasattr(measure, 'NumericValue'):
                                value = float(measure.NumericValue)
                                # Convert to mm if needed
                                if hasattr(measure, 'MeasurementUnitsCodeSequence'):
                                    unit = measure.MeasurementUnitsCodeSequence[0]
                                    if hasattr(unit, 'CodeMeaning'):
                                        if 'cm' in unit.CodeMeaning.lower():
                                            value *= 10  # Convert cm to mm
                                
                                measurements['tumor_size'] = value
        
        return measurements if measurements else None
    
    def _get_concept_name(self, item: pydicom.Dataset) -> Optional[str]:
        """Extract concept name from structured report item"""
        if hasattr(item, 'ConceptNameCodeSequence'):
            concept = item.ConceptNameCodeSequence[0]
            if hasattr(concept, 'CodeMeaning'):
                return concept.CodeMeaning
        return None
    
    def _get_concept_value(self, item: pydicom.Dataset) -> Optional[str]:
        """Extract value from structured report item"""
        if hasattr(item, 'TextValue'):
            return item.TextValue
        elif hasattr(item, 'NumericValue'):
            return str(item.NumericValue)
        return None
    
    def _safe_get(self, dcm: pydicom.Dataset, tag: str, default):
        """Safely get DICOM tag value"""
        try:
            return getattr(dcm, tag, default)
        except:
            return default
    
    def _is_dicom_file(self, filepath: Path) -> bool:
        """Check if file is a valid DICOM file"""
        try:
            pydicom.dcmread(str(filepath), stop_before_pixels=True)
            return True
        except:
            return False
    
    def _merge_patient_features(
        self,
        patient1: PatientFeatures,
        patient2: PatientFeatures
    ) -> PatientFeatures:
        """Merge features from multiple DICOM files (take non-None values)"""
        merged = PatientFeatures(age=patient1.age or patient2.age)
        
        for field in PatientFeatures.__annotations__:
            val1 = getattr(patient1, field, None)
            val2 = getattr(patient2, field, None)
            # Prefer non-None value
            setattr(merged, field, val1 if val1 is not None else val2)
        
        return merged


# ============= INTEGRATION WITH EXISTING ACR DICOM PROCESSOR =============

def integrate_with_mammoviewer_processor(
    dicom_processor_output: Dict
) -> Dict:
    """
    Integrate with existing MammoViewer DICOM processor
    
    Args:
        dicom_processor_output: Output from MammoViewer's dicom_processor.py
        
    Returns:
        Combined output with Bayesian analysis
    """
    integrator = DICOMBayesianIntegrator()
    
    # Extract metadata
    metadata = dicom_processor_output.get('metadata', {})
    
    # Create patient features
    patient = PatientFeatures(
        age=metadata.get('patient_age', 50)
    )
    
    # Add any additional features from metadata
    if 'modality' in metadata and metadata['modality'] == 'MG':
        patient.mammogram_positive = True  # Assume positive if screening
    
    # Perform Bayesian analysis
    engine = BayesianReasoningEngine()
    results = engine.compute_full_analysis(patient)
    
    # Combine with existing output
    dicom_processor_output['bayesian_analysis'] = {
        'cancer_probability': results.cancer_probability,
        'subtype': results.most_likely_subtype.value if results.most_likely_subtype else None,
        'risk_level': results.estimated_risk_level.value if results.estimated_risk_level else None,
        'confidence': results.overall_confidence,
        'reasoning': results.reasoning_chain
    }
    
    return dicom_processor_output


# ============= EXAMPLE USAGE =============

if __name__ == '__main__':
    integrator = DICOMBayesianIntegrator()
    
    # Example: Process single DICOM file
    # results = integrator.extract_patient_from_dicom('path/to/mammogram.dcm')
    
    # Example: Process directory
    # results = integrator.process_dicom_directory('/path/to/dicom/directory')
    
    print("DICOM-Bayesian Integrator initialized successfully")
    print("Ready to process DICOM files with Bayesian analysis")
