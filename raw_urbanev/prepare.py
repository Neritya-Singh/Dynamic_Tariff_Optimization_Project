"""Aggregate regular five-minute station observations into completed hours."""
import argparse
from pathlib import Path
import zipfile
import pandas as pd
import numpy as np

parser=argparse.ArgumentParser()
parser.add_argument("archive")
args=parser.parse_args()
cohort=pd.read_csv("cohort.csv")
hours=[]
audit=[]
grid=pd.date_range("2022-09-01","2023-02-28 23:55",freq="5min")
with zipfile.ZipFile(args.archive) as z:
    prefix=next(n.rsplit("/",1)[0] for n in z.namelist() if n.endswith("station-raw/station_information.csv"))
    meta=pd.read_csv(z.open(prefix+"/station_information.csv"))
    print("station files:",sum(n.startswith(prefix+"/charge_5min/") and n.endswith(".csv") for n in z.namelist()))
    for site in cohort.site:
        capacity=int(meta.loc[meta.station_id==site,"charge_count"].item())
        raw=pd.read_csv(z.open(f"{prefix}/charge_5min/{site}.csv"),parse_dates=["time"])
        raw_count=len(raw)
        duplicate=raw.time.duplicated(keep=False)
        v=raw[~duplicate].set_index("time").reindex(grid)
        valid=v.busy.ge(0)&v.idle.ge(0)&v.busy.add(v.idle).eq(capacity)
        occ=(v.busy/capacity).where(valid)
        k=v.volume.where(v.volume.ge(0))
        def aggregate(series,operation):
            return getattr(series.resample("h"),operation)().where(series.resample("h").count()==12)
        # Require complete occupancy and energy coverage separately, no forward filling.
        h=pd.DataFrame({"occupancy":aggregate(occ,"mean"),"kwh":aggregate(k,"sum"),
            "occ_last":aggregate(occ,"last"),"kwh_last15":k.rolling(3).sum().resample("h").last(),
            "charging_hours":aggregate(v.duration.where(v.duration.ge(0)),"sum"),
            "posted_cny":aggregate(v.e_price+v.s_price,"mean")})
        h["occ_change15"]=occ.diff(3).resample("h").last().where(h.occupancy.notna())
        h["site"]=site
        h["plugs"]=capacity
        h.index.name="time"
        hours.append(h.reset_index())
        audit.append(dict(site=site,raw_rows=raw_count,duplicate_rows=int(duplicate.sum()),
             complete_hours=int(h[["occupancy","kwh"]].notna().all(axis=1).sum()),installed=capacity))
pd.concat(hours).to_csv("hourly.csv.gz",index=False)
pd.DataFrame(audit).to_csv("results/audit.csv",index=False)
