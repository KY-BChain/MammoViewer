#!/usr/bin/env python3
"""
ACR Platform - OWL Ontology Reasoner with SWRL Rules
Implements semantic reasoning for breast cancer clinical decision support

Author: ACR Development Team
Date: 2025-11-11

Requires: owlready2 (pip install owlready2)
"""

from owlready2 import *
from typing import Dict, List, Tuple
import json

from acr_bayesian_engine import (
    PatientFeatures, BayesianProbabilities,
    MolecularSubtype, RiskLevel
)


class ACR_Ontology_Reasoner:
    """
    OWL/SWRL-based ontology reasoner for ACR Platform
    Integrates with Bayesian engine for clinical decision support
    """
    
    def __init__(self, ontology_file: Optional[str] = None):
        """
        Initialize ontology reasoner
        
        Args:
            ontology_file: Path to existing OWL ontology file (optional)
        """
        if ontology_file and os.path.exists(ontology_file):
            self.onto = get_ontology(f"file://{ontology_file}").load()
        else:
            # Create new ontology
            self.onto = self._create_acr_ontology()
        
        # Initialize reasoner
        self.reasoner_initialized = False
    
    def _create_acr_ontology(self):
        """Create ACR breast cancer ontology from scratch"""
        onto = get_ontology("http://acr-platform.org/ontology/breast-cancer.owl")
        
        with onto:
            # ============= CORE CLASSES =============
            
            class Patient(Thing):
                """Patient entity"""
                pass
            
            class ClinicalFinding(Thing):
                """Clinical finding or observation"""
                pass
            
            class Biomarker(ClinicalFinding):
                """Molecular biomarker"""
                pass
            
            class ImagingFinding(ClinicalFinding):
                """Radiological finding"""
                pass
            
            class TumorCharacteristic(Thing):
                """Tumor characteristic"""
                pass
            
            class MolecularSubtype(Thing):
                """Breast cancer molecular subtype"""
                pass
            
            class TreatmentRecommendation(Thing):
                """Treatment recommendation"""
                pass
            
            class RiskStratification(Thing):
                """Risk level classification"""
                pass
            
            # ============= SUBCLASSES =============
            
            # Biomarkers
            class ER_Status(Biomarker):
                pass
            
            class PR_Status(Biomarker):
                pass
            
            class HER2_Status(Biomarker):
                pass
            
            class Ki67_Index(Biomarker):
                pass
            
            # Molecular Subtypes
            class LuminalA(MolecularSubtype):
                pass
            
            class LuminalB_HER2Negative(MolecularSubtype):
                pass
            
            class LuminalB_HER2Positive(MolecularSubtype):
                pass
            
            class HER2Enriched(MolecularSubtype):
                pass
            
            class TripleNegative(MolecularSubtype):
                pass
            
            # Risk Levels
            class LowRisk(RiskStratification):
                pass
            
            class IntermediateRisk(RiskStratification):
                pass
            
            class HighRisk(RiskStratification):
                pass
            
            class VeryHighRisk(RiskStratification):
                pass
            
            # Treatments
            class HormoneTherapy(TreatmentRecommendation):
                pass
            
            class Chemotherapy(TreatmentRecommendation):
                pass
            
            class HER2TargetedTherapy(TreatmentRecommendation):
                pass
            
            # ============= OBJECT PROPERTIES =============
            
            class hasBiomarker(Patient >> Biomarker):
                """Patient has biomarker"""
                pass
            
            class hasSubtype(Patient >> MolecularSubtype):
                """Patient has molecular subtype"""
                pass
            
            class hasRiskLevel(Patient >> RiskStratification):
                """Patient has risk stratification"""
                pass
            
            class recommendsTreatment(Patient >> TreatmentRecommendation):
                """Treatment recommended for patient"""
                pass
            
            class hasImagingFinding(Patient >> ImagingFinding):
                """Patient has imaging finding"""
                pass
            
            # ============= DATA PROPERTIES =============
            
            class hasAge(Patient >> int):
                """Patient age"""
                pass
            
            class hasTumorSize(Patient >> float):
                """Tumor size in mm"""
                pass
            
            class hasER_Percentage(ER_Status >> float):
                """ER expression percentage"""
                pass
            
            class hasPR_Percentage(PR_Status >> float):
                """PR expression percentage"""
                pass
            
            class hasKi67_Value(Ki67_Index >> float):
                """Ki67 proliferation index"""
                pass
            
            class hasCancerProbability(Patient >> float):
                """Bayesian cancer probability"""
                pass
            
            class hasRecurrenceRisk(Patient >> float):
                """5-year recurrence risk"""
                pass
            
            class hasConfidenceScore(Patient >> float):
                """Analysis confidence score"""
                pass
        
        return onto
    
    def add_swrl_rules(self):
        """Add SWRL (Semantic Web Rule Language) rules for reasoning"""
        
        with self.onto:
            # ============= MOLECULAR SUBTYPE CLASSIFICATION RULES =============
            
            # Rule 1: Luminal A classification
            # ER+ AND PR+ AND HER2- AND Ki67 low
            rule1 = Imp()
            rule1.set_as_rule("""
                Patient(?p) ^ 
                hasBiomarker(?p, ?er) ^ ER_Status(?er) ^ hasER_Percentage(?er, ?er_pct) ^ greaterThan(?er_pct, 1) ^
                hasBiomarker(?p, ?pr) ^ PR_Status(?pr) ^ hasPR_Percentage(?pr, ?pr_pct) ^ greaterThan(?pr_pct, 20) ^
                hasBiomarker(?p, ?her2) ^ HER2_Status(?her2) ^ isNegative(?her2) ^
                hasBiomarker(?p, ?ki67) ^ Ki67_Index(?ki67) ^ hasKi67_Value(?ki67, ?ki67_val) ^ lessThan(?ki67_val, 14)
                -> hasSubtype(?p, LuminalA)
            """)
            
            # Rule 2: Luminal B (HER2-) classification
            # ER+ AND (PR low/negative OR Ki67 high) AND HER2-
            rule2 = Imp()
            rule2.set_as_rule("""
                Patient(?p) ^
                hasBiomarker(?p, ?er) ^ ER_Status(?er) ^ hasER_Percentage(?er, ?er_pct) ^ greaterThan(?er_pct, 1) ^
                hasBiomarker(?p, ?ki67) ^ Ki67_Index(?ki67) ^ hasKi67_Value(?ki67, ?ki67_val) ^ greaterThan(?ki67_val, 14) ^
                hasBiomarker(?p, ?her2) ^ HER2_Status(?her2) ^ isNegative(?her2)
                -> hasSubtype(?p, LuminalB_HER2Negative)
            """)
            
            # Rule 3: Luminal B (HER2+) classification
            # ER+ AND HER2+
            rule3 = Imp()
            rule3.set_as_rule("""
                Patient(?p) ^
                hasBiomarker(?p, ?er) ^ ER_Status(?er) ^ hasER_Percentage(?er, ?er_pct) ^ greaterThan(?er_pct, 1) ^
                hasBiomarker(?p, ?her2) ^ HER2_Status(?her2) ^ isPositive(?her2)
                -> hasSubtype(?p, LuminalB_HER2Positive)
            """)
            
            # Rule 4: HER2-enriched classification
            # ER- AND PR- AND HER2+
            rule4 = Imp()
            rule4.set_as_rule("""
                Patient(?p) ^
                hasBiomarker(?p, ?er) ^ ER_Status(?er) ^ isNegative(?er) ^
                hasBiomarker(?p, ?pr) ^ PR_Status(?pr) ^ isNegative(?pr) ^
                hasBiomarker(?p, ?her2) ^ HER2_Status(?her2) ^ isPositive(?her2)
                -> hasSubtype(?p, HER2Enriched)
            """)
            
            # Rule 5: Triple Negative classification
            # ER- AND PR- AND HER2-
            rule5 = Imp()
            rule5.set_as_rule("""
                Patient(?p) ^
                hasBiomarker(?p, ?er) ^ ER_Status(?er) ^ isNegative(?er) ^
                hasBiomarker(?p, ?pr) ^ PR_Status(?pr) ^ isNegative(?pr) ^
                hasBiomarker(?p, ?her2) ^ HER2_Status(?her2) ^ isNegative(?her2)
                -> hasSubtype(?p, TripleNegative)
            """)
            
            # ============= TREATMENT RECOMMENDATION RULES =============
            
            # Rule 6: Hormone therapy for ER+
            rule6 = Imp()
            rule6.set_as_rule("""
                Patient(?p) ^
                hasBiomarker(?p, ?er) ^ ER_Status(?er) ^ isPositive(?er)
                -> recommendsTreatment(?p, HormoneTherapy)
            """)
            
            # Rule 7: HER2-targeted therapy for HER2+
            rule7 = Imp()
            rule7.set_as_rule("""
                Patient(?p) ^
                hasBiomarker(?p, ?her2) ^ HER2_Status(?her2) ^ isPositive(?her2)
                -> recommendsTreatment(?p, HER2TargetedTherapy)
            """)
            
            # Rule 8: Chemotherapy for high-grade or large tumors
            rule8 = Imp()
            rule8.set_as_rule("""
                Patient(?p) ^
                hasTumorSize(?p, ?size) ^ greaterThan(?size, 20)
                -> recommendsTreatment(?p, Chemotherapy)
            """)
            
            # Rule 9: Chemotherapy for triple negative
            rule9 = Imp()
            rule9.set_as_rule("""
                Patient(?p) ^
                hasSubtype(?p, TripleNegative)
                -> recommendsTreatment(?p, Chemotherapy)
            """)
            
            # ============= RISK STRATIFICATION RULES =============
            
            # Rule 10: High risk if large tumor + node positive
            rule10 = Imp()
            rule10.set_as_rule("""
                Patient(?p) ^
                hasTumorSize(?p, ?size) ^ greaterThan(?size, 50) ^
                hasLymphNodeInvolvement(?p, true)
                -> hasRiskLevel(?p, HighRisk)
            """)
            
            # Rule 11: High risk if triple negative
            rule11 = Imp()
            rule11.set_as_rule("""
                Patient(?p) ^
                hasSubtype(?p, TripleNegative) ^
                hasTumorSize(?p, ?size) ^ greaterThan(?size, 20)
                -> hasRiskLevel(?p, HighRisk)
            """)
            
            # Rule 12: Low risk if Luminal A + small tumor + node negative
            rule12 = Imp()
            rule12.set_as_rule("""
                Patient(?p) ^
                hasSubtype(?p, LuminalA) ^
                hasTumorSize(?p, ?size) ^ lessThan(?size, 20) ^
                hasLymphNodeInvolvement(?p, false)
                -> hasRiskLevel(?p, LowRisk)
            """)
    
    def create_patient_individual(
        self,
        patient_features: PatientFeatures,
        bayesian_results: BayesianProbabilities,
        patient_id: str = "Patient_001"
    ):
        """
        Create patient individual in ontology with features and results
        
        Args:
            patient_features: Patient clinical features
            bayesian_results: Bayesian analysis results
            patient_id: Unique patient identifier
        """
        with self.onto:
            # Create patient individual
            patient = self.onto.Patient(patient_id)
            
            # Set age
            if patient_features.age:
                patient.hasAge.append(patient_features.age)
            
            # Set tumor size
            if patient_features.tumor_size_mm:
                patient.hasTumorSize.append(patient_features.tumor_size_mm)
            
            # Set Bayesian probabilities
            patient.hasCancerProbability.append(bayesian_results.cancer_probability)
            patient.hasRecurrenceRisk.append(bayesian_results.five_year_recurrence_risk)
            patient.hasConfidenceScore.append(bayesian_results.overall_confidence)
            
            # Create and link biomarkers
            if patient_features.er_status:
                er = self.onto.ER_Status(f"{patient_id}_ER")
                if patient_features.er_percentage:
                    er.hasER_Percentage.append(patient_features.er_percentage)
                patient.hasBiomarker.append(er)
            
            if patient_features.pr_status:
                pr = self.onto.PR_Status(f"{patient_id}_PR")
                if patient_features.pr_percentage:
                    pr.hasPR_Percentage.append(patient_features.pr_percentage)
                patient.hasBiomarker.append(pr)
            
            if patient_features.her2_status:
                her2 = self.onto.HER2_Status(f"{patient_id}_HER2")
                patient.hasBiomarker.append(her2)
            
            if patient_features.ki67_index is not None:
                ki67 = self.onto.Ki67_Index(f"{patient_id}_Ki67")
                ki67.hasKi67_Value.append(patient_features.ki67_index)
                patient.hasBiomarker.append(ki67)
            
            return patient
    
    def run_reasoner(self):
        """Execute OWL reasoner to infer new facts"""
        if not self.reasoner_initialized:
            sync_reasoner_pellet(self.onto)
            self.reasoner_initialized = True
        else:
            sync_reasoner_pellet(self.onto, infer_property_values=True)
    
    def get_inferred_subtype(self, patient_id: str) -> Optional[str]:
        """Get inferred molecular subtype for patient"""
        patient = self.onto.search_one(iri=f"*{patient_id}")
        if patient and patient.hasSubtype:
            return patient.hasSubtype[0].name
        return None
    
    def get_treatment_recommendations(self, patient_id: str) -> List[str]:
        """Get inferred treatment recommendations"""
        patient = self.onto.search_one(iri=f"*{patient_id}")
        if patient and patient.recommendsTreatment:
            return [t.name for t in patient.recommendsTreatment]
        return []
    
    def get_risk_level(self, patient_id: str) -> Optional[str]:
        """Get inferred risk stratification"""
        patient = self.onto.search_one(iri=f"*{patient_id}")
        if patient and patient.hasRiskLevel:
            return patient.hasRiskLevel[0].name
        return None
    
    def export_ontology(self, filename: str):
        """Export ontology to OWL file"""
        self.onto.save(file=filename, format="rdfxml")
    
    def query_sparql(self, query: str) -> List:
        """Execute SPARQL query on ontology"""
        graph = default_world.as_rdflib_graph()
        results = list(graph.query(query))
        return results
    
    def generate_explanation(self, patient_id: str) -> Dict:
        """
        Generate human-readable explanation of reasoning
        
        Returns:
            Dictionary with classification and reasoning
        """
        patient = self.onto.search_one(iri=f"*{patient_id}")
        
        if not patient:
            return {'error': 'Patient not found'}
        
        explanation = {
            'patient_id': patient_id,
            'classifications': {},
            'reasoning_steps': []
        }
        
        # Get molecular subtype
        if patient.hasSubtype:
            subtype = patient.hasSubtype[0].name
            explanation['classifications']['molecular_subtype'] = subtype
            
            # Explain subtype classification
            if 'LuminalA' in subtype:
                explanation['reasoning_steps'].append(
                    "Classified as Luminal A: ER+, PR+, HER2-, low Ki67 (<14%)"
                )
            elif 'LuminalB_HER2Negative' in subtype:
                explanation['reasoning_steps'].append(
                    "Classified as Luminal B (HER2-): ER+, high Ki67 (≥14%) or low PR, HER2-"
                )
            elif 'LuminalB_HER2Positive' in subtype:
                explanation['reasoning_steps'].append(
                    "Classified as Luminal B (HER2+): ER+, HER2+"
                )
            elif 'HER2Enriched' in subtype:
                explanation['reasoning_steps'].append(
                    "Classified as HER2-enriched: ER-, PR-, HER2+"
                )
            elif 'TripleNegative' in subtype:
                explanation['reasoning_steps'].append(
                    "Classified as Triple-negative: ER-, PR-, HER2-"
                )
        
        # Get treatment recommendations
        if patient.recommendsTreatment:
            treatments = [t.name for t in patient.recommendsTreatment]
            explanation['classifications']['treatments'] = treatments
            
            for treatment in treatments:
                if 'HormoneTherapy' in treatment:
                    explanation['reasoning_steps'].append(
                        "Hormone therapy recommended: Patient is ER-positive"
                    )
                elif 'HER2TargetedTherapy' in treatment:
                    explanation['reasoning_steps'].append(
                        "HER2-targeted therapy recommended: Patient is HER2-positive"
                    )
                elif 'Chemotherapy' in treatment:
                    explanation['reasoning_steps'].append(
                        "Chemotherapy recommended: Based on tumor characteristics and subtype"
                    )
        
        # Get risk level
        if patient.hasRiskLevel:
            risk = patient.hasRiskLevel[0].name
            explanation['classifications']['risk_level'] = risk
            explanation['reasoning_steps'].append(
                f"Risk stratified as {risk} based on tumor size, nodal status, and subtype"
            )
        
        return explanation


# ============= INTEGRATION FUNCTION =============

def run_complete_acr_pipeline(
    patient_features: PatientFeatures
) -> Dict:
    """
    Run complete ACR pipeline: Bayesian + Ontology reasoning
    
    Args:
        patient_features: Patient clinical features
        
    Returns:
        Combined results from both engines
    """
    from acr_bayesian_engine import BayesianReasoningEngine
    
    # Step 1: Bayesian analysis
    bayesian_engine = BayesianReasoningEngine()
    bayesian_results = bayesian_engine.compute_full_analysis(patient_features)
    
    # Step 2: Ontology reasoning
    ontology_reasoner = ACR_Ontology_Reasoner()
    ontology_reasoner.add_swrl_rules()
    
    patient_id = "Patient_001"
    ontology_reasoner.create_patient_individual(
        patient_features,
        bayesian_results,
        patient_id
    )
    
    # Run reasoner
    ontology_reasoner.run_reasoner()
    
    # Get inferred results
    inferred_subtype = ontology_reasoner.get_inferred_subtype(patient_id)
    inferred_treatments = ontology_reasoner.get_treatment_recommendations(patient_id)
    inferred_risk = ontology_reasoner.get_risk_level(patient_id)
    
    # Generate explanation
    explanation = ontology_reasoner.generate_explanation(patient_id)
    
    # Combine results
    return {
        'bayesian_analysis': {
            'cancer_probability': bayesian_results.cancer_probability,
            'subtype_probabilities': {
                k.value: v for k, v in bayesian_results.subtype_probabilities.items()
            },
            'most_likely_subtype': bayesian_results.most_likely_subtype.value,
            'risk_level': bayesian_results.estimated_risk_level.value,
            'treatment_responses': {
                'hormone_therapy': bayesian_results.hormone_therapy_response_prob,
                'chemotherapy': bayesian_results.chemotherapy_response_prob,
                'her2_targeted': bayesian_results.her2_targeted_response_prob
            },
            'recurrence_risk_5yr': bayesian_results.five_year_recurrence_risk,
            'confidence': bayesian_results.overall_confidence,
            'reasoning_chain': bayesian_results.reasoning_chain
        },
        'ontology_reasoning': {
            'inferred_subtype': inferred_subtype,
            'inferred_treatments': inferred_treatments,
            'inferred_risk': inferred_risk,
            'explanation': explanation
        },
        'patient_features': {
            'age': patient_features.age,
            'tumor_size_mm': patient_features.tumor_size_mm,
            'er_status': patient_features.er_status,
            'pr_status': patient_features.pr_status,
            'her2_status': patient_features.her2_status,
            'ki67_index': patient_features.ki67_index
        }
    }


# ============= EXAMPLE USAGE =============

if __name__ == '__main__':
    print("ACR Ontology Reasoner initialized")
    print("Ready to perform semantic reasoning with SWRL rules")
