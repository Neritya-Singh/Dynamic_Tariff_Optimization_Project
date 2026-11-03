"""Create the six-slide club presentation and check the exported replay."""
from pathlib import Path
import textwrap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np
R=Path("results")
h=pd.read_csv("hourly.csv.gz",parse_dates=["time"])
t=pd.read_csv(R/"holdout.csv.gz",parse_dates=["target_time"])
m=pd.read_csv(R/"forecast_scores.csv").query("split=='test'")
v=pd.read_csv(R/"revenue.csv").query("basis=='historical replay'")
assert not t.duplicated(["site","target_time"]).any()
assert t.target_time.min()>=pd.Timestamp("2023-02-01") and t.target_time.max()<pd.Timestamp("2023-03-01")
assert np.isclose(v.baseline_inr.iloc[0],15*t.actual_kwh.sum())
assert np.isclose(v.dynamic_inr.iloc[0],(t.actual_kwh*t.tariff).sum())
t["correct"]=t.tariff==t.actual_band_price
t["error_kwh"]=(t.actual_kwh-t.forecast_kwh).abs()
t["error_occ"]=(t.actual_occupancy-t.forecast_occupancy).abs()
t.groupby(t.target_time.dt.date).agg(pairs=("site","size"),band_accuracy=("correct","mean"),
    mae_kwh=("error_kwh","mean"),mae_occupancy=("error_occ","mean")).to_csv(R/"daily.csv")
train=h[h.time<"2023-01-01"].copy()
train["weekend"]=train.time.dt.dayofweek>=5
profile=train.groupby([train.time.dt.hour,"weekend"]).occupancy.mean().unstack()
profile.to_csv(R/"training_profile.csv")
def plot(title,caption,drawer):
    fig=plt.figure(figsize=(12,6.75),facecolor="#fafaf6")
    fig.text(.07,.89,title,fontsize=24,weight="bold",color="#173640")
    ax=fig.add_axes([.12,.33,.78,.44])
    drawer(ax)
    ax.spines[["right","top"]].set_visible(False)
    fig.text(.07,.10,textwrap.fill(caption,110),fontsize=13,color="#233e42",linespacing=1.35)
    fig.text(.07,.035,"URBANEV   /   SHENZHEN                                         Historical replay   •   30 stations",fontsize=9,color="#596768")
    pdf.savefig(fig)
    plt.close(fig)
def bars(labels,values,label):
    def draw(ax):
        bb=ax.barh(labels,values,color="#24857b")
        ax.bar_label(bb,fmt="%.2f",padding=3)
        ax.margins(x=.18)
        ax.set_xlabel(label)
    return draw
with PdfPages(R/"club_presentation.pdf") as pdf:
    plot("01   How much of February can we evaluate?",
         "Five-minute readings are aggregated only when all 12 intervals are usable. Missing inputs or outcomes remove station-hours from the replay.",
         bars(["Potential February hours","Eligible forecast pairs"],[20160,len(t)],"Station-hours"))
    plot("02   Occupancy by local hour","Training-period means across the sampled stations. Network averages can hide individual stations crossing the 30% and 80% tariff thresholds.",
         lambda ax:(ax.plot(profile.index,profile[False]*100,label="Weekday"),ax.plot(profile.index,profile[True]*100,label="Weekend"),ax.set(xlabel="Hour in Shenzhen",ylabel="Mean occupancy (%)"),ax.legend()))
    for num,target,title,units in [("03","occupancy","Five-minute trends help anticipate occupancy","MAE (percentage points)"),("04","kwh","Recent charging improves the energy forecast","MAE (kWh per station-hour)")]:
        values=m[m.target.eq(target)].set_index("model").mae
        plot(num+"   "+title,"All methods are scored on identical February hours. Hourly boosting and five-minute boosting share model settings; the latter adds end-of-hour occupancy, recent change and last-quarter-hour energy.",
             bars(["Last completed hour","Hourly boosting","Five-minute boosting"],values[["persistence","hourly_boosting","boosting"]]*(100 if target=="occupancy" else 1),units))
    decisions=pd.read_csv(R/"agent_decisions.csv")
    plot("05   Did the feedback loop change the decision?",
         "Each morning the agent selects the forecast method with lowest MAE over the prior seven days. It chose five-minute boosting throughout February. Daily selection added no gain over freezing January’s winner.",
         bars(["Occupancy model","Energy model"],[len(decisions.query("target=='occupancy' and method=='boosting'")),len(decisions.query("target=='kwh' and method=='boosting'"))],"February days selecting five-minute boosting"))
    plot("06   Tariff outcomes depend on driver response",
         "Relative to INR 15/kWh flat pricing. Discount/peak volume changes: weak +10%/−5%, moderate +25%/−10%, strong +40%/−20%, downside 0%/−20%. No customer received these prices.",
         bars(v.scenario,v.gain_pct,"Simulated revenue change (%)"))
print("Band accuracy",t.correct.mean(),"coverage",len(t)/20160)
