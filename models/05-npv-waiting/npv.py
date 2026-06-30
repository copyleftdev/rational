#!/usr/bin/env python3
"""Chapter 5 — The NPV of waiting.

You need a fixed monthly token volume for T months. Two ways to pay:
  COMMIT  : lock a discounted rate now -> flat monthly spend  S0·(1-disc)
  PAY-GO  : stay flexible, ride the price decline -> month t spend  S0·(1-g)^(t/12)

Token prices fall fast. So a committed discount is a bet that the lock-in beats
the decline. We NPV both cash-flow streams (discounted at cost of capital) and
find the BREAK-EVEN annual decline rate g* where waiting ties committing.

Two decline regimes (data/decline.md):
  FIXED-QUALITY (same capability gets cheaper): central ~80%/yr  (a16z/Epoch)
  FRONTIER (always run the best): central ~30%/yr, flat-to-modest

agent-calc roles:
  - finance/net_present_value : exact NPV of each spend stream
  - eval (rational)           : exact ratios
Monthly decline & discount factors are rationalized (1e-9) before exact NPV.
"""
import json, subprocess
from fractions import Fraction as F

CALC="agent-calc"
def rn(fr): return {"kind":"rational","numerator":str(fr.numerator),"denominator":str(fr.denominator)}
def run(sub,req):
    r=subprocess.run([CALC,sub],input=json.dumps(req),capture_output=True,text=True)
    if r.returncode: raise RuntimeError(f"{sub}: {r.stderr}")
    return json.loads(r.stdout)
def npv(rate_m, flows):
    res=run("finance",{"intent":"net_present_value","rate":rn(rate_m),"cash_flows":[rn(f) for f in flows]})
    return F(int(res["exact"]["numerator"]),int(res["exact"]["denominator"]))
def ratl(x): return F(x).limit_denominator(10**9)
def monthly_from_annual(a): return ratl((1.0-float(a))**(1.0/12.0))

# ---- assumptions (data/decline.md) ----
S0    = F(195125,1000)        # today's monthly pay-go spend: 1B tok × $0.195125/1M ≈ $195.125
COC_Y = F(12,100)
COC_M = ratl((1.0+float(COC_Y))**(1.0/12.0) - 1.0)
DISC  = F(30,100)             # representative 1-yr reserved/commit discount
FIXED = [("decline 50%/yr (low)",F(50,100)),("decline 80%/yr (central)",F(80,100)),("decline 90%/yr (high)",F(90,100))]
FRONT = [("decline 0%/yr (flat)",F(0,1)),    ("decline 30%/yr (central)",F(30,100)),("decline 50%/yr (high)",F(50,100))]

def npv_commit(disc,T): return npv(COC_M,[S0*(F(1)-disc)]*T)
def npv_paygo(g,T):
    f=monthly_from_annual(g); return npv(COC_M,[S0*(f**t) for t in range(T)])
def breakeven_g(disc,T,lo=0.0,hi=0.99):
    c=npv_commit(disc,T)
    for _ in range(44):
        mid=(lo+hi)/2
        if npv_paygo(ratl(mid),T)<=c: hi=mid
        else: lo=mid
    return (lo+hi)/2

T=12
print(f"S0=${float(S0):.2f}/mo (1B tok) · horizon {T}mo · CoC {int(float(COC_Y)*100)}%/yr · commit discount {int(float(DISC)*100)}%\n")
c=npv_commit(DISC,T)
for title,scen in [("FIXED-QUALITY workload (commodity model, migrate to equal quality)",FIXED),
                   ("FRONTIER workload (always run the best model)",FRONT)]:
    print(title)
    print(f"  {'scenario':<28}{'NPV cost':>11}{'vs commit':>11}{'winner':>11}")
    print(f"  {'COMMIT (flat '+str(int(float(DISC)*100))+'% off)':<28}{float(c):>11.2f}{'—':>11}{'—':>11}")
    for name,g in scen:
        p=npv_paygo(g,T); print(f"  {name:<28}{float(p):>11.2f}{float(p/c-1)*100:>+10.1f}%{('pay-go ✅' if p<c else 'commit ✅'):>11}")
    print()

# ---- break-even decline grid + verdict overlay ----
print("Break-even annual decline g* (pay-go wins ABOVE this; commit wins below):")
print(f"{'commit discount':>16}{'12-mo':>10}{'24-mo':>10}{'36-mo':>10}")
print("-"*46)
grid={}
for disc in (F(15,100),F(30,100),F(45,100)):
    grid[disc]=[breakeven_g(disc,t) for t in (12,24,36)]
    print(f"{str(int(float(disc)*100))+'%':>16}"+"".join(f"{g*100:>9.1f}%" for g in grid[disc]))
print("\nVerdict at CENTRAL decline rates — does COMMIT ever win?")
for label,rate in [("Fixed-quality (80%/yr)",0.80),("Frontier (30%/yr)",0.30)]:
    cells=[]
    for disc in (F(15,100),F(30,100),F(45,100)):
        for j,t in enumerate((12,24,36)):
            if grid[disc][j] > rate: cells.append(f"{int(float(disc)*100)}%/{t}mo")
    print(f"  {label:<24} commit wins only at: {', '.join(cells) if cells else 'NEVER — pay-go always wins'}")
