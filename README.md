# Autonomous EV Charging Demand Prediction & Dynamic Pricing Agent

An end-to-end data analytics and machine learning workflow that forecasts localized electric vehicle (EV) charging network utilization and simulates an adaptive, closed-loop dynamic pricing agent to optimize infrastructure efficiency. The Project was announced by Society of Business (SocBiz) - IIT Rookee Club.

Problem Statement - [Click here to view the Google Drive folder](https://drive.google.com/file/d/1X_HSEORnjR4FJK1D2t58TiP7LInP52EZ/view?usp=sharing)


## Project Performance Dashboard

| Evaluation Parameter | Achieved Result | System Context |
| :--- | :--- | :--- |
| **Demand Prediction Accuracy ($R^2$)** | **74.08%** | UrbanEV Public Grid |
| **Mean Absolute Error (MAE)** | **0.0627** | Demand Prediction Error ($\pm6.27\%$) |
| **Average Waiting Time Reduction** | **88.40% Latency Drop** | Queuing Theory Proxy Simulation |
| **Off-Peak Volume Growth** | **+5.00%** | Midday Demand Stimulus |
| **Dynamic Tariff Revenue Gain** | **+8.30% Margin Shift** | ACN Workplace Lot Simulation |
| **Simulated Customer Response** | **-3.02% Load Shift** | Price Elasticity Adjustment ($\epsilon = -0.4$) |
| **Pricing Efficiency Score** | **7.59 / 100.00** | Behavioral Workplace Correlation |

---

## Core Architecture Pipeline

The project implements a 4-phase data engineering and modeling workflow:

1. **Data Preprocessing & Reshaping:** Converts raw workplace transaction JSON formats into structured dataframes. Uses `pd.melt()` to flatten wide-layout public grid occupancy matrices into long-format time-series rows.
2. **Exploratory Data Analysis (EDA):** Profiles charging demand across diurnal cycles, identifying a heavy midnight-to-7 AM commercial fleet surge in public grids and an inverse daytime 9-to-5 peak at workplaces. Uses variance calculations to prove time-of-day blocks dictate grid volatility rather than day types.
3. **Supervised Machine Learning:** Trains a Random Forest Regressor using location-focused feature inputs to resolve station spatial blindness, tracking future grid load within an average 6% margin of error.
4. **Agentic Dynamic Pricing:** Implements an automated tariff engine that charges a 30% premium (₹19.50/kWh) during peak congestion ($\ge30\%$ load) and offers a 25% discount (₹11.25/kWh) during underutilized valleys ($\le23\%$ load). Features a closed-loop monitoring agent that self-corrects discount thresholds when operational deficits occur.

---

## Key Visual Insights

* **The Diurnal Inversion:** Public urban chargers experience their peak strain overnight due to commercial fleet cycles, while workplace facilities peak sharply during morning arrival hours.
* **Queuing Theory Impact:** By flattening peak load by just 4%, the system avoids exponential congestion build-ups, dropping the mathematical waiting-time proxy by 88.40%.
* **Workplace Captive Audience:** A lower Pricing Efficiency Score (7.59) combined with an 8.30% revenue gain proves workplace users park and charge based on rigid office hours, making them reliable, premium revenue targets during grid spikes.

---

## Environment & Libraries Used
* **Language:** Python
* **Data Manipulation:** `pandas`, `numpy`, `json`
* **Machine Learning:** `scikit-learn` (Random Forest Regressor)
* **Visualization:** `matplotlib`

## Repository Deliverables
* `Project.ipynb`: The fully documented, executable Jupyter Notebook containing all clean markdown sections.
* `Datasets/`: Directory housing the raw public grid tracking files and workplace transaction metrics.
* `Submission_Outputs/`: Automated standalone CSV exports containing detailed simulation rows and data summaries.