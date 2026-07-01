#!/usr/bin/env python3
"""Generate article charts as PNGs. Values match the committed chapter harness
outputs; frontier/quadratic series are recomputed from the same formulas.
Run: python3 article/charts/make_charts.py   ->   *.png in this dir."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"figure.dpi":150,"font.size":11,"axes.grid":True,
                     "grid.alpha":0.25,"axes.axisbelow":True,"figure.autolayout":True})
INK, HL, WARN, GOOD = "#1b2838","#2d7dd2","#e15554","#3bb273"
def save(fig,name): fig.savefig(os.path.join(HERE,name),bbox_inches="tight"); plt.close(fig); print("wrote",name)

# ---- Ch01: cost-of-privacy frontier ----
theta=[0,10,20,30,40,50,60,70,80,87,87.2]
cost =[146.77,146.77,146.77,146.77,146.77,154.83,162.89,216.62,271.61,310.48,311.59]
fig,ax=plt.subplots(figsize=(7,4.3))
ax.plot(theta,cost,marker="o",color=HL,lw=2.2,zorder=3)
ax.axvspan(87.2,100,color=WARN,alpha=0.12)
ax.axvline(87.2,color=WARN,ls="--",lw=1.6)
ax.text(88,180,"PRIVACY WALL\n(infeasible ≥87.2%)",color=WARN,fontsize=9,va="center")
ax.annotate("first 40% US is free",(20,146.77),(20,175),color=INK,fontsize=9,
            arrowprops=dict(arrowstyle="->",color=INK,alpha=0.6),ha="center")
ax.set(xlim=(0,100),ylim=(120,340),xlabel="US-jurisdiction floor θ (%)",
       ylabel="min cost  ($/mo @ 1B tokens)",title="Ch.1 — The cost-of-privacy frontier")
save(fig,"ch01_privacy_frontier.png")

# ---- Ch02: self-host break-even utilization ----
labels=["8×H200\nrent on-demand","8×H200\nrent reserved","8×H200\nown","8×B200\nrent on-demand",
        "8×B200\nrent reserved","8×B200\nown"]
u=[531,372,220,232,174,72]
cols=[WARN if v>100 else GOOD for v in u]
fig,ax=plt.subplots(figsize=(7.4,4.3))
b=ax.barh(labels,u,color=cols)
ax.axvline(100,color=INK,ls="--",lw=1.6); ax.text(150,4.6,"100% = break-even\n(right of line = never wins)",fontsize=8.5,color=INK)
for rect,v in zip(b,u): ax.text(v+8,rect.get_y()+rect.get_height()/2,f"{v}%",va="center",fontsize=9)
ax.invert_yaxis()
ax.set(xlim=(0,600),xlabel="break-even utilization u*  (must exceed to beat the API)",
       title="Ch.2 — Self-host only wins at owned Blackwell, >72% utilized")
save(fig,"ch02_selfhost_breakeven.png")

# ---- Ch03: reasoning-token tax (R1 $/solved as thinking burn grows) ----
k=[0,2,4,8,12,20]; r1=[8.13,12.91,17.69,27.24,36.80,55.91]; champ=3.17
fig,ax=plt.subplots(figsize=(7,4.3))
ax.plot(k,r1,marker="o",color=WARN,lw=2.2,label="DeepSeek R1 (reasoner)")
ax.axhline(champ,color=GOOD,lw=2,ls="--",label=f"DeepSeek V3.2 champion ({champ}m)")
ax.fill_between(k,champ,r1,color=WARN,alpha=0.08)
ax.set(xlabel="reasoning multiplier k  (thinking tokens ÷ visible output)",
       ylabel="cost per solved task  (milli-$)",title="Ch.3 — The reasoning-token tax")
ax.legend(frameon=False)
save(fig,"ch03_reasoning_tax.png")

# ---- Ch04: retry cascade (cost/solved vs coverage) ----
names=["Cheap-only","Premium-only\n(Opus)","Cascade\nV3.2→Opus","Cascade\nV3.2→Gemini→Opus"]
cps=[3.17,82.96,19.78,13.52]; cov=[77.0,88.0,97.2,99.5]
cols=[INK,WARN,HL,GOOD]
fig,ax=plt.subplots(figsize=(7.2,4.3))
sc=ax.scatter(cov,cps,s=180,c=cols,zorder=3,edgecolor="white",lw=1.5)
for n,x,y in zip(names,cov,cps):
    ax.annotate(n,(x,y),(x,y+5),fontsize=8.5,ha="center")
ax.set(xlabel="coverage  (% of tasks solved)",ylabel="cost per solved task  (milli-$)",
       xlim=(72,103),ylim=(0,95),title="Ch.4 — Cascades: more coverage, less cost (down-right is best)")
ax.annotate("",(97.2,19.78),(88,82.96),arrowprops=dict(arrowstyle="->",color=GOOD,lw=1.8,alpha=0.7))
save(fig,"ch04_cascade.png")

# ---- Ch05: NPV commit vs pay-go, two decline regimes ----
scen=["Commit\n(30% off)","Pay-go\nfixed-qual 80%/yr","Pay-go\nfrontier 30%/yr"]
npv=[1556.91,1198.50,1905.03]; cols=[INK,GOOD,WARN]
fig,ax=plt.subplots(figsize=(7,4.3))
b=ax.bar(scen,npv,color=cols)
ax.axhline(1556.91,color=INK,ls="--",lw=1,alpha=0.6)
for rect,v in zip(b,npv): ax.text(rect.get_x()+rect.get_width()/2,v+30,f"${v:,.0f}",ha="center",fontsize=9.5)
ax.text(1,1430,"waiting wins\n(−23%)",ha="center",color=GOOD,fontsize=9.5,fontweight="bold")
ax.text(2,1050,"committing\nwins (+22%)",ha="center",color="white",fontsize=9.5,fontweight="bold")
ax.set(ylabel="12-mo NPV cost  ($, lower is better)",ylim=(0,2200),
       title="Ch.5 — Commit only where prices are sticky (frontier), not commodity")
save(fig,"ch05_npv_waiting.png")

# ---- Ch07: the O(K^2) tax ----
K=np.arange(1,101); B,D,W,PIN,PRD=8000,1500,20000,0.26,0.13
cum=np.array([sum(B+(k-1)*D for k in range(1,int(n)+1)) for n in K])
naive=cum*PIN/1e6
unique=np.array([B+(n-1)*D for n in K]); cached=(unique*PIN+(cum-unique)*PRD)/1e6
comp=np.array([sum(min(B+(k-1)*D,B+W) for k in range(1,int(n)+1)) for n in K])*PIN/1e6
fig,ax=plt.subplots(figsize=(7,4.3))
ax.plot(K,naive,color=WARN,lw=2.4,label="naive (quadratic)")
ax.plot(K,cached,color=HL,lw=2.2,label="cached (½ constant, still quadratic)")
ax.plot(K,comp,color=GOOD,lw=2.2,label="compacted (linear)")
ax.set(xlabel="agent loop length  (K tool-call steps)",ylabel="cumulative input cost  ($)",
       title="Ch.7 — Long agent loops cost O(K²) unless you compact")
ax.legend(frameon=False,loc="upper left")
ax.annotate("100 steps = 56× the tokens of 10 steps",(100,naive[-1]),(55,1.9),
            fontsize=9,color=WARN,arrowprops=dict(arrowstyle="->",color=WARN,alpha=0.6))
save(fig,"ch07_loop_quadratic.png")

print("done — 6 charts")
