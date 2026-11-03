# Five-minute Shenzhen EV tariff project

Run with Python 3.12 from the raw_urbanev directory. Install requirements with pip. The project ZIP includes the prepared hourly feature table. To regenerate it from the full original archive run:

    python prepare.py /path/to/UrbanEVDataset.zip
    python evaluate.py
    python report.py

To reproduce the forecasts from the included table, start at evaluate.py. Source: Li, Qu, Tan et al., UrbanEV, Dryad DOI 10.5061/dryad.np5hqc04z (February 2026 release). Use the inner archive containing the station-raw folder. Cohort.csv fixes the original 30 station IDs before analysis. The source contains 1,682 station CSVs. Units are local Shenzhen time, charger-hours and estimated kWh from rated power. CNY price observations and hypothetical INR pricing are separate.

Preprocessing: regular five-minute grid, remove duplicate timestamp groups, require nonnegative busy/idle counts that sum to metadata capacity, compute busy/installed occupancy, reject negative kWh. Only complete 12-reading hours for both decision and outcome enter the replay. Lag gaps remain missing. Target is next completed hour's MEAN occupancy and TOTAL energy. Decisions occur after the prior hour closes. EDA and selection use earlier data; no unobserved future price or volume is an input.

Models: September–December fit; January selects lowest MAE separately per target; refit through January; February held out for chronological replay. Compare current hour, yesterday, histogram gradient boosting with hourly lags and identical boosting with three within-hour features. The daily agent chooses a method using seven preceding days of out-of-sample errors. All candidates issue shadow forecasts. agent_decisions.csv records choices and available outcome counts. Updating model choice is distinct from retraining model weights. The six-slide PDF explains data coverage, temporal patterns, forecasting, monitoring and pricing.

Pricing rule: above 80% predicted occupancy quote INR 18, below 30% quote INR 12, otherwise INR 15. Bands are evaluated against actual next-hour occupancy. Scenario revenue is quoted tariff times baseline energy times assumed net demand response. Forward estimates use forecast kWh; replay uses dataset-estimated kWh. Scenarios neither measure causal elasticity nor guarantee physical spare capacity. At a discount of 12 versus 15, revenue break-even requires 25% additional energy. No procurement cost, actual wait, driver identity, actual profit or intervention outcome is available. Results apply to evaluable hours only. They should not be directly compared to the earlier imputed hourly release; use the matched hourly-only boosting scores in this run.

Outputs: audit.csv records station coverage; holdout.csv.gz contains individual predictions and recommendations; forecast_scores.csv contains MAE, RMSE and R²; revenue.csv and tariff_mix.csv contain economic scenarios; tariff_confusion.csv and daily.csv support alert and monitoring diagnostics.
