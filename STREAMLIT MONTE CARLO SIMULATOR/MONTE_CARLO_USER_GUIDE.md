# 🎲 MONTE CARLO SIMULATION - STREAMLIT APPLICATION
## Complete Installation & User Guide

**Version:** 1.0.0  
**Date:** 2025-01-27  
**Author:** ACR Development Team

---

## 📋 TABLE OF CONTENTS

1. [Quick Start (5 Minutes)](#quick-start)
2. [Installation Guide](#installation)
3. [Application Overview](#overview)
4. [Simulation Types Explained](#simulation-types)
5. [Step-by-Step Usage](#usage)
6. [Interpretation Guide](#interpretation)
7. [Advanced Features](#advanced)
8. [Troubleshooting](#troubleshooting)
9. [Real-World Examples](#examples)

---

## ⚡ QUICK START (5 MINUTES) {#quick-start}

### Step 1: Install Dependencies
```bash
pip install streamlit numpy pandas plotly scipy
```

### Step 2: Download Application
Download `monte_carlo_streamlit_app.py`

### Step 3: Run Application
```bash
streamlit run monte_carlo_streamlit_app.py
```

### Step 4: Open Browser
Automatic: Browser opens to `http://localhost:8501`  
Manual: Navigate to the URL shown in terminal

### Step 5: Start Simulating!
1. Select simulation type from sidebar
2. Adjust parameters
3. Click "Run Simulation" button
4. View interactive results

**That's it! You're ready to go!** 🚀

---

## 💿 INSTALLATION GUIDE {#installation}

### Prerequisites

**Required:**
- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for initial installation)

**System Requirements:**
- RAM: 4GB minimum, 8GB recommended
- Storage: 500MB for packages
- OS: Windows, macOS, or Linux

### Installation Methods

#### Method 1: Quick Install (Recommended)

```bash
# Create requirements file
cat > requirements.txt << EOF
streamlit>=1.30.0
numpy>=1.24.0
pandas>=2.0.0
plotly>=5.18.0
scipy>=1.11.0
EOF

# Install all dependencies
pip install -r requirements.txt

# Verify installation
python -c "import streamlit, numpy, pandas, plotly, scipy; print('✓ All packages installed')"
```

#### Method 2: Individual Package Installation

```bash
pip install streamlit
pip install numpy
pip install pandas
pip install plotly
pip install scipy
```

#### Method 3: Virtual Environment (Best Practice)

```bash
# Create virtual environment
python -m venv monte_carlo_env

# Activate (macOS/Linux)
source monte_carlo_env/bin/activate

# Activate (Windows)
monte_carlo_env\Scripts\activate

# Install packages
pip install streamlit numpy pandas plotly scipy

# Run application
streamlit run monte_carlo_streamlit_app.py
```

### Verification

```bash
# Test Streamlit
streamlit hello

# Should open browser with Streamlit demo

# Test Python packages
python -c "import streamlit as st; print(f'Streamlit version: {st.__version__}')"
python -c "import numpy as np; print(f'NumPy version: {np.__version__}')"
python -c "import pandas as pd; print(f'Pandas version: {pd.__version__}')"
python -c "import plotly; print(f'Plotly version: {plotly.__version__}')"
python -c "import scipy; print(f'SciPy version: {scipy.__version__}')"
```

---

## 🎯 APPLICATION OVERVIEW {#overview}

### What is Monte Carlo Simulation?

**Monte Carlo simulation** is a computational algorithm that uses **random sampling** to obtain numerical results for problems that might be deterministically complex or impossible to solve analytically.

**Key Concepts:**
- **Random Sampling:** Generate thousands/millions of scenarios using probability distributions
- **Statistical Analysis:** Analyze the distribution of possible outcomes
- **Risk Quantification:** Understand uncertainty and probability of different results
- **Decision Support:** Make informed decisions based on probabilistic outcomes

### Why Use This Application?

**For Healthcare:**
- ✅ Predict clinical trial outcomes
- ✅ Assess treatment cost-effectiveness
- ✅ Model patient survival curves
- ✅ Estimate healthcare resource needs

**For Finance:**
- ✅ Portfolio risk analysis
- ✅ Investment return forecasting
- ✅ Option pricing
- ✅ Risk management

**For Project Management:**
- ✅ Timeline estimation
- ✅ Budget forecasting
- ✅ Resource allocation
- ✅ Risk assessment

**For Research:**
- ✅ Uncertainty quantification
- ✅ Sensitivity analysis
- ✅ Hypothesis testing
- ✅ Model validation

---

## 🔬 SIMULATION TYPES EXPLAINED {#simulation-types}

### 1. 📊 Basic Distribution Sampling

**Purpose:** Understand single-variable uncertainty  
**Use Cases:**
- Testing measurement uncertainty
- Understanding variability in processes
- Educational demonstrations

**Key Parameters:**
- **Mean (μ):** Average expected value
- **Standard Deviation (σ):** Amount of variation
- **Distribution Type:** 
  - *Normal:* Symmetric, bell curve (most natural phenomena)
  - *Lognormal:* Right-skewed (stock prices, income)
  - *Uniform:* Equal probability across range

**Example:**  
*"What's the distribution of patient wait times if average is 45 minutes with 10-minute variation?"*

---

### 2. 💰 Financial Portfolio Analysis

**Purpose:** Model investment growth with market volatility  
**Mathematical Model:** Geometric Brownian Motion

**Formula:**
```
dS = μS dt + σS dW
```
Where:
- S = Stock price
- μ = Expected return (drift)
- σ = Volatility
- dW = Random Brownian motion

**Key Parameters:**
- **Initial Investment:** Starting capital
- **Expected Annual Return:** Historical average (e.g., S&P 500 = 7-10%)
- **Annual Volatility:** Market fluctuation (typical: 15-20%)
- **Investment Period:** Time horizon in years

**Outputs:**
- Distribution of final portfolio values
- Probability of loss
- Probability of doubling investment
- 95% confidence intervals
- Best/worst case scenarios

**Example:**  
*"If I invest $100,000 at 7% return with 15% volatility, what's my expected value in 20 years?"*

**Typical Results:**
- Mean: $387,000
- Median: $345,000
- 95th percentile: $680,000
- 5th percentile: $180,000
- Probability of loss: 5%

---

### 3. 🏥 Clinical Outcome Prediction

**Purpose:** Model patient treatment outcomes with individual variability

**Medical Context:**
- Simulates thousands of "virtual patients"
- Each patient has individual success probability
- Tracks outcomes over multiple years
- Accounts for treatment effects and variability

**Key Parameters:**
- **Baseline Success Rate:** Natural disease outcome (0-100%)
- **Treatment Benefit:** Additional benefit from intervention (0-30%)
- **Patient Variability (σ):** Individual differences (0.0-0.5)
- **Follow-up Years:** Duration of observation (1-10 years)

**Outputs:**
- Survival curves over time
- Final survival/success rates
- Distribution of patient outcomes
- Confidence intervals
- Probability bands

**Example - Breast Cancer Treatment:**
```
Input:
- Baseline survival: 70%
- Treatment benefit: 10%
- Patient variability: 0.15
- Follow-up: 5 years

Results:
- 5-year survival: 78.5% (mean)
- Range: 62% - 92% (5th-95th percentile)
- 90% of patients: >65% success
```

**Clinical Interpretation:**
- Treatment provides significant benefit
- Most patients respond well
- Some patient variability expected
- Plan for close monitoring of lower-responding patients

---

### 4. 💊 Treatment Cost-Effectiveness Analysis

**Purpose:** Evaluate if treatment provides value for money

**Health Economics Framework:**

**ICER = (Cost_Treatment - Cost_Control) / (QALY_Treatment - QALY_Control)**

Where:
- **ICER:** Incremental Cost-Effectiveness Ratio ($/QALY)
- **QALY:** Quality-Adjusted Life Year (1 QALY = 1 year perfect health)
- **Willingness-to-Pay (WTP):** Maximum acceptable cost per QALY

**Common WTP Thresholds:**
- US: $50,000 - $150,000 per QALY
- UK (NICE): £20,000 - £30,000 per QALY
- WHO: 1-3× GDP per capita

**Key Parameters:**
- **Treatment Cost:** Mean and variability (lognormal distribution)
- **QALY Gain:** Health benefit in quality-adjusted life years
- **WTP Threshold:** Decision-making criterion

**Outputs:**
- Mean ICER
- Probability cost-effective
- Cost-effectiveness plane (scatter plot)
- Cost-effectiveness acceptability curve
- Sensitivity to WTP threshold

**Example - New Cancer Drug:**
```
Input:
- Mean cost: $75,000 (σ = $15,000)
- Mean QALY gain: 2.5 years (σ = 0.8)
- WTP: $100,000/QALY

Results:
- Mean ICER: $30,000/QALY
- Probability cost-effective: 87%
- Recommendation: LIKELY COST-EFFECTIVE
```

**Decision Framework:**
- ICER < WTP → Cost-effective
- ICER > WTP → Not cost-effective
- Probability > 50% → Acceptable uncertainty

---

### 5. 📅 Project Timeline Estimation

**Purpose:** Forecast project completion with task uncertainty

**Methodology:** PERT (Program Evaluation and Review Technique)

**Triangular Distribution:**
```
Each task has:
- Minimum time (optimistic)
- Most likely time (realistic)
- Maximum time (pessimistic)
```

**Key Parameters:**
- **Number of Tasks:** Project complexity
- **Task Correlation:** How tasks affect each other (0-1)
  - 0 = Independent tasks
  - 1 = Highly correlated (team-wide issues)
- **Task Estimates:** Min, likely, max for each task

**Outputs:**
- Total project duration distribution
- Task-by-task analysis
- Critical path identification
- Buffer recommendations
- Risk of schedule overrun

**Example - Software Development:**
```
Tasks:
1. Design: 5-10-20 days
2. Backend: 10-15-25 days
3. Frontend: 8-12-20 days
4. Testing: 5-8-15 days
5. Deployment: 2-3-5 days

Correlation: 0.3 (moderate)

Results:
- Mean duration: 52 days
- 50% confidence: 48 days
- 95% confidence: 68 days
- Recommended timeline: 70 days (with buffer)
- Probability 30% overrun: 12%
```

**Project Management Insights:**
- Set deadlines at 80-95th percentile
- Include explicit buffers
- Monitor high-variance tasks
- Plan contingencies for correlated risks

---

## 📖 STEP-BY-STEP USAGE GUIDE {#usage}

### General Workflow

1. **Launch Application**
   ```bash
   streamlit run monte_carlo_streamlit_app.py
   ```

2. **Select Simulation Type**
   - Use sidebar dropdown
   - Choose appropriate simulation for your problem

3. **Set Parameters**
   - Use sliders for continuous values
   - Use number inputs for precise values
   - Use dropdowns for categorical choices

4. **Run Simulation**
   - Click the simulation button
   - Watch progress bar
   - Wait for completion (1-10 seconds typically)

5. **Analyze Results**
   - Review key metrics
   - Examine distributions
   - Study visualizations
   - Read insights

6. **Export/Share**
   - Screenshot results
   - Download data (if needed)
   - Share findings

### Detailed Example: Clinical Outcome Simulation

#### Step 1: Select Simulation
- Sidebar → "🏥 Clinical Outcome Prediction"

#### Step 2: Configure Parameters
```
Baseline Success Rate: 70%
Treatment Benefit: 10%
Patient Variability: 0.15
Follow-up Period: 5 years
Number of Simulations: 10,000
```

#### Step 3: Run Simulation
- Click "🏥 Run Clinical Simulation"
- Progress bar shows completion

#### Step 4: Interpret Results

**Metrics Display:**
```
Final Survival Rate: 78.5%
Expected Success Rate: 80%
Range (5th-95th): 62% - 92%
Number of Simulated Patients: 10,000
```

**What this means:**
- ✅ Treatment effective (78.5% > 70% baseline)
- ✅ Close to expected (78.5% ≈ 80%)
- ⚠️ Wide range (30% spread) indicates variability
- ✅ Large sample (10,000) provides confidence

**Survival Curves:**
- Shows probability over time
- Confidence bands indicate uncertainty
- Downward trend shows attrition
- Plateaus indicate stabilization

**Distribution Plots:**
- Histogram: Shows frequency of outcomes
- Cumulative: Shows probability thresholds
- Use to answer: "What % of patients have >X% success?"

#### Step 5: Clinical Decision

**If Results Show:**
- High mean survival (>75%) → Treatment recommended
- Narrow confidence bands → Predictable outcomes
- Wide confidence bands → Need patient stratification

**Action Items:**
- Document findings
- Present to clinical team
- Discuss patient selection criteria
- Plan monitoring strategy

---

## 📊 INTERPRETATION GUIDE {#interpretation}

### Understanding Statistics

#### Mean vs Median
- **Mean:** Average of all outcomes
  - Sensitive to extreme values
  - Use for: Expected value calculations

- **Median:** Middle value (50th percentile)
  - Resistant to outliers
  - Use for: Typical outcome

**When they differ:**
- Mean > Median → Right-skewed (positive outliers)
- Mean < Median → Left-skewed (negative outliers)
- Mean ≈ Median → Symmetric distribution

#### Standard Deviation (σ)
- Measures spread/dispersion
- **Low σ:** Predictable, consistent
- **High σ:** Variable, uncertain

**Rules of thumb:**
- 68% of values within ±1σ of mean
- 95% of values within ±2σ of mean
- 99.7% of values within ±3σ of mean

#### Percentiles
- **5th percentile:** Worst-case scenario (95% of outcomes better)
- **50th percentile:** Median, typical outcome
- **95th percentile:** Best-case scenario (95% of outcomes worse)

**Usage:**
- Conservative planning: Use 5th percentile
- Realistic planning: Use 50th percentile (median)
- Optimistic planning: Use 95th percentile

#### Confidence Intervals
- **95% CI:** Range containing 95% of outcomes
- Narrower → More certain
- Wider → More uncertain

**Example:**
```
95% CI: [$180,000 - $680,000]
Interpretation: 95% probability final value in this range
```

### Reading Visualizations

#### Histogram
- **X-axis:** Outcome value
- **Y-axis:** Frequency/count
- **Peak:** Most common outcome
- **Spread:** Variability
- **Tails:** Extreme outcomes

**Look for:**
- Symmetry vs skewness
- Single peak vs multiple peaks
- Outliers (isolated bars)

#### Cumulative Distribution
- **X-axis:** Outcome value
- **Y-axis:** Cumulative probability (%)
- **Curve:** S-shaped typically

**How to use:**
1. Pick outcome value on X-axis
2. Read up to curve
3. Read across to Y-axis
4. This is probability of getting ≤ that value

**Example:**
"What's probability portfolio > $500,000?"
- Find $500,000 on X-axis
- Read cumulative probability (e.g., 70%)
- Probability > $500k = 100% - 70% = 30%

#### Box Plot
- **Box:** 25th to 75th percentile (middle 50%)
- **Line in box:** Median
- **Whiskers:** Extend to min/max (or 1.5× IQR)
- **Dots:** Outliers

**Interpretation:**
- Larger box → More variability
- Asymmetric box → Skewed distribution
- Many outliers → Heavy tails

---

## 🚀 ADVANCED FEATURES {#advanced}

### 1. Adjusting Number of Simulations

**Trade-offs:**
```
1,000 simulations:
✓ Fast (< 1 second)
✗ Less accurate
✗ Noisy results

10,000 simulations:
✓ Good accuracy
✓ Reasonable speed (~1-2 seconds)
✓ Smooth distributions

100,000 simulations:
✓ Very accurate
✓ Smooth distributions
✗ Slower (5-10 seconds)
```

**Recommendation:** Use 10,000 for most cases

### 2. Distribution Selection

**Normal Distribution:**
- Use when: Natural variation, measurement error
- Examples: Heights, test scores, manufacturing tolerances
- Characteristics: Symmetric, bell-shaped

**Lognormal Distribution:**
- Use when: Cannot be negative, right-skewed
- Examples: Income, stock prices, medical costs
- Characteristics: Always positive, long right tail

**Uniform Distribution:**
- Use when: All outcomes equally likely
- Examples: Random number generation, initial modeling
- Characteristics: Flat probability across range

### 3. Correlation in Project Timelines

**Understanding Correlation:**
- **0.0:** Tasks completely independent
  - Team members work isolated
  - No shared resources
  - Different skill sets

- **0.3:** Moderate correlation (typical)
  - Some shared resources
  - Common blockers affect multiple tasks
  - Realistic for most projects

- **0.7:** High correlation
  - Shared team members
  - Dependencies on common systems
  - Company-wide issues affect all tasks

- **1.0:** Perfect correlation
  - All tasks affected identically
  - Unrealistic, avoid using

**Impact on Results:**
- Higher correlation → Wider distribution
- Higher correlation → Higher risk of major delays
- Lower correlation → Tasks compensate for each other

### 4. Sensitivity Analysis

**What-If Analysis:**
1. Run baseline simulation
2. Change ONE parameter
3. Run again
4. Compare results
5. Identify sensitive parameters

**Example - Portfolio:**
```
Baseline: 7% return, 15% volatility → Mean: $387k

Sensitivity test:
- 8% return → Mean: $466k (+20% impact)
- 20% volatility → Mean: $375k (-3% impact)

Conclusion: Return more important than volatility
```

### 5. Customization Tips

**Modify Application:**
```python
# Change color scheme
line=dict(color='#YOUR_COLOR', width=3)

# Adjust number of simulation range
max_value=200000  # Allow up to 200k simulations

# Add custom distributions
from scipy.stats import beta
outcomes = beta.rvs(a, b, size=num_simulations)
```

---

## 🔧 TROUBLESHOOTING {#troubleshooting}

### Common Issues

#### 1. "Module not found" Error
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
```bash
pip install streamlit numpy pandas plotly scipy
```

#### 2. Port Already in Use
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Kill existing Streamlit process
pkill -f streamlit

# Or use different port
streamlit run monte_carlo_streamlit_app.py --server.port 8502
```

#### 3. Browser Doesn't Open
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

**Solution:**
Manually open browser and navigate to `http://localhost:8501`

#### 4. Slow Performance
```
Simulation taking > 30 seconds
```

**Solutions:**
- Reduce number of simulations (e.g., 5,000 instead of 100,000)
- Close other applications
- Use faster computer
- Check memory usage

#### 5. "Invalid Value" Warnings
```
RuntimeWarning: divide by zero encountered
```

**Cause:** Division by zero in ICER calculation (QALY = 0)

**Solution:** Already handled in code (filters infinite values)

#### 6. Visualization Not Displaying
**Check:**
- Plotly installed: `pip list | grep plotly`
- Browser JavaScript enabled
- Try different browser (Chrome recommended)

### Getting Help

**Resources:**
- Streamlit docs: https://docs.streamlit.io
- Plotly docs: https://plotly.com/python/
- NumPy docs: https://numpy.org/doc/
- SciPy docs: https://docs.scipy.org/

**Support:**
- Create GitHub issue (if available)
- Check Stack Overflow: [streamlit] or [monte-carlo]
- Streamlit community forum

---

## 💡 REAL-WORLD EXAMPLES {#examples}

### Example 1: Healthcare - Clinical Trial Design

**Scenario:**  
Planning Phase III trial for new breast cancer treatment

**Simulation Setup:**
```
Type: Clinical Outcome Prediction
Baseline Success: 65% (standard treatment 5-year survival)
Treatment Benefit: 12% (expected improvement)
Patient Variability: 0.18 (heterogeneous population)
Follow-up: 5 years
Simulations: 50,000 (large trial simulation)
```

**Results:**
```
5-Year Survival: 75.3% (95% CI: 72.1% - 78.5%)
Probability >70% survival: 89%
Recommendation: Trial likely to show benefit
```

**Decision:**
- ✅ Proceed with trial
- Sample size: Based on 75% expected outcome
- Plan stratification for high-variability subgroups

---

### Example 2: Finance - Retirement Planning

**Scenario:**  
45-year-old planning for retirement at 65

**Simulation Setup:**
```
Type: Financial Portfolio
Initial Investment: $250,000
Expected Return: 7.5%
Volatility: 18%
Period: 20 years
Simulations: 10,000
```

**Results:**
```
Mean Final Value: $1,042,000
Median: $932,000
95% CI: $482,000 - $1,876,000
Probability of Loss: 2.3%
Probability Doubling: 78%
```

**Retirement Planning:**
- Conservative estimate: $482,000 (5th percentile)
- Realistic estimate: $932,000 (median)
- Optimistic estimate: $1,876,000 (95th percentile)

**Recommendations:**
- Plan expenses based on $500,000-$900,000
- Maintain current contribution rate
- Review annually
- Consider reducing volatility after age 55

---

### Example 3: Healthcare - Cost-Effectiveness

**Scenario:**  
Evaluating new immunotherapy vs standard chemotherapy

**Simulation Setup:**
```
Type: Cost-Effectiveness
Treatment Cost: $120,000 (σ = $25,000)
QALY Gain: 3.2 years (σ = 1.1)
Comparator Cost: $45,000
Comparator QALY: 1.8 years
WTP Threshold: $100,000/QALY
Simulations: 20,000
```

**Calculations:**
```
Incremental Cost: $120k - $45k = $75,000
Incremental QALY: 3.2 - 1.8 = 1.4 years
ICER: $75,000 / 1.4 = $53,571/QALY
```

**Results:**
```
Mean ICER: $53,571/QALY
Probability Cost-Effective (at $100k WTP): 82%
Recommendation: COST-EFFECTIVE
```

**Decision Framework:**
- ICER ($53,571) < WTP ($100,000) ✓
- High probability (82%) ✓
- Recommendation: Approve for formulary inclusion

---

### Example 4: Project Management - Software Launch

**Scenario:**  
Launching new mobile app with hard deadline

**Simulation Setup:**
```
Type: Project Timeline
Tasks:
1. Backend API: 10-15-25 days
2. iOS App: 15-20-30 days
3. Android App: 15-20-28 days
4. Testing: 5-8-15 days
5. App Store Review: 3-7-14 days
Correlation: 0.35
Simulations: 10,000
```

**Results:**
```
Mean Duration: 67 days
Median: 64 days
95% Confidence: 88 days
Range: 52 - 104 days

Probability completing in:
- 60 days: 30%
- 70 days: 62%
- 80 days: 85%
- 90 days: 95%
```

**Project Decision:**
- **Client Promise:** 75 days (75% confidence)
- **Internal Target:** 70 days (allows 5-day buffer)
- **Contingency Plan:** 85 days (15-day buffer)

**Risk Mitigation:**
- Parallel track iOS/Android where possible
- Pre-submit app store materials
- Begin testing early (concurrent with development)
- Daily standups to catch delays

---

## 📚 APPENDIX: MATHEMATICAL FOUNDATIONS

### Bayesian Inference in Context

Monte Carlo can be combined with Bayesian reasoning:

```
Prior → Simulate → Update → Posterior
```

**Example:**
1. Prior belief: 70% treatment success
2. Run simulation with variability
3. Observe actual patient outcomes
4. Update belief using Bayes' theorem
5. Posterior: 75% success (refined estimate)

### Central Limit Theorem

**Why Monte Carlo Works:**
As number of simulations → ∞, the mean of simulations → true mean

This is why:
- More simulations = more accurate
- 10,000+ gives good results
- Results converge to true distribution

### Law of Large Numbers

**Statistical Guarantee:**
Sample mean converges to population mean as sample size increases

**Practical Impact:**
- 1,000 sims: ±5% error
- 10,000 sims: ±1.5% error  
- 100,000 sims: ±0.5% error

---

## 🎓 LEARNING RESOURCES

### Further Reading

**Monte Carlo Methods:**
- "Monte Carlo Methods in Financial Engineering" - Paul Glasserman
- "Risk Analysis: A Quantitative Guide" - David Vose

**Streamlit:**
- Official Streamlit Docs: docs.streamlit.io
- Streamlit Gallery: streamlit.io/gallery

**Healthcare Analytics:**
- "Medical Decision Making" - Sox et al.
- "Cost-Effectiveness in Health and Medicine" - Neumann et al.

### Online Courses

- Coursera: "Computational Investing" (Georgia Tech)
- edX: "Health Economics" (various universities)
- Udemy: "Monte Carlo Simulation Python"

---

## ✅ CHECKLIST: FIRST-TIME USERS

- [ ] Python 3.8+ installed
- [ ] All packages installed (`pip install -r requirements.txt`)
- [ ] Application runs (`streamlit run monte_carlo_streamlit_app.py`)
- [ ] Browser opens to application
- [ ] Tested basic simulation
- [ ] Understand key statistics (mean, median, percentiles)
- [ ] Can interpret histograms
- [ ] Can read cumulative distributions
- [ ] Comfortable adjusting parameters
- [ ] Know when to use each simulation type
- [ ] Ready for real-world application!

---

**END OF USER GUIDE**

**Questions? Issues? Feedback?**  
Contact: acr-platform@support.com  
Version: 1.0.0 | Date: 2025-01-27
