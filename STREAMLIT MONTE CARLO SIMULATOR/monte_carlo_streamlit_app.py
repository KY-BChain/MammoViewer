#!/usr/bin/env python3
"""
Monte Carlo Simulation - Streamlit Interactive Application
Comprehensive simulator with multiple scenarios including clinical applications

Author: ACR Development Team
Date: 2025-01-27
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats
from dataclasses import dataclass
from typing import List, Dict, Tuple
import time


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Monte Carlo Simulation App",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS STYLING
# ============================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .stButton>button {
        width: 100%;
        background-color: #667eea;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem;
        border: none;
        font-size: 1.1rem;
    }
    
    .stButton>button:hover {
        background-color: #5568d3;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class SimulationResult:
    """Store Monte Carlo simulation results"""
    outcomes: np.ndarray
    mean: float
    median: float
    std: float
    percentile_5: float
    percentile_95: float
    min_value: float
    max_value: float
    confidence_interval_95: Tuple[float, float]
    probability_success: float


# ============================================================
# MONTE CARLO SIMULATION FUNCTIONS
# ============================================================

def run_monte_carlo_basic(
    num_simulations: int,
    mean: float,
    std_dev: float,
    distribution: str = 'normal'
) -> SimulationResult:
    """
    Basic Monte Carlo simulation with various distributions
    
    Args:
        num_simulations: Number of iterations
        mean: Mean value
        std_dev: Standard deviation
        distribution: Type of distribution ('normal', 'lognormal', 'uniform')
    
    Returns:
        SimulationResult object
    """
    
    if distribution == 'normal':
        outcomes = np.random.normal(mean, std_dev, num_simulations)
    elif distribution == 'lognormal':
        # For lognormal, mean and std are of the underlying normal
        outcomes = np.random.lognormal(mean, std_dev, num_simulations)
    elif distribution == 'uniform':
        # Use mean ± 2*std as bounds for uniform
        low = mean - 2 * std_dev
        high = mean + 2 * std_dev
        outcomes = np.random.uniform(low, high, num_simulations)
    else:
        outcomes = np.random.normal(mean, std_dev, num_simulations)
    
    return _calculate_statistics(outcomes)


def run_portfolio_simulation(
    num_simulations: int,
    initial_investment: float,
    expected_return: float,
    volatility: float,
    years: int
) -> Tuple[SimulationResult, np.ndarray]:
    """
    Financial portfolio Monte Carlo simulation
    
    Returns:
        Tuple of (final_values_result, all_paths)
    """
    
    dt = 1  # Annual time steps
    paths = np.zeros((num_simulations, years + 1))
    paths[:, 0] = initial_investment
    
    for t in range(1, years + 1):
        # Geometric Brownian Motion
        z = np.random.standard_normal(num_simulations)
        paths[:, t] = paths[:, t-1] * np.exp(
            (expected_return - 0.5 * volatility**2) * dt + 
            volatility * np.sqrt(dt) * z
        )
    
    final_values = paths[:, -1]
    return _calculate_statistics(final_values), paths


def run_clinical_outcome_simulation(
    num_simulations: int,
    base_success_rate: float,
    treatment_effect: float,
    patient_variability: float,
    follow_up_years: int = 5
) -> Tuple[SimulationResult, Dict]:
    """
    Clinical outcome Monte Carlo simulation for medical treatments
    
    Args:
        num_simulations: Number of patient simulations
        base_success_rate: Baseline success probability (0-1)
        treatment_effect: Additional treatment benefit (0-1)
        patient_variability: Individual variation (std dev)
        follow_up_years: Years of follow-up
        
    Returns:
        Tuple of (survival_result, detailed_outcomes)
    """
    
    # Simulate individual patient success rates with variability
    patient_rates = np.random.normal(
        base_success_rate + treatment_effect,
        patient_variability,
        num_simulations
    )
    
    # Clip to valid probability range [0, 1]
    patient_rates = np.clip(patient_rates, 0, 1)
    
    # Simulate survival/success over time
    survival_outcomes = np.zeros((num_simulations, follow_up_years + 1))
    survival_outcomes[:, 0] = 1.0  # Everyone starts at 100%
    
    for year in range(1, follow_up_years + 1):
        # Each year, probability of continued success
        year_success = np.random.binomial(1, patient_rates, num_simulations)
        survival_outcomes[:, year] = survival_outcomes[:, year-1] * year_success
    
    # Calculate final outcomes
    final_survival = survival_outcomes[:, -1]
    
    detailed_outcomes = {
        'patient_rates': patient_rates,
        'survival_curves': survival_outcomes,
        'yearly_survival': np.mean(survival_outcomes, axis=0),
        'final_survival': final_survival
    }
    
    return _calculate_statistics(final_survival), detailed_outcomes


def run_treatment_cost_effectiveness(
    num_simulations: int,
    treatment_cost_mean: float,
    treatment_cost_std: float,
    qaly_gain_mean: float,
    qaly_gain_std: float,
    willingness_to_pay: float = 50000
) -> Tuple[SimulationResult, Dict]:
    """
    Cost-effectiveness Monte Carlo simulation for medical treatments
    
    QALY = Quality-Adjusted Life Years
    ICER = Incremental Cost-Effectiveness Ratio
    
    Returns:
        Tuple of (icer_result, detailed_metrics)
    """
    
    # Simulate treatment costs (lognormal distribution)
    costs = np.random.lognormal(
        np.log(treatment_cost_mean) - 0.5 * (treatment_cost_std/treatment_cost_mean)**2,
        treatment_cost_std/treatment_cost_mean,
        num_simulations
    )
    
    # Simulate QALY gains (normal distribution, clipped at 0)
    qalys = np.random.normal(qaly_gain_mean, qaly_gain_std, num_simulations)
    qalys = np.clip(qalys, 0, None)
    
    # Calculate ICER (Incremental Cost-Effectiveness Ratio)
    # Avoid division by zero
    icers = np.where(qalys > 0, costs / qalys, np.inf)
    
    # Determine cost-effectiveness
    cost_effective = icers < willingness_to_pay
    probability_cost_effective = np.mean(cost_effective)
    
    detailed_metrics = {
        'costs': costs,
        'qalys': qalys,
        'icers': icers,
        'cost_effective': cost_effective,
        'probability_cost_effective': probability_cost_effective,
        'mean_cost': np.mean(costs),
        'mean_qaly': np.mean(qalys),
        'mean_icer': np.mean(icers[icers != np.inf])
    }
    
    return _calculate_statistics(icers[icers != np.inf]), detailed_metrics


def run_project_completion_simulation(
    num_simulations: int,
    tasks: List[Dict],
    correlation: float = 0.3
) -> Tuple[SimulationResult, np.ndarray]:
    """
    Project completion time Monte Carlo simulation
    
    Args:
        num_simulations: Number of simulations
        tasks: List of dicts with 'min', 'likely', 'max' time estimates
        correlation: Correlation between task durations (0-1)
        
    Returns:
        Tuple of (completion_time_result, task_durations)
    """
    
    num_tasks = len(tasks)
    task_durations = np.zeros((num_simulations, num_tasks))
    
    # Generate correlated random variables
    for i, task in enumerate(tasks):
        # Use triangular distribution (PERT)
        durations = np.random.triangular(
            task['min'],
            task['likely'],
            task['max'],
            num_simulations
        )
        task_durations[:, i] = durations
    
    # Add correlation effect
    if correlation > 0 and num_tasks > 1:
        # Generate common random factor
        common_factor = np.random.normal(0, correlation, num_simulations)
        for i in range(num_tasks):
            task_durations[:, i] *= (1 + common_factor)
            task_durations[:, i] = np.maximum(task_durations[:, i], tasks[i]['min'])
    
    # Total project duration (assuming sequential tasks)
    total_durations = np.sum(task_durations, axis=1)
    
    return _calculate_statistics(total_durations), task_durations


def _calculate_statistics(outcomes: np.ndarray) -> SimulationResult:
    """Calculate comprehensive statistics from outcomes"""
    
    # Handle infinite values
    finite_outcomes = outcomes[np.isfinite(outcomes)]
    
    if len(finite_outcomes) == 0:
        finite_outcomes = np.array([0])
    
    mean_val = np.mean(finite_outcomes)
    median_val = np.median(finite_outcomes)
    std_val = np.std(finite_outcomes)
    
    percentile_5 = np.percentile(finite_outcomes, 5)
    percentile_95 = np.percentile(finite_outcomes, 95)
    
    min_val = np.min(finite_outcomes)
    max_val = np.max(finite_outcomes)
    
    # 95% confidence interval
    ci_95 = (np.percentile(finite_outcomes, 2.5), np.percentile(finite_outcomes, 97.5))
    
    # Probability of success (assuming positive outcome is success)
    prob_success = np.mean(finite_outcomes > 0)
    
    return SimulationResult(
        outcomes=outcomes,
        mean=mean_val,
        median=median_val,
        std=std_val,
        percentile_5=percentile_5,
        percentile_95=percentile_95,
        min_value=min_val,
        max_value=max_val,
        confidence_interval_95=ci_95,
        probability_success=prob_success
    )


# ============================================================
# VISUALIZATION FUNCTIONS
# ============================================================

def plot_histogram_with_stats(result: SimulationResult, title: str, x_label: str):
    """Create interactive histogram with statistics overlay"""
    
    fig = go.Figure()
    
    # Histogram
    fig.add_trace(go.Histogram(
        x=result.outcomes,
        nbinsx=50,
        name='Frequency',
        marker_color='#667eea',
        opacity=0.7
    ))
    
    # Add vertical lines for key statistics
    fig.add_vline(x=result.mean, line_dash="dash", line_color="red", 
                  annotation_text=f"Mean: {result.mean:.2f}")
    fig.add_vline(x=result.median, line_dash="dash", line_color="green",
                  annotation_text=f"Median: {result.median:.2f}")
    fig.add_vline(x=result.percentile_5, line_dash="dot", line_color="orange",
                  annotation_text=f"5th %ile: {result.percentile_5:.2f}")
    fig.add_vline(x=result.percentile_95, line_dash="dot", line_color="orange",
                  annotation_text=f"95th %ile: {result.percentile_95:.2f}")
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title="Frequency",
        height=500,
        showlegend=True,
        template='plotly_white'
    )
    
    return fig


def plot_cumulative_distribution(result: SimulationResult, title: str, x_label: str):
    """Create cumulative distribution plot"""
    
    sorted_outcomes = np.sort(result.outcomes)
    cumulative_prob = np.arange(1, len(sorted_outcomes) + 1) / len(sorted_outcomes)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=sorted_outcomes,
        y=cumulative_prob * 100,
        mode='lines',
        name='Cumulative Probability',
        line=dict(color='#667eea', width=3)
    ))
    
    # Add confidence interval shading
    fig.add_vrect(
        x0=result.confidence_interval_95[0],
        x1=result.confidence_interval_95[1],
        fillcolor="green",
        opacity=0.2,
        annotation_text="95% CI",
        annotation_position="top left"
    )
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title="Cumulative Probability (%)",
        height=500,
        template='plotly_white'
    )
    
    return fig


def plot_portfolio_paths(paths: np.ndarray, years: int, num_paths_to_show: int = 100):
    """Plot portfolio simulation paths"""
    
    fig = go.Figure()
    
    # Show subset of paths
    indices = np.random.choice(paths.shape[0], min(num_paths_to_show, paths.shape[0]), replace=False)
    
    for i in indices:
        fig.add_trace(go.Scatter(
            x=list(range(years + 1)),
            y=paths[i, :],
            mode='lines',
            line=dict(width=0.5),
            opacity=0.3,
            showlegend=False,
            hovertemplate='Year %{x}<br>Value: $%{y:,.0f}<extra></extra>'
        ))
    
    # Add mean path
    mean_path = np.mean(paths, axis=0)
    fig.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=mean_path,
        mode='lines',
        name='Mean Path',
        line=dict(color='red', width=3)
    ))
    
    # Add percentile bands
    percentile_5 = np.percentile(paths, 5, axis=0)
    percentile_95 = np.percentile(paths, 95, axis=0)
    
    fig.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=percentile_95,
        mode='lines',
        name='95th Percentile',
        line=dict(color='green', dash='dash', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=percentile_5,
        mode='lines',
        name='5th Percentile',
        line=dict(color='orange', dash='dash', width=2)
    ))
    
    fig.update_layout(
        title='Portfolio Value Simulation Paths',
        xaxis_title='Year',
        yaxis_title='Portfolio Value ($)',
        height=600,
        template='plotly_white'
    )
    
    return fig


def plot_survival_curves(survival_data: np.ndarray, years: int):
    """Plot clinical survival curves from simulation"""
    
    fig = go.Figure()
    
    # Calculate mean and confidence intervals
    mean_survival = np.mean(survival_data, axis=0)
    percentile_25 = np.percentile(survival_data, 25, axis=0)
    percentile_75 = np.percentile(survival_data, 75, axis=0)
    percentile_5 = np.percentile(survival_data, 5, axis=0)
    percentile_95 = np.percentile(survival_data, 95, axis=0)
    
    time_points = list(range(years + 1))
    
    # Add confidence bands
    fig.add_trace(go.Scatter(
        x=time_points + time_points[::-1],
        y=list(percentile_95) + list(percentile_5[::-1]),
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='90% CI',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=time_points + time_points[::-1],
        y=list(percentile_75) + list(percentile_25[::-1]),
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='rgba(255,255,255,0)'),
        name='50% CI',
        showlegend=True
    ))
    
    # Add mean line
    fig.add_trace(go.Scatter(
        x=time_points,
        y=mean_survival,
        mode='lines+markers',
        name='Mean Survival',
        line=dict(color='#667eea', width=3)
    ))
    
    fig.update_layout(
        title='Survival Probability Over Time',
        xaxis_title='Years',
        yaxis_title='Survival Probability',
        yaxis=dict(range=[0, 1.05]),
        height=500,
        template='plotly_white'
    )
    
    return fig


def plot_cost_effectiveness_plane(costs: np.ndarray, qalys: np.ndarray, 
                                   willingness_to_pay: float):
    """Plot cost-effectiveness plane"""
    
    fig = go.Figure()
    
    # Scatter plot of simulations
    fig.add_trace(go.Scatter(
        x=qalys,
        y=costs,
        mode='markers',
        marker=dict(
            size=5,
            color=costs/qalys,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="ICER")
        ),
        name='Simulations',
        hovertemplate='QALY: %{x:.2f}<br>Cost: $%{y:,.0f}<extra></extra>'
    ))
    
    # Add willingness-to-pay threshold line
    max_qaly = np.max(qalys)
    fig.add_trace(go.Scatter(
        x=[0, max_qaly],
        y=[0, max_qaly * willingness_to_pay],
        mode='lines',
        name=f'WTP Threshold (${willingness_to_pay:,}/QALY)',
        line=dict(color='red', dash='dash', width=3)
    ))
    
    fig.update_layout(
        title='Cost-Effectiveness Plane',
        xaxis_title='QALY Gained',
        yaxis_title='Cost ($)',
        height=600,
        template='plotly_white'
    )
    
    return fig


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<div class="main-header">🎲 Monte Carlo Simulation Interactive Application</div>', 
                unsafe_allow_html=True)
    
    # Sidebar - Simulation Selection
    st.sidebar.title("⚙️ Simulation Settings")
    
    simulation_type = st.sidebar.selectbox(
        "Select Simulation Type",
        [
            "📊 Basic Distribution Sampling",
            "💰 Financial Portfolio Analysis",
            "🏥 Clinical Outcome Prediction",
            "💊 Treatment Cost-Effectiveness",
            "📅 Project Timeline Estimation"
        ]
    )
    
    st.sidebar.markdown("---")
    
    # Number of simulations (common to all)
    num_simulations = st.sidebar.slider(
        "Number of Simulations",
        min_value=1000,
        max_value=100000,
        value=10000,
        step=1000,
        help="More simulations = more accurate but slower"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 About Monte Carlo")
    st.sidebar.info(
        """
        **Monte Carlo simulation** uses random sampling to obtain numerical results for 
        problems that might be deterministically complex.
        
        **Key Features:**
        - Uses probability distributions
        - Generates many scenarios
        - Provides statistical insights
        - Quantifies uncertainty
        """
    )
    
    # ============================================================
    # SIMULATION TYPE IMPLEMENTATIONS
    # ============================================================
    
    if "📊 Basic Distribution Sampling" in simulation_type:
        run_basic_simulation(num_simulations)
    
    elif "💰 Financial Portfolio Analysis" in simulation_type:
        run_portfolio_analysis(num_simulations)
    
    elif "🏥 Clinical Outcome Prediction" in simulation_type:
        run_clinical_simulation(num_simulations)
    
    elif "💊 Treatment Cost-Effectiveness" in simulation_type:
        run_cost_effectiveness_analysis(num_simulations)
    
    elif "📅 Project Timeline Estimation" in simulation_type:
        run_project_timeline_simulation(num_simulations)


# ============================================================
# INDIVIDUAL SIMULATION PAGES
# ============================================================

def run_basic_simulation(num_simulations: int):
    """Basic distribution sampling simulation"""
    
    st.header("📊 Basic Distribution Sampling")
    
    st.markdown("""
    <div class="info-box">
    This simulation demonstrates sampling from various probability distributions.
    Useful for understanding uncertainty in single-variable scenarios.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mean = st.number_input("Mean (μ)", value=100.0, step=10.0)
    
    with col2:
        std_dev = st.number_input("Standard Deviation (σ)", value=15.0, step=5.0, min_value=0.1)
    
    with col3:
        distribution = st.selectbox(
            "Distribution Type",
            ["normal", "lognormal", "uniform"]
        )
    
    if st.button("🎲 Run Simulation", key="basic_sim"):
        with st.spinner("Running simulation..."):
            progress_bar = st.progress(0)
            
            # Run simulation
            result = run_monte_carlo_basic(num_simulations, mean, std_dev, distribution)
            
            progress_bar.progress(100)
            time.sleep(0.5)
            progress_bar.empty()
        
        # Display results
        st.success("✅ Simulation Complete!")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mean", f"{result.mean:.2f}")
        col2.metric("Median", f"{result.median:.2f}")
        col3.metric("Std Dev", f"{result.std:.2f}")
        col4.metric("Range", f"{result.min_value:.2f} - {result.max_value:.2f}")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = plot_histogram_with_stats(result, "Distribution of Outcomes", "Value")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = plot_cumulative_distribution(result, "Cumulative Distribution", "Value")
            st.plotly_chart(fig2, use_container_width=True)
        
        # Statistics table
        st.subheader("📈 Detailed Statistics")
        stats_df = pd.DataFrame({
            'Statistic': ['Mean', 'Median', 'Std Dev', 'Min', 'Max', '5th Percentile', 
                         '95th Percentile', '95% CI Lower', '95% CI Upper'],
            'Value': [result.mean, result.median, result.std, result.min_value, result.max_value,
                     result.percentile_5, result.percentile_95, 
                     result.confidence_interval_95[0], result.confidence_interval_95[1]]
        })
        st.dataframe(stats_df, use_container_width=True)


def run_portfolio_analysis(num_simulations: int):
    """Financial portfolio Monte Carlo simulation"""
    
    st.header("💰 Financial Portfolio Analysis")
    
    st.markdown("""
    <div class="info-box">
    Simulates investment portfolio growth using Geometric Brownian Motion.
    Models stock market volatility and long-term returns.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        initial_investment = st.number_input("Initial Investment ($)", value=100000.0, step=10000.0)
    
    with col2:
        expected_return = st.slider("Expected Annual Return (%)", 0.0, 20.0, 7.0, 0.5) / 100
    
    with col3:
        volatility = st.slider("Annual Volatility (%)", 0.0, 50.0, 15.0, 1.0) / 100
    
    with col4:
        years = st.slider("Investment Period (Years)", 1, 40, 20, 1)
    
    if st.button("💰 Run Portfolio Simulation", key="portfolio_sim"):
        with st.spinner("Simulating portfolio growth..."):
            progress_bar = st.progress(0)
            
            result, paths = run_portfolio_simulation(
                num_simulations, initial_investment, expected_return, volatility, years
            )
            
            progress_bar.progress(100)
            time.sleep(0.5)
            progress_bar.empty()
        
        st.success("✅ Portfolio Simulation Complete!")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric(
            "Expected Final Value", 
            f"${result.mean:,.0f}",
            f"{((result.mean - initial_investment)/initial_investment * 100):.1f}%"
        )
        col2.metric("Median Value", f"${result.median:,.0f}")
        col3.metric("Best Case (95th)", f"${result.percentile_95:,.0f}")
        col4.metric("Worst Case (5th)", f"${result.percentile_5:,.0f}")
        
        # Portfolio paths visualization
        st.subheader("📈 Portfolio Growth Paths")
        fig_paths = plot_portfolio_paths(paths, years, num_paths_to_show=200)
        st.plotly_chart(fig_paths, use_container_width=True)
        
        # Distribution of final values
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = plot_histogram_with_stats(result, "Distribution of Final Values", "Portfolio Value ($)")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = plot_cumulative_distribution(result, "Probability of Achieving Value", "Portfolio Value ($)")
            st.plotly_chart(fig2, use_container_width=True)
        
        # Risk analysis
        st.subheader("⚠️ Risk Analysis")
        
        prob_loss = np.mean(result.outcomes < initial_investment) * 100
        prob_double = np.mean(result.outcomes > initial_investment * 2) * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Probability of Loss", f"{prob_loss:.1f}%")
        col2.metric("Probability of Doubling", f"{prob_double:.1f}%")
        col3.metric("95% Confidence Interval", 
                   f"${result.confidence_interval_95[0]:,.0f} - ${result.confidence_interval_95[1]:,.0f}")


def run_clinical_simulation(num_simulations: int):
    """Clinical outcome Monte Carlo simulation"""
    
    st.header("🏥 Clinical Outcome Prediction")
    
    st.markdown("""
    <div class="info-box">
    Simulates patient outcomes for medical treatments considering individual variability.
    Useful for clinical trial design and treatment planning.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        base_success_rate = st.slider("Baseline Success Rate (%)", 0, 100, 70, 5) / 100
    
    with col2:
        treatment_effect = st.slider("Treatment Benefit (%)", 0, 30, 10, 1) / 100
    
    with col3:
        patient_variability = st.slider("Patient Variability (σ)", 0.0, 0.5, 0.15, 0.05)
    
    with col4:
        follow_up_years = st.slider("Follow-up Period (Years)", 1, 10, 5, 1)
    
    if st.button("🏥 Run Clinical Simulation", key="clinical_sim"):
        with st.spinner("Simulating patient outcomes..."):
            progress_bar = st.progress(0)
            
            result, detailed = run_clinical_outcome_simulation(
                num_simulations, base_success_rate, treatment_effect, 
                patient_variability, follow_up_years
            )
            
            progress_bar.progress(100)
            time.sleep(0.5)
            progress_bar.empty()
        
        st.success("✅ Clinical Simulation Complete!")
        
        # Key outcomes
        col1, col2, col3, col4 = st.columns(4)
        
        final_survival_rate = np.mean(detailed['final_survival']) * 100
        
        col1.metric("Final Survival Rate", f"{final_survival_rate:.1f}%")
        col2.metric("Expected Success Rate", f"{(base_success_rate + treatment_effect) * 100:.1f}%")
        col3.metric("Range (5th-95th)", 
                   f"{np.percentile(detailed['patient_rates'], 5)*100:.1f}% - {np.percentile(detailed['patient_rates'], 95)*100:.1f}%")
        col4.metric("Number of Simulated Patients", f"{num_simulations:,}")
        
        # Survival curves
        st.subheader("📊 Survival Analysis")
        fig_survival = plot_survival_curves(detailed['survival_curves'], follow_up_years)
        st.plotly_chart(fig_survival, use_container_width=True)
        
        # Distribution visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Patient success rate distribution
            patient_result = SimulationResult(
                outcomes=detailed['patient_rates'],
                mean=np.mean(detailed['patient_rates']),
                median=np.median(detailed['patient_rates']),
                std=np.std(detailed['patient_rates']),
                percentile_5=np.percentile(detailed['patient_rates'], 5),
                percentile_95=np.percentile(detailed['patient_rates'], 95),
                min_value=np.min(detailed['patient_rates']),
                max_value=np.max(detailed['patient_rates']),
                confidence_interval_95=(np.percentile(detailed['patient_rates'], 2.5),
                                       np.percentile(detailed['patient_rates'], 97.5)),
                probability_success=0.0
            )
            
            fig1 = plot_histogram_with_stats(patient_result, 
                                            "Distribution of Patient Success Rates", 
                                            "Success Probability")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = plot_cumulative_distribution(patient_result,
                                               "Cumulative Success Probability",
                                               "Success Rate")
            st.plotly_chart(fig2, use_container_width=True)
        
        # Clinical insights
        st.subheader("💡 Clinical Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="success-box">
            <h4>Positive Findings</h4>
            """, unsafe_allow_html=True)
            
            prob_above_90 = np.mean(detailed['patient_rates'] > 0.90) * 100
            prob_above_80 = np.mean(detailed['patient_rates'] > 0.80) * 100
            
            st.write(f"- {prob_above_90:.1f}% of patients expected to have >90% success rate")
            st.write(f"- {prob_above_80:.1f}% of patients expected to have >80% success rate")
            st.write(f"- Mean treatment effect: {treatment_effect * 100:.1f}% absolute benefit")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="warning-box">
            <h4>Risk Factors</h4>
            """, unsafe_allow_html=True)
            
            prob_below_50 = np.mean(detailed['patient_rates'] < 0.50) * 100
            prob_below_60 = np.mean(detailed['patient_rates'] < 0.60) * 100
            
            st.write(f"- {prob_below_50:.1f}% of patients may have <50% success rate")
            st.write(f"- {prob_below_60:.1f}% of patients may have <60% success rate")
            st.write(f"- Patient variability (σ): {patient_variability:.2f}")
            st.markdown("</div>", unsafe_allow_html=True)


def run_cost_effectiveness_analysis(num_simulations: int):
    """Treatment cost-effectiveness Monte Carlo simulation"""
    
    st.header("💊 Treatment Cost-Effectiveness Analysis")
    
    st.markdown("""
    <div class="info-box">
    Analyzes cost-effectiveness using ICER (Incremental Cost-Effectiveness Ratio) and 
    QALY (Quality-Adjusted Life Years). Standard method for health economics evaluation.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Cost Parameters")
        treatment_cost_mean = st.number_input("Mean Treatment Cost ($)", value=50000.0, step=5000.0)
        treatment_cost_std = st.number_input("Cost Std Dev ($)", value=10000.0, step=1000.0)
    
    with col2:
        st.subheader("🏥 Health Outcome Parameters")
        qaly_gain_mean = st.number_input("Mean QALY Gain", value=2.5, step=0.5, min_value=0.0)
        qaly_gain_std = st.number_input("QALY Std Dev", value=0.8, step=0.1, min_value=0.1)
    
    willingness_to_pay = st.slider(
        "Willingness-to-Pay Threshold ($/QALY)",
        10000, 150000, 50000, 10000,
        help="Common thresholds: $50k-$100k per QALY in US, £20k-£30k in UK"
    )
    
    if st.button("💊 Run Cost-Effectiveness Analysis", key="ce_sim"):
        with st.spinner("Analyzing cost-effectiveness..."):
            progress_bar = st.progress(0)
            
            result, detailed = run_treatment_cost_effectiveness(
                num_simulations, treatment_cost_mean, treatment_cost_std,
                qaly_gain_mean, qaly_gain_std, willingness_to_pay
            )
            
            progress_bar.progress(100)
            time.sleep(0.5)
            progress_bar.empty()
        
        st.success("✅ Cost-Effectiveness Analysis Complete!")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Mean ICER", f"${detailed['mean_icer']:,.0f}/QALY")
        col2.metric("Mean Cost", f"${detailed['mean_cost']:,.0f}")
        col3.metric("Mean QALY Gain", f"{detailed['mean_qaly']:.2f}")
        col4.metric("Probability Cost-Effective", 
                   f"{detailed['probability_cost_effective'] * 100:.1f}%")
        
        # Decision
        if detailed['probability_cost_effective'] > 0.5:
            st.markdown("""
            <div class="success-box">
            <h3>✅ LIKELY COST-EFFECTIVE</h3>
            <p>The treatment has a >50% probability of being cost-effective at the specified 
            willingness-to-pay threshold.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box">
            <h3>⚠️ MAY NOT BE COST-EFFECTIVE</h3>
            <p>The treatment has a <50% probability of being cost-effective at the specified 
            willingness-to-pay threshold.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Cost-effectiveness plane
        st.subheader("📊 Cost-Effectiveness Plane")
        fig_ce = plot_cost_effectiveness_plane(
            detailed['costs'], detailed['qalys'], willingness_to_pay
        )
        st.plotly_chart(fig_ce, use_container_width=True)
        
        # Distributions
        col1, col2 = st.columns(2)
        
        with col1:
            # Cost distribution
            cost_result = SimulationResult(
                outcomes=detailed['costs'],
                mean=detailed['mean_cost'],
                median=np.median(detailed['costs']),
                std=np.std(detailed['costs']),
                percentile_5=np.percentile(detailed['costs'], 5),
                percentile_95=np.percentile(detailed['costs'], 95),
                min_value=np.min(detailed['costs']),
                max_value=np.max(detailed['costs']),
                confidence_interval_95=(np.percentile(detailed['costs'], 2.5),
                                       np.percentile(detailed['costs'], 97.5)),
                probability_success=0.0
            )
            
            fig1 = plot_histogram_with_stats(cost_result, "Treatment Cost Distribution", "Cost ($)")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # QALY distribution
            qaly_result = SimulationResult(
                outcomes=detailed['qalys'],
                mean=detailed['mean_qaly'],
                median=np.median(detailed['qalys']),
                std=np.std(detailed['qalys']),
                percentile_5=np.percentile(detailed['qalys'], 5),
                percentile_95=np.percentile(detailed['qalys'], 95),
                min_value=np.min(detailed['qalys']),
                max_value=np.max(detailed['qalys']),
                confidence_interval_95=(np.percentile(detailed['qalys'], 2.5),
                                       np.percentile(detailed['qalys'], 97.5)),
                probability_success=0.0
            )
            
            fig2 = plot_histogram_with_stats(qaly_result, "QALY Gain Distribution", "QALY")
            st.plotly_chart(fig2, use_container_width=True)
        
        # Sensitivity analysis
        st.subheader("🔍 Sensitivity Analysis")
        
        wtp_range = np.linspace(10000, 200000, 20)
        prob_ce_at_wtp = []
        
        for wtp in wtp_range:
            ce = detailed['icers'] < wtp
            prob_ce_at_wtp.append(np.mean(ce) * 100)
        
        fig_sens = go.Figure()
        fig_sens.add_trace(go.Scatter(
            x=wtp_range,
            y=prob_ce_at_wtp,
            mode='lines+markers',
            name='Probability Cost-Effective',
            line=dict(color='#667eea', width=3)
        ))
        
        fig_sens.add_vline(x=willingness_to_pay, line_dash="dash", line_color="red",
                          annotation_text=f"Current WTP: ${willingness_to_pay:,}")
        
        fig_sens.update_layout(
            title='Cost-Effectiveness Acceptability Curve',
            xaxis_title='Willingness-to-Pay ($/QALY)',
            yaxis_title='Probability Cost-Effective (%)',
            height=500,
            template='plotly_white'
        )
        
        st.plotly_chart(fig_sens, use_container_width=True)


def run_project_timeline_simulation(num_simulations: int):
    """Project completion timeline Monte Carlo simulation"""
    
    st.header("📅 Project Timeline Estimation")
    
    st.markdown("""
    <div class="info-box">
    Uses triangular distribution (PERT) for task duration estimation with optional 
    correlation between tasks. Useful for project management and planning.
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📋 Task Configuration")
    
    num_tasks = st.number_input("Number of Tasks", min_value=2, max_value=20, value=5, step=1)
    
    correlation = st.slider(
        "Task Correlation Factor",
        0.0, 1.0, 0.3, 0.05,
        help="0 = independent tasks, 1 = highly correlated"
    )
    
    st.markdown("### 📝 Define Tasks")
    st.markdown("*Enter minimum, most likely, and maximum duration (in days) for each task*")
    
    tasks = []
    
    for i in range(num_tasks):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            task_name = st.text_input(f"Task {i+1} Name", value=f"Task {i+1}", key=f"task_name_{i}")
        
        with col2:
            min_days = st.number_input(f"Min", value=5.0, step=1.0, key=f"min_{i}", min_value=1.0)
        
        with col3:
            likely_days = st.number_input(f"Likely", value=10.0, step=1.0, key=f"likely_{i}", 
                                         min_value=min_days)
        
        with col4:
            max_days = st.number_input(f"Max", value=20.0, step=1.0, key=f"max_{i}", 
                                      min_value=likely_days)
        
        tasks.append({
            'name': task_name,
            'min': min_days,
            'likely': likely_days,
            'max': max_days
        })
    
    if st.button("📅 Run Project Simulation", key="project_sim"):
        with st.spinner("Simulating project completion times..."):
            progress_bar = st.progress(0)
            
            result, task_durations = run_project_completion_simulation(
                num_simulations, tasks, correlation
            )
            
            progress_bar.progress(100)
            time.sleep(0.5)
            progress_bar.empty()
        
        st.success("✅ Project Simulation Complete!")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Mean Duration", f"{result.mean:.1f} days")
        col2.metric("Median Duration", f"{result.median:.1f} days")
        col3.metric("90% Confidence", f"{result.percentile_5:.1f} - {result.percentile_95:.1f} days")
        col4.metric("Range", f"{result.min_value:.1f} - {result.max_value:.1f} days")
        
        # Project duration distribution
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = plot_histogram_with_stats(result, "Project Completion Time Distribution", 
                                            "Duration (days)")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = plot_cumulative_distribution(result, 
                                               "Probability of Completing by Date",
                                               "Duration (days)")
            st.plotly_chart(fig2, use_container_width=True)
        
        # Task analysis
        st.subheader("📊 Task-by-Task Analysis")
        
        task_stats = []
        for i, task in enumerate(tasks):
            task_stats.append({
                'Task': task['name'],
                'Mean Duration': f"{np.mean(task_durations[:, i]):.1f}",
                'Std Dev': f"{np.std(task_durations[:, i]):.1f}",
                'Min': f"{task['min']:.1f}",
                'Likely': f"{task['likely']:.1f}",
                'Max': f"{task['max']:.1f}",
                '% of Total Time': f"{(np.mean(task_durations[:, i]) / result.mean * 100):.1f}%"
            })
        
        st.dataframe(pd.DataFrame(task_stats), use_container_width=True)
        
        # Task duration box plot
        fig_box = go.Figure()
        
        for i, task in enumerate(tasks):
            fig_box.add_trace(go.Box(
                y=task_durations[:, i],
                name=task['name'],
                boxmean='sd'
            ))
        
        fig_box.update_layout(
            title='Task Duration Distributions',
            yaxis_title='Duration (days)',
            height=500,
            template='plotly_white',
            showlegend=True
        )
        
        st.plotly_chart(fig_box, use_container_width=True)
        
        # Recommendations
        st.subheader("💡 Project Management Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="success-box">
            <h4>Timeline Recommendations</h4>
            """, unsafe_allow_html=True)
            
            st.write(f"- **Target Completion:** {result.percentile_95:.0f} days (95% confidence)")
            st.write(f"- **Aggressive Timeline:** {result.median:.0f} days (50% confidence)")
            st.write(f"- **Buffer Required:** {(result.percentile_95 - result.median):.0f} days")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="warning-box">
            <h4>Risk Factors</h4>
            """, unsafe_allow_html=True)
            
            prob_overrun_50 = np.mean(result.outcomes > (result.median * 1.5)) * 100
            prob_overrun_30 = np.mean(result.outcomes > (result.median * 1.3)) * 100
            
            st.write(f"- {prob_overrun_30:.1f}% chance of >30% overrun")
            st.write(f"- {prob_overrun_50:.1f}% chance of >50% overrun")
            st.write(f"- Correlation effect: {correlation:.0%} task dependency")
            
            st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    main()
