"""Forecast next-hour occupancy and kWh and replay tariffs on an untouched final month."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from threadpoolctl import threadpool_limits

out = Path("results")
out.mkdir(exist_ok=True)
d = pd.read_csv("hourly.csv.gz", parse_dates=["time"]).sort_values(["site","time"])
assert not d.duplicated(["site","time"]).any()
assert d.groupby("site").time.diff().dropna().eq(pd.Timedelta(hours=1)).all()
g = d.groupby("site",sort=False)
features = ["site","occupancy","kwh","hour","weekday"]
d["target_time"] = d.time + pd.Timedelta(hours=1)
d["hour"] = d.target_time.dt.hour
d["weekday"] = d.target_time.dt.dayofweek
for col in ["occupancy","kwh"]:
    for lag in [1,2,23,167]:
        name = f"{col}_lag{lag}"
        d[name] = g[col].shift(lag)
        features.append(name)
    d["actual_"+col] = g[col].shift(-1)
d = d.dropna(subset=["occupancy","kwh","actual_occupancy","actual_kwh"])
cut = pd.Timestamp("2023-02-01")
valid = pd.Timestamp("2023-01-01")
test = d[d.target_time>=cut].copy()
score_rows=[]
def scores(y,p):
    return dict(mae=mean_absolute_error(y,p),rmse=root_mean_squared_error(y,p),r2=r2_score(y,p))
for col in ["occupancy","kwh"]:
    y = "actual_"+col
    def models(frame,train):
        m = HistGradientBoostingRegressor(max_iter=100,max_leaf_nodes=23,learning_rate=.09,
                categorical_features=[0],early_stopping=False,random_state=42)
        with threadpool_limits(limits=2):
            m.fit(train[features],train[y])
            pred=m.predict(frame[features])
        return {"persistence":frame[col].to_numpy(),"previous_day":frame[col+"_lag23"].fillna(frame[col]).to_numpy(),
                "boosting":np.clip(pred,0,1 if col=="occupancy" else None)}
    val=d[(d.target_time>=valid)&(d.target_time<cut)]
    selected=None
    for split, frame,train in [("validation",val,d[d.target_time<valid]),("test",test,d[d.target_time<cut])]:
        preds=models(frame,train)
        if split=="validation":
            selected=min(preds,key=lambda k:mean_absolute_error(frame[y],preds[k]))
        for key,p in preds.items():
            score_rows.append(dict(split=split,target=col,model=key,selected=key==selected,rows=len(p),**scores(frame[y],p)))
        if split=="test":
            test["forecast_"+col]=preds[selected]
pd.DataFrame(score_rows).to_csv(out/"forecast_scores.csv",index=False)
def price(x):
    return np.select([x>.80,x<.30],[18.,12.],default=15.)
test["tariff"]=price(test.forecast_occupancy)
test["actual_band_price"]=price(test.actual_occupancy)
pd.crosstab(test.actual_band_price,test.tariff).to_csv(out/"tariff_confusion.csv")
test.groupby("tariff").agg(hours=("site","size"),forecast_energy=("forecast_kwh","sum"),estimated_energy=("actual_kwh","sum")).to_csv(out/"tariff_mix.csv")
rows=[]
for basis,col in [("forward forecast","forecast_kwh"),("historical replay","actual_kwh")]:
    q=test[col]
    base=(15*q).sum()
    for name,discount,premium in [("unchanged",0,0),("weak",.10,-.05),("moderate",.25,-.10),("strong",.40,-.20),("downside",0,-.20)]:
        # Independent net changes in kWh per price band; no automatic transfers.
        sold=q*(1+np.select([test.tariff==12,test.tariff==18],[discount,premium],default=0.))
        revenue=(sold*test.tariff).sum()
        rows.append(dict(basis=basis,scenario=name,discount_response=discount,premium_response=premium,
                 baseline_inr=base,dynamic_inr=revenue,gain_pct=100*(revenue/base-1),
                 scenario_kwh=sold.sum(),inr_per_kwh=revenue/sold.sum()))
pd.DataFrame(rows).to_csv(out/"revenue.csv",index=False)
test[["site","time","target_time","actual_occupancy","forecast_occupancy","actual_kwh","forecast_kwh","tariff","actual_band_price"]].to_csv(out/"holdout.csv.gz",index=False,float_format="%.6f")
print(pd.DataFrame(score_rows).round(4).to_string(index=False))
print(pd.DataFrame(rows).round(2).to_string(index=False))
