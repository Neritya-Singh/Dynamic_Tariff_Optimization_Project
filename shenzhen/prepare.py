"""Rebuild the packaged hourly sample from the pinned authors' UrbanEV GitHub data directory."""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

parser=argparse.ArgumentParser()
parser.add_argument("directory",type=Path)
source=parser.parse_args().directory
raw=pd.read_csv(source/"inf_raw.csv")
clean=pd.read_csv(source/"inf.csv")
assert raw.station_id.is_unique and clean.station_id.is_unique
singleton=raw.groupby("TAZID").filter(lambda group:len(group)==1)
sites=clean.merge(singleton,on=["station_id","TAZID","charge_count"],validate="one_to_one").sort_values("station_id")
sites=sites[sites.charge_count>0]
names={"occupancy":"busy","volume":"kwh","duration":"charging_hours","e_price":"electricity_cny","s_price":"service_cny"}
tables={col:pd.read_csv(source/(file+".csv"),index_col=0,parse_dates=True) for file,col in names.items()}
rows=[]
audit=[]
for s in sites.itertuples():
    frame=pd.DataFrame({col:table[str(s.TAZID)] for col,table in tables.items()})
    assert frame.index.is_unique
    frame=frame.reindex(pd.date_range("2022-09-01","2023-02-28 23:00",freq="h"))
    frame["occupancy"]=frame.busy.div(s.charge_count).where(frame.busy.between(0,s.charge_count))
    frame["kwh"]=frame.kwh.where(frame.kwh>=0)
    valid=frame[["occupancy","kwh"]].notna().all(axis=1)
    coverage=valid[frame.index<"2023-01-01"].mean()
    if coverage < .95:
        continue
    frame["site"]=s.station_id
    frame["zone"]=s.TAZID
    frame["plugs"]=s.charge_count
    frame.index.name="time"
    rows.append(frame.reset_index())
    audit.append(dict(site=s.station_id,zone=s.TAZID,plugs=s.charge_count,training_coverage=coverage,
        valid_hours=int(valid.sum()),posted_price_levels=(frame.electricity_cny+frame.service_cny).round(4).nunique()))
    if len(rows)==30:
        break
assert len(rows)==30
pd.concat(rows).to_csv("hourly.csv.gz",index=False)
pd.DataFrame(audit).to_csv("results/sites.csv",index=False)
