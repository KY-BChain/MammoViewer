#!/usr/bin/env python3
"""
ACR Platform - Bayesian Reasoning Engine
Integrates Bayesian inference for breast cancer diagnosis and treatment recommendations

Author: ACR Development Team
Date: 2025-11-11
Version: 1.0.0
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime


class MolecularSubtype(Enum):
    """Molecular subtypes of breast cancer"""
    LUMINAL_A = "Luminal A"
    LUMINAL_B_HER2_NEG = "Luminal B (HER2-)"
    LUMINAL_B_HER2_POS = "Luminal B (HER2+)"
    HER2_ENRICHED = "HER2-enriched"
    TRIPLE_NEGATIVE = "Triple-negative"
    UNKNOWN = "Unknown"


class RiskLevel(Enum):
    """Risk stratification levels"""
    LOW = "Low"
    INTERMEDIATE = "Intermediate"
    HIGH = "High"
    VERY_HIGH = "Very High"


@dataclass
class PatientFeatures:
    """Patient clinical and demographic features"""
    # Demographics
    age: int
    ethnicity: Optional[str] = None
    
    # Clinical stage
    tumor_size_mm: Optional[float] = None
    lymph_node_status: Optional[str] = None  # N0, N1, N2, N3
    metastasis_status: Optional[str] = None  # M0, M1
    clinical_stage: Optional[str] = None  # I, II, III, IV
    
    # Biomarkers
    er_status: Optional[str] = None  # Positive/Negative
    er_percentage: Optional[float] = None  # 0-100
    pr_status: Optional[str] = None  # Positive/Negative
    pr_percentage: Optional[float] = None  # 0-100
    her2_status: Optional[str] = None  # Positive/Negative/Equivocal
    her2_ihc_score: Optional[str] = None  # 0, 1+, 2+, 3+
    her2_fish_ratio: Optional[float] = None
    ki67_index: Optional[float] = None  # 0-100
    
    # Histology
    histological_grade: Optional[str] = None  # I, II, III
    histological_type: Optional[str] = None  # IDC, ILC, etc.
    
    # Imaging findings
    mammogram_birad: Optional[int] = None  # 0-6
    mammogram_positive: Optional[bool] = None
    ultrasound_findings: Optional[str] = None
    mri_findings: Optional[str] = None
    
    # Risk factors
    family_history_breast_cancer: bool = False
    family_history_ovarian_cancer: bool = False
    brca1_mutation: Optional[bool] = None
    brca2_mutation: Optional[bool] = None
    prior_breast_cancer: bool = False
    
    # Treatment history
    prior_chemotherapy: bool = False
    prior_radiation: bool = False
    prior_hormone_therapy: bool = False


@dataclass
class BayesianProbabilities:
    """Probability estimates from Bayesian inference"""
    # Cancer presence probabilities
    cancer_probability: float = 0.0
    malignancy_probability: float = 0.0
    
    # Subtype probabilities
    subtype_probabilities: Dict[MolecularSubtype, float] = field(default_factory=dict)
    most_likely_subtype: Optional[MolecularSubtype] = None
    
    # Risk stratification
    risk_probabilities: Dict[RiskLevel, float] = field(default_factory=dict)
    estimated_risk_level: Optional[RiskLevel] = None
    
    # Treatment response predictions
    hormone_therapy_response_prob: float = 0.0
    chemotherapy_response_prob: float = 0.0
    her2_targeted_response_prob: float = 0.0
    
    # Recurrence risk
    five_year_recurrence_risk: float = 0.0
    ten_year_recurrence_risk: float = 0.0
    
    # Confidence metrics
    overall_confidence: float = 0.0
    data_completeness: float = 0.0
    
    # Supporting evidence
    reasoning_chain: List[str] = field(default_factory=list)
    prior_probabilities: Dict[str, float] = field(default_factory=dict)
    likelihood_ratios: Dict[str, float] = field(default_factory=dict)


class BayesianReasoningEngine:
    """
    Main Bayesian reasoning engine for ACR Platform
    Implements Bayesian inference for breast cancer diagnosis and treatment
    """
    
    def __init__(self):
        """Initialize the Bayesian engine with base rates and parameters"""
        self.base_rates = self._load_base_rates()
        self.likelihood_params = self._load_likelihood_parameters()
        
    def _load_base_rates(self) -> Dict:
        """Load population base rates for breast cancer"""
        return {
            # Age-specific breast cancer incidence (per 1000 women)
            'age_groups': {
                '20-29': 0.0004,
                '30-39': 0.0044,
                '40-49': 0.0147,
                '50-59': 0.0237,
                '60-69': 0.0342,
                '70-79': 0.0372,
                '80+': 0.0363
            },
            
            # Molecular subtype distribution
            'subtypes': {
                MolecularSubtype.LUMINAL_A: 0.40,
                MolecularSubtype.LUMINAL_B_HER2_NEG: 0.20,
                MolecularSubtype.LUMINAL_B_HER2_POS: 0.10,
                MolecularSubtype.HER2_ENRICHED: 0.15,
                MolecularSubtype.TRIPLE_NEGATIVE: 0.15
            },
            
            # Risk factor prevalences
            'family_history': 0.20,
            'brca1_mutation': 0.0025,
            'brca2_mutation': 0.0025,
        }
    
    def _load_likelihood_parameters(self) -> Dict:
        """Load likelihood ratios and test sensitivities/specificities"""
        return {
            # Mammography test characteristics
            'mammography': {
                'sensitivity': 0.80,  # P(Positive|Cancer)
                'specificity': 0.904,  # P(Negative|No Cancer)
                'ppv_by_age': {
                    '40-49': 0.078,
                    '50-59': 0.14,
                    '60-69': 0.22,
                    '70+': 0.27
                }
            },
            
            # BI-RADS likelihood ratios
            'birad_lr': {
                0: 0.5,   # Incomplete - inconclusive
                1: 0.1,   # Negative
                2: 0.1,   # Benign
                3: 0.67,  # Probably benign (2% risk)
                4: 8.0,   # Suspicious (2-95% risk)
                5: 50.0,  # Highly suspicious (>95% risk)
                6: 100.0  # Known biopsy-proven malignancy
            },
            
            # Biomarker-specific likelihoods
            'biomarkers': {
                'ER_positive': {
                    'luminal_a': 0.95,
                    'luminal_b': 0.90,
                    'her2_enriched': 0.20,
                    'triple_negative': 0.0
                },
                'PR_positive': {
                    'luminal_a': 0.90,
                    'luminal_b': 0.80,
                    'her2_enriched': 0.15,
                    'triple_negative': 0.0
                },
                'HER2_positive': {
                    'luminal_a': 0.05,
                    'luminal_b_her2_pos': 0.95,
                    'her2_enriched': 0.95,
                    'triple_negative': 0.0
                },
                'high_ki67': {  # >14%
                    'luminal_a': 0.10,
                    'luminal_b': 0.90,
                    'her2_enriched': 0.85,
                    'triple_negative': 0.90
                }
            },
            
            # Family history likelihood ratios
            'family_history': {
                'first_degree': 2.1,   # Relative risk
                'two_first_degree': 3.6,
                'brca1_mutation': 60.0,  # Lifetime risk 60-80%
                'brca2_mutation': 45.0   # Lifetime risk 45-55%
            },
            
            # Lymph node involvement probability
            'lymph_node_involvement': {
                'T1': 0.20,  # <2cm
                'T2': 0.40,  # 2-5cm
                'T3': 0.60,  # >5cm
                'T4': 0.80   # Chest wall/skin invasion
            }
        }
    
    def calculate_cancer_probability(
        self, 
        patient: PatientFeatures
    ) -> Tuple[float, List[str]]:
        """
        Calculate probability of breast cancer using Bayesian inference
        
        Args:
            patient: PatientFeatures object with clinical data
            
        Returns:
            Tuple of (probability, reasoning_chain)
        """
        reasoning = []
        
        # Step 1: Get prior probability based on age
        prior = self._get_age_based_prior(patient.age)
        reasoning.append(f"Prior probability based on age {patient.age}: {prior:.4f}")
        
        # Step 2: Update with family history
        if patient.family_history_breast_cancer:
            lr = self.likelihood_params['family_history']['first_degree']
            prior = self._bayes_update(prior, lr)
            reasoning.append(f"Updated with family history (LR={lr}): {prior:.4f}")
        
        # Step 3: Update with BRCA mutations
        if patient.brca1_mutation:
            lr = self.likelihood_params['family_history']['brca1_mutation']
            prior = self._bayes_update(prior, lr)
            reasoning.append(f"Updated with BRCA1 mutation (LR={lr}): {prior:.4f}")
        
        if patient.brca2_mutation:
            lr = self.likelihood_params['family_history']['brca2_mutation']
            prior = self._bayes_update(prior, lr)
            reasoning.append(f"Updated with BRCA2 mutation (LR={lr}): {prior:.4f}")
        
        # Step 4: Update with mammography result
        if patient.mammogram_positive is not None:
            if patient.mammogram_positive:
                sensitivity = self.likelihood_params['mammography']['sensitivity']
                specificity = self.likelihood_params['mammography']['specificity']
                posterior = self._mammography_bayes_update(
                    prior, sensitivity, specificity, positive=True
                )
                reasoning.append(
                    f"Updated with positive mammography: {posterior:.4f}"
                )
                prior = posterior
            else:
                # Negative mammography
                sensitivity = self.likelihood_params['mammography']['sensitivity']
                specificity = self.likelihood_params['mammography']['specificity']
                posterior = self._mammography_bayes_update(
                    prior, sensitivity, specificity, positive=False
                )
                reasoning.append(
                    f"Updated with negative mammography: {posterior:.4f}"
                )
                prior = posterior
        
        # Step 5: Update with BI-RADS if available
        if patient.mammogram_birad is not None:
            lr = self.likelihood_params['birad_lr'].get(patient.mammogram_birad, 1.0)
            posterior = self._bayes_update(prior, lr)
            reasoning.append(
                f"Updated with BI-RADS {patient.mammogram_birad} (LR={lr}): {posterior:.4f}"
            )
            prior = posterior
        
        return prior, reasoning
    
    def classify_molecular_subtype(
        self,
        patient: PatientFeatures
    ) -> Tuple[MolecularSubtype, Dict[MolecularSubtype, float], List[str]]:
        """
        Classify molecular subtype using Bayesian inference on biomarkers
        
        Returns:
            Tuple of (most_likely_subtype, all_probabilities, reasoning)
        """
        reasoning = []
        
        # Start with base rate priors
        probabilities = self.base_rates['subtypes'].copy()
        reasoning.append(f"Initial subtype priors: {self._format_probs(probabilities)}")
        
        # Update with ER status
        if patient.er_status:
            probabilities = self._update_subtype_with_er(
                probabilities, patient.er_status, patient.er_percentage
            )
            reasoning.append(
                f"After ER {patient.er_status}: {self._format_probs(probabilities)}"
            )
        
        # Update with PR status
        if patient.pr_status:
            probabilities = self._update_subtype_with_pr(
                probabilities, patient.pr_status, patient.pr_percentage
            )
            reasoning.append(
                f"After PR {patient.pr_status}: {self._format_probs(probabilities)}"
            )
        
        # Update with HER2 status
        if patient.her2_status:
            probabilities = self._update_subtype_with_her2(
                probabilities, patient.her2_status
            )
            reasoning.append(
                f"After HER2 {patient.her2_status}: {self._format_probs(probabilities)}"
            )
        
        # Update with Ki67
        if patient.ki67_index is not None:
            probabilities = self._update_subtype_with_ki67(
                probabilities, patient.ki67_index
            )
            reasoning.append(
                f"After Ki67 {patient.ki67_index}%: {self._format_probs(probabilities)}"
            )
        
        # Normalize probabilities
        total = sum(probabilities.values())
        probabilities = {k: v/total for k, v in probabilities.items()}
        
        # Get most likely subtype
        most_likely = max(probabilities.items(), key=lambda x: x[1])
        
        reasoning.append(f"Final classification: {most_likely[0].value} ({most_likely[1]:.2%})")
        
        return most_likely[0], probabilities, reasoning
    
    def estimate_treatment_response(
        self,
        patient: PatientFeatures,
        subtype: MolecularSubtype
    ) -> Dict[str, float]:
        """
        Estimate probability of response to different treatment modalities
        
        Returns:
            Dictionary of treatment: response_probability
        """
        responses = {}
        
        # Hormone therapy response (for ER+ tumors)
        if patient.er_status == "Positive":
            # Base response rate for ER+ tumors
            base_response = 0.70
            
            # Adjust based on ER percentage
            if patient.er_percentage:
                if patient.er_percentage >= 50:
                    base_response *= 1.15
                elif patient.er_percentage < 10:
                    base_response *= 0.70
            
            # Adjust for PR status (better response if PR+)
            if patient.pr_status == "Positive":
                base_response *= 1.10
            
            # Adjust for Ki67 (lower Ki67 = better hormone response)
            if patient.ki67_index:
                if patient.ki67_index < 14:
                    base_response *= 1.10
                elif patient.ki67_index > 30:
                    base_response *= 0.85
            
            responses['hormone_therapy'] = min(base_response, 0.95)
        else:
            responses['hormone_therapy'] = 0.05  # Unlikely if ER-
        
        # Chemotherapy response
        chemo_base = {
            MolecularSubtype.LUMINAL_A: 0.50,
            MolecularSubtype.LUMINAL_B_HER2_NEG: 0.65,
            MolecularSubtype.LUMINAL_B_HER2_POS: 0.75,
            MolecularSubtype.HER2_ENRICHED: 0.80,
            MolecularSubtype.TRIPLE_NEGATIVE: 0.75
        }
        
        responses['chemotherapy'] = chemo_base.get(subtype, 0.60)
        
        # HER2-targeted therapy (if HER2+)
        if patient.her2_status == "Positive":
            # Trastuzumab response rates
            base_her2_response = 0.85
            
            # Adjust based on HER2 intensity
            if patient.her2_ihc_score == "3+":
                base_her2_response *= 1.05
            elif patient.her2_ihc_score == "2+":
                base_her2_response *= 0.95
            
            responses['her2_targeted'] = min(base_her2_response, 0.95)
        else:
            responses['her2_targeted'] = 0.0
        
        return responses
    
    def estimate_recurrence_risk(
        self,
        patient: PatientFeatures,
        subtype: MolecularSubtype
    ) -> Tuple[float, float]:
        """
        Estimate 5-year and 10-year recurrence risk
        
        Returns:
            Tuple of (five_year_risk, ten_year_risk)
        """
        # Base recurrence rates by subtype
        base_rates = {
            MolecularSubtype.LUMINAL_A: (0.10, 0.20),
            MolecularSubtype.LUMINAL_B_HER2_NEG: (0.15, 0.30),
            MolecularSubtype.LUMINAL_B_HER2_POS: (0.20, 0.35),
            MolecularSubtype.HER2_ENRICHED: (0.25, 0.40),
            MolecularSubtype.TRIPLE_NEGATIVE: (0.30, 0.40)
        }
        
        five_yr, ten_yr = base_rates.get(subtype, (0.20, 0.35))
        
        # Adjust for tumor size
        if patient.tumor_size_mm:
            if patient.tumor_size_mm > 50:  # T3
                five_yr *= 1.5
                ten_yr *= 1.3
            elif patient.tumor_size_mm > 20:  # T2
                five_yr *= 1.2
                ten_yr *= 1.15
        
        # Adjust for lymph node involvement
        if patient.lymph_node_status:
            if 'N3' in patient.lymph_node_status:
                five_yr *= 2.0
                ten_yr *= 1.8
            elif 'N2' in patient.lymph_node_status:
                five_yr *= 1.6
                ten_yr *= 1.5
            elif 'N1' in patient.lymph_node_status:
                five_yr *= 1.3
                ten_yr *= 1.25
        
        # Adjust for grade
        if patient.histological_grade == "III":
            five_yr *= 1.4
            ten_yr *= 1.3
        elif patient.histological_grade == "I":
            five_yr *= 0.7
            ten_yr *= 0.8
        
        # Cap at reasonable maximum
        five_yr = min(five_yr, 0.80)
        ten_yr = min(ten_yr, 0.85)
        
        return five_yr, ten_yr
    
    def compute_full_analysis(
        self,
        patient: PatientFeatures
    ) -> BayesianProbabilities:
        """
        Perform complete Bayesian analysis of patient data
        
        Returns:
            BayesianProbabilities object with all computed probabilities
        """
        result = BayesianProbabilities()
        
        # Calculate cancer probability
        cancer_prob, cancer_reasoning = self.calculate_cancer_probability(patient)
        result.cancer_probability = cancer_prob
        result.malignancy_probability = cancer_prob
        result.reasoning_chain.extend(cancer_reasoning)
        
        # Classify molecular subtype
        subtype, subtype_probs, subtype_reasoning = self.classify_molecular_subtype(patient)
        result.most_likely_subtype = subtype
        result.subtype_probabilities = subtype_probs
        result.reasoning_chain.extend(subtype_reasoning)
        
        # Estimate treatment responses
        treatment_responses = self.estimate_treatment_response(patient, subtype)
        result.hormone_therapy_response_prob = treatment_responses.get('hormone_therapy', 0.0)
        result.chemotherapy_response_prob = treatment_responses.get('chemotherapy', 0.0)
        result.her2_targeted_response_prob = treatment_responses.get('her2_targeted', 0.0)
        
        # Estimate recurrence risk
        five_yr_risk, ten_yr_risk = self.estimate_recurrence_risk(patient, subtype)
        result.five_year_recurrence_risk = five_yr_risk
        result.ten_year_recurrence_risk = ten_yr_risk
        
        # Risk stratification
        result.risk_probabilities = self._stratify_risk(patient, subtype, five_yr_risk)
        result.estimated_risk_level = max(
            result.risk_probabilities.items(), key=lambda x: x[1]
        )[0]
        
        # Calculate confidence metrics
        result.data_completeness = self._calculate_data_completeness(patient)
        result.overall_confidence = self._calculate_overall_confidence(result)
        
        return result
    
    # ============= HELPER METHODS =============
    
    def _get_age_based_prior(self, age: int) -> float:
        """Get prior probability based on patient age"""
        if age < 30:
            return self.base_rates['age_groups']['20-29']
        elif age < 40:
            return self.base_rates['age_groups']['30-39']
        elif age < 50:
            return self.base_rates['age_groups']['40-49']
        elif age < 60:
            return self.base_rates['age_groups']['50-59']
        elif age < 70:
            return self.base_rates['age_groups']['60-69']
        elif age < 80:
            return self.base_rates['age_groups']['70-79']
        else:
            return self.base_rates['age_groups']['80+']
    
    def _bayes_update(self, prior: float, likelihood_ratio: float) -> float:
        """
        Update probability using likelihood ratio
        
        P(H|E) = LR * P(H) / [LR * P(H) + (1 - P(H))]
        """
        numerator = likelihood_ratio * prior
        denominator = likelihood_ratio * prior + (1 - prior)
        return numerator / denominator
    
    def _mammography_bayes_update(
        self,
        prior: float,
        sensitivity: float,
        specificity: float,
        positive: bool
    ) -> float:
        """Update probability based on mammography result"""
        if positive:
            # Positive test
            numerator = sensitivity * prior
            denominator = sensitivity * prior + (1 - specificity) * (1 - prior)
        else:
            # Negative test
            numerator = (1 - sensitivity) * prior
            denominator = (1 - sensitivity) * prior + specificity * (1 - prior)
        
        return numerator / denominator
    
    def _update_subtype_with_er(
        self,
        probs: Dict[MolecularSubtype, float],
        er_status: str,
        er_percentage: Optional[float]
    ) -> Dict[MolecularSubtype, float]:
        """Update subtype probabilities with ER status"""
        likelihoods = self.likelihood_params['biomarkers']['ER_positive']
        
        if er_status == "Positive":
            # Multiply each prior by likelihood of ER+ given that subtype
            probs[MolecularSubtype.LUMINAL_A] *= likelihoods['luminal_a']
            probs[MolecularSubtype.LUMINAL_B_HER2_NEG] *= likelihoods['luminal_b']
            probs[MolecularSubtype.LUMINAL_B_HER2_POS] *= likelihoods['luminal_b']
            probs[MolecularSubtype.HER2_ENRICHED] *= likelihoods['her2_enriched']
            probs[MolecularSubtype.TRIPLE_NEGATIVE] *= 0.01  # Very unlikely
        else:
            # ER negative
            probs[MolecularSubtype.LUMINAL_A] *= (1 - likelihoods['luminal_a'])
            probs[MolecularSubtype.LUMINAL_B_HER2_NEG] *= (1 - likelihoods['luminal_b'])
            probs[MolecularSubtype.LUMINAL_B_HER2_POS] *= (1 - likelihoods['luminal_b'])
            probs[MolecularSubtype.HER2_ENRICHED] *= (1 - likelihoods['her2_enriched'])
            probs[MolecularSubtype.TRIPLE_NEGATIVE] *= 1.0  # Consistent with TNBC
        
        return probs
    
    def _update_subtype_with_pr(
        self,
        probs: Dict[MolecularSubtype, float],
        pr_status: str,
        pr_percentage: Optional[float]
    ) -> Dict[MolecularSubtype, float]:
        """Update subtype probabilities with PR status"""
        likelihoods = self.likelihood_params['biomarkers']['PR_positive']
        
        if pr_status == "Positive":
            probs[MolecularSubtype.LUMINAL_A] *= likelihoods['luminal_a']
            probs[MolecularSubtype.LUMINAL_B_HER2_NEG] *= likelihoods['luminal_b']
            probs[MolecularSubtype.LUMINAL_B_HER2_POS] *= likelihoods['luminal_b']
            probs[MolecularSubtype.HER2_ENRICHED] *= likelihoods['her2_enriched']
            probs[MolecularSubtype.TRIPLE_NEGATIVE] *= 0.01
        else:
            probs[MolecularSubtype.LUMINAL_A] *= (1 - likelihoods['luminal_a'])
            probs[MolecularSubtype.LUMINAL_B_HER2_NEG] *= (1 - likelihoods['luminal_b'])
            probs[MolecularSubtype.LUMINAL_B_HER2_POS] *= (1 - likelihoods['luminal_b'])
            probs[MolecularSubtype.HER2_ENRICHED] *= (1 - likelihoods['her2_enriched'])
            probs[MolecularSubtype.TRIPLE_NEGATIVE] *= 1.0
        
        return probs
    
    def _update_subtype_with_her2(
        self,
        probs: Dict[MolecularSubtype, float],
        her2_status: str
    ) -> Dict[MolecularSubtype, float]:
        """Update subtype probabilities with HER2 status"""
        likelihoods = self.likelihood_params['biomarkers']['HER2_positive']
        
        if her2_status == "Positive":
            probs[MolecularSubtype.LUMINAL_A] *= likelihoods['luminal_a']
            probs[MolecularSubtype.LUMINAL_B_HER2_NEG] *= 0.01
            probs[MolecularSubtype.LUMINAL_B_HER2_POS] *= likelihoods['luminal_b_her2_pos']
            probs[MolecularSubtype.HER2_ENRICHED] *= likelihoods['her2_enriched']
            probs[MolecularSubtype.TRIPLE_NEGATIVE] *= 0.01
        else:
            probs[MolecularSubtype.LUMINAL_A] *= (1 - likelihoods['luminal_a'])
            probs[MolecularSubtype.LUMINAL_B_HER2_NEG] *= 1.0
            probs[MolecularSubtype.LUMINAL_B_HER2_POS] *= (1 - likelihoods['luminal_b_her2_pos'])
            probs[MolecularSubtype.HER2_ENRICHED] *= (1 - likelihoods['her2_enriched'])
            probs[MolecularSubtype.TRIPLE_NEGATIVE] *= 1.0
        
        return probs
    
    def _update_subtype_with_ki67(
        self,
        probs: Dict[MolecularSubtype, float],
        ki67_index: float
    ) -> Dict[MolecularSubtype, float]:
        """Update subtype probabilities with Ki67 index"""
        likelihoods = self.likelihood_params['biomarkers']['high_ki67']
        
        if ki67_index > 14:  # High Ki67
            probs[MolecularSubtype.LUMINAL_A] *= likelihoods['luminal_a']
            probs[MolecularSubtype.LUMINAL_B_HER2_NEG] *= likelihoods['luminal_b']
            probs[MolecularSubtype.LUMINAL_B_HER2_POS] *= likelihoods['luminal_b']
            probs[MolecularSubtype.HER2_ENRICHED] *= likelihoods['her2_enriched']
            probs[MolecularSubtype.TRIPLE_NEGATIVE] *= likelihoods['triple_negative']
        else:  # Low Ki67
            probs[MolecularSubtype.LUMINAL_A] *= (1 - likelihoods['luminal_a'])
            probs[MolecularSubtype.LUMINAL_B_HER2_NEG] *= (1 - likelihoods['luminal_b'])
            probs[MolecularSubtype.LUMINAL_B_HER2_POS] *= (1 - likelihoods['luminal_b'])
            probs[MolecularSubtype.HER2_ENRICHED] *= (1 - likelihoods['her2_enriched'])
            probs[MolecularSubtype.TRIPLE_NEGATIVE] *= (1 - likelihoods['triple_negative'])
        
        return probs
    
    def _stratify_risk(
        self,
        patient: PatientFeatures,
        subtype: MolecularSubtype,
        five_year_risk: float
    ) -> Dict[RiskLevel, float]:
        """Stratify patient into risk categories"""
        # Initialize with base assumption
        risk_probs = {
            RiskLevel.LOW: 0.25,
            RiskLevel.INTERMEDIATE: 0.25,
            RiskLevel.HIGH: 0.25,
            RiskLevel.VERY_HIGH: 0.25
        }
        
        # Adjust based on 5-year recurrence risk
        if five_year_risk < 0.10:
            risk_probs[RiskLevel.LOW] = 0.70
            risk_probs[RiskLevel.INTERMEDIATE] = 0.20
            risk_probs[RiskLevel.HIGH] = 0.08
            risk_probs[RiskLevel.VERY_HIGH] = 0.02
        elif five_year_risk < 0.20:
            risk_probs[RiskLevel.LOW] = 0.20
            risk_probs[RiskLevel.INTERMEDIATE] = 0.60
            risk_probs[RiskLevel.HIGH] = 0.15
            risk_probs[RiskLevel.VERY_HIGH] = 0.05
        elif five_year_risk < 0.30:
            risk_probs[RiskLevel.LOW] = 0.05
            risk_probs[RiskLevel.INTERMEDIATE] = 0.25
            risk_probs[RiskLevel.HIGH] = 0.55
            risk_probs[RiskLevel.VERY_HIGH] = 0.15
        else:
            risk_probs[RiskLevel.LOW] = 0.02
            risk_probs[RiskLevel.INTERMEDIATE] = 0.08
            risk_probs[RiskLevel.HIGH] = 0.30
            risk_probs[RiskLevel.VERY_HIGH] = 0.60
        
        return risk_probs
    
    def _calculate_data_completeness(self, patient: PatientFeatures) -> float:
        """Calculate what percentage of relevant data is available"""
        fields = [
            patient.age is not None,
            patient.tumor_size_mm is not None,
            patient.lymph_node_status is not None,
            patient.clinical_stage is not None,
            patient.er_status is not None,
            patient.pr_status is not None,
            patient.her2_status is not None,
            patient.ki67_index is not None,
            patient.histological_grade is not None,
            patient.mammogram_birad is not None
        ]
        
        return sum(fields) / len(fields)
    
    def _calculate_overall_confidence(self, result: BayesianProbabilities) -> float:
        """Calculate overall confidence in the analysis"""
        # Base confidence on data completeness
        confidence = result.data_completeness * 100
        
        # Adjust based on probability distributions
        # High confidence if one subtype clearly dominant
        if result.subtype_probabilities:
            max_prob = max(result.subtype_probabilities.values())
            if max_prob > 0.80:
                confidence *= 1.10
            elif max_prob < 0.50:
                confidence *= 0.85
        
        # Cap at 95% (never 100% certain)
        return min(confidence, 95.0)
    
    def _format_probs(self, probs: Dict) -> str:
        """Format probability dictionary for display"""
        return ", ".join([f"{k.value if hasattr(k, 'value') else k}: {v:.2%}" 
                         for k, v in sorted(probs.items(), key=lambda x: -x[1])[:3]])


# ============= CONVENIENCE FUNCTIONS =============

def create_patient_from_dict(data: Dict) -> PatientFeatures:
    """Create PatientFeatures object from dictionary"""
    return PatientFeatures(**{k: v for k, v in data.items() if k in PatientFeatures.__annotations__})


def export_results_to_json(results: BayesianProbabilities, filename: str):
    """Export Bayesian analysis results to JSON file"""
    output = {
        'timestamp': datetime.now().isoformat(),
        'cancer_probability': results.cancer_probability,
        'malignancy_probability': results.malignancy_probability,
        'most_likely_subtype': results.most_likely_subtype.value if results.most_likely_subtype else None,
        'subtype_probabilities': {
            k.value: v for k, v in results.subtype_probabilities.items()
        },
        'estimated_risk_level': results.estimated_risk_level.value if results.estimated_risk_level else None,
        'risk_probabilities': {
            k.value: v for k, v in results.risk_probabilities.items()
        },
        'treatment_response_predictions': {
            'hormone_therapy': results.hormone_therapy_response_prob,
            'chemotherapy': results.chemotherapy_response_prob,
            'her2_targeted': results.her2_targeted_response_prob
        },
        'recurrence_risk': {
            '5_year': results.five_year_recurrence_risk,
            '10_year': results.ten_year_recurrence_risk
        },
        'confidence_metrics': {
            'overall_confidence': results.overall_confidence,
            'data_completeness': results.data_completeness
        },
        'reasoning_chain': results.reasoning_chain
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


# ============= EXAMPLE USAGE =============

if __name__ == '__main__':
    # Example patient
    patient = PatientFeatures(
        age=52,
        tumor_size_mm=23.5,
        lymph_node_status="N1",
        clinical_stage="IIA",
        er_status="Positive",
        er_percentage=85,
        pr_status="Positive",
        pr_percentage=70,
        her2_status="Negative",
        ki67_index=18,
        histological_grade="II",
        mammogram_birad=5,
        mammogram_positive=True,
        family_history_breast_cancer=True
    )
    
    # Create engine and analyze
    engine = BayesianReasoningEngine()
    results = engine.compute_full_analysis(patient)
    
    # Print results
    print("="*60)
    print("BAYESIAN ANALYSIS RESULTS")
    print("="*60)
    print(f"\nCancer Probability: {results.cancer_probability:.2%}")
    print(f"Most Likely Subtype: {results.most_likely_subtype.value}")
    print(f"Risk Level: {results.estimated_risk_level.value}")
    print(f"5-Year Recurrence Risk: {results.five_year_recurrence_risk:.2%}")
    print(f"Overall Confidence: {results.overall_confidence:.1f}%")
    print(f"\nReasoning Chain:")
    for i, step in enumerate(results.reasoning_chain, 1):
        print(f"  {i}. {step}")
    
    # Export to JSON
    export_results_to_json(results, 'bayesian_analysis_results.json')
    print(f"\n✓ Results exported to bayesian_analysis_results.json")
