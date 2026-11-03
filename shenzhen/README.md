# Forecasting EV charging demand and evaluating dynamic tariffs in Shenzhen

One-hour forecasts for 30 single-station zones in the six-month UrbanEV dataset. Forecast measured busy-plug share and estimated energy sales separately, then compare three tariff bands against flat pricing.

## Reproduce

The standalone ZIP includes the hourly input, all code, and completed results. On the GitHub branch the input can also be regenerated from the original data. Use Python 3.12 from the shenzhen directory.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Only needed when hourly.csv.gz is absent or you want to rebuild it:
git clone https://github.com/IntelligentSystemsLab/UrbanEV.git upstream
git -C upstream checkout 44f2aa0c8d89f192bce00bafb0def74a21b39c68
python prepare.py upstream/data
# Run the evaluation and generate the checked outputs
python evaluate.py
python report.py
```

## Data choice and quality

Source: Li, Qu, Tan et al., UrbanEV, [dataset DOI](https://doi.org/10.5061/dryad.np5hqc04z), [authors' processed release](https://github.com/IntelligentSystemsLab/UrbanEV/tree/44f2aa0c8d89f192bce00bafb0def74a21b39c68/data), CC0. Acquisition used the public hourly matrix release because the Dryad five-minute archive download was unavailable here. Every selected zone maps to exactly one site in the authors' inf_raw.csv and agrees with inf.csv on station, zone, and plug count. This gives 36 eligible single-station zones before sampling. Take the first 30 sorted station IDs with at least 95% usable training hours through December. Do not generalize this convenience sample to all sites. The processed release includes publisher cleaning and imputation; source-observed versus imputed intervals cannot be distinguished here.

130,320 hourly rows from September 2022 to February 2023. Occupancy is the count of busy plugs divided by installed capacity. Estimated kWh comes from the published volume measure derived using rated power; availability and power delivery are different concepts. Original CNY electricity and service fees are retained separately. Only 4 of the 30 sites vary their combined posted price (rounded to four decimals). Billing, operator costs, driver queues and interventions are unavailable.

## Forecasting

Treat the most recent station-hour as completed before making a forecast for the following hour. Train on target hours through December. Use January to choose, for each target, the method with the smallest MAE. Refit on outcomes available through January, then evaluate on all 20,160 February station-hours. No random splitting. Lag features never reach beyond the decision hour. Two baselines use the last completed hour or the same hour yesterday. Histogram gradient boosting uses site, clock, recent occupancy and estimated kWh plus day/week lags. No future price, volume or occupancy is an input. This historical exercise assumes the latest completed hour is available without reporting delay.

Persistence won on occupancy MAE (2.85 percentage points in February). Boosting lowered occupancy RMSE from 7.75 to 6.18 points, but had higher MAE. Boosting won for kWh, reducing February MAE from 17.89 to 13.76 kWh. The scorecard separately records energy error, occupancy error, true, false and missed premium alerts.

## Tariffs and economics

Use INR 18 above 80% predicted occupied, INR 12 below 30%, and INR 15 otherwise. These are club scenarios; historical Chinese prices are kept in CNY. The rules use only the selected occupancy forecast. Later actual occupancy is used to score timing. Premium precision 86.4%, recall 86.6%; overall band agreement 94.2%. A valid premium alert confirms the forecast crossed the business threshold, not that a driver accepted the price.

For each held-out row, flat revenue = 15 × baseline kWh. Dynamic revenue = recommended price × baseline kWh × (1 + assumed band response). Sum across identical hours, then compute percentage gain. Forward uses forecast kWh; replay uses the dataset's estimated kWh. Scenario responses are independent net changes in demand; they do not identify transfers among hours or causal elasticity. No-response, weak, moderate, strong and downside combinations are all reported. Rules are fixed, not an estimated profit-maximizing tariff. Discounts from INR 15 to INR 12 need 25% more energy for revenue break-even; INR 18 can tolerate a 16.7% volume decline. Profit break-even also requires cost data.

February replay: INR 2.035 crore flat vs INR 2.061 crore dynamic with unchanged volume (+1.32%). Moderate response (+25% discount-band energy, -10% premium-band energy) gives +1.96%; downside (0%, -20%) gives -4.56%. Two stations accounted for 74.5% of energy. Excluding them yields -6.54% at unchanged volume. A targeted pricing trial would be more defensible than a network-wide rollout.

## Output guide

- results/forecast_scores.csv: validation and test metrics, including all baselines and the chosen model per target.
- results/holdout.csv.gz: inspectable forecasts, target times, actual quantities and suggested prices.
- results/tariff_confusion.csv and tariff_mix.csv: band agreement, counts and energy by price.
- results/revenue.csv and concentration.csv: forecast versus replay, stress scenarios and dependence on high-volume sites.
- results/sites.csv, training_profile.csv, daily_scorecard.csv and station_scorecard.csv: data checks, EDA and monitoring.
- results/project_results.png: hourly occupancy profiles and scenario outcomes.
