"""Validate the exports and summarize temporal patterns, errors and scenario economics."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

r=Path("results")
d=pd.read_csv("hourly.csv.gz",parse_dates=["time"])
test=pd.read_csv(r/"holdout.csv.gz",parse_dates=["target_time"])
assert test.target_time.min()==pd.Timestamp("2023-02-01")
assert test.target_time.max()==pd.Timestamp("2023-02-28 23:00")
assert not test.duplicated(["site","target_time"]).any()
assert len(test)==30*28*24
assert test.forecast_occupancy.between(0,1).all() and test.forecast_kwh.ge(0).all()
assert (test.tariff==np.select([test.forecast_occupancy>.8,test.forecast_occupancy<.3],[18,12],15)).all()
revenue=pd.read_csv(r/"revenue.csv")
assert np.allclose(revenue.gain_pct,(revenue.dynamic_inr/revenue.baseline_inr-1)*100)
assert np.isclose(test.actual_kwh.sum()*15,revenue[revenue.basis=="historical replay"].baseline_inr.iloc[0])
assert pd.read_csv(r/"tariff_confusion.csv",index_col=0).values.sum()==len(test)
train=d[d.time<"2023-01-01"].copy()
train["hour"]=train.time.dt.hour
train["day_type"]=np.where(train.time.dt.weekday>=5,"Weekend","Weekday")
profiles=train.groupby(["hour","day_type"]).agg(mean_occupancy=("occupancy","mean"),
       mean_estimated_kwh=("kwh","mean"),hours=("time","size")).reset_index()
profiles.to_csv(r/"training_profile.csv",index=False)
test["occupancy_abs_error"]=(test.actual_occupancy-test.forecast_occupancy).abs()
test["energy_abs_error"]=(test.actual_kwh-test.forecast_kwh).abs()
test["premium_hit"]=(test.tariff==18)&(test.actual_band_price==18)
test["false_premium"]=(test.tariff==18)&(test.actual_band_price!=18)
test["missed_premium"]=(test.tariff!=18)&(test.actual_band_price==18)
metrics={"hours":("site","size"),"occupancy_mae":("occupancy_abs_error","mean"),
         "energy_mae_kwh":("energy_abs_error","mean"),"hits":("premium_hit","sum"),
         "false_premiums":("false_premium","sum"),"missed_premiums":("missed_premium","sum"),
         "estimated_kwh":("actual_kwh","sum")}
test.groupby(test.target_time.dt.date).agg(**metrics).to_csv(r/"daily_scorecard.csv")
test.groupby("site").agg(**metrics).to_csv(r/"station_scorecard.csv")
fig,axes=plt.subplots(1,2,figsize=(10,4))
for name,group in profiles.groupby("day_type"):
    axes[0].plot(group.hour,100*group.mean_occupancy,label=name)
axes[0].set(xlabel="Hour in Shenzhen",ylabel="Mean occupied plugs (%)",title="Historical occupancy by hour")
axes[0].legend(frameon=False)
rev=revenue[revenue.basis=="historical replay"]
axes[1].barh(rev.scenario,rev.gain_pct,color=["#216d76" if v>=0 else "#b4493e" for v in rev.gain_pct])
axes[1].axvline(0,color="#444",lw=.8)
axes[1].set(xlabel="Revenue change vs flat pricing (%)",title="February pricing scenarios")
fig.tight_layout()
fig.savefig(r/"project_results.png",dpi=160)
print("Checks passed")
largest=test.groupby("site").actual_kwh.sum().nlargest(2).index
segments=[]
for label,s in [("all",test),("two_largest",test[test.site.isin(largest)]),
                ("remaining_28",test[~test.site.isin(largest)])]:
    flat=15*s.actual_kwh.sum()
    dynamic=(s.tariff*s.actual_kwh).sum()
    segments.append(dict(segment=label,stations=s.site.nunique(),flat_inr=flat,dynamic_inr=dynamic,
                         kwh_share=s.actual_kwh.sum()/test.actual_kwh.sum(),gain_pct=100*(dynamic/flat-1)))
pd.DataFrame(segments).to_csv(r/"concentration.csv",index=False)
