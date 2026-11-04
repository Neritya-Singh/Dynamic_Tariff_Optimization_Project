# Hourly EV charging tariffs

Open **Dynamic_Tariff_Optimization.ipynb** to see the executed notebook and graphs. To rerun, use Python 3.12 with the packages in requirements.txt and Jupyter. Download [UrbanEV](https://doi.org/10.5061/dryad.np5hqc04z) and place the inner UrbanEVDataset.zip beside the notebook (or set URBANEV_ZIP). Run all cells in order. Allow several GB of RAM.

The notebook builds results/ from raw readings. It includes demand forecasting, daily monitoring and a tariff agent. Forecast mean occupancy for the incoming hour and hold its price fixed until the next hour. The prices are ₹15 up to 60%, ₹16 above 60%, ₹17 above 70%, ₹18 above 80%, and ₹19 above 90%. No discounts. Exact threshold values remain in the lower band. Tariffs and gross revenue are INR-based scenarios.

### Findings from this run

- All 1,682 station files were processed. 1,633 stations supplied 633,815 valid February cases, covering 56.1% of potential station-hours.
- Adding five-minute signals reduced February occupancy MAE from 2.84 to 2.31 percentage points and energy MAE from 13.45 to 11.78 kWh. The daily monitor selected enhanced boosting on all 28 days for both targets.
- The pricing agent recommended a premium in 12.5% of scored hours. Forecast and reference tariff bands matched in 97.0% of hours.
- Compared with flat ₹15/kWh, gross revenue changed by +4.08% with unchanged energy, +1.97% with elasticity −0.5, and -1.83% with elasticity −1.5. Under unchanged demand a nonnegative premium mechanically increases gross revenue whenever energy is sold at a premium. Customer acceptance remains unknown.
- February was held out of model fitting. Because this period had already been examined during project development, the pricing replay is retrospective. An independent later period or a controlled pilot would be needed to confirm policy performance.

**Files.** coverage.csv includes every station, scores.csv compares January and February methods, agent.csv logs daily choices, tariff_mix.csv gives per-price volume, tariff_confusion.csv shows decision errors, and revenue.csv compares assumptions. The downloadable project also contains holdout.csv.gz, the row-level replay. Running the notebook regenerates it.
