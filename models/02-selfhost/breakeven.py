#!/usr/bin/env python3
"""Chapter 2 — Self-host vs. serverless break-even.

Apples-to-apples: self-hosting DeepSeek V3.2 on your own GPUs vs. buying the
SAME model per-token from DeepInfra (US, ZDR). The insight intuition misses:
a self-hosted node costs the same at 5% or 95% load, while the API scales
linearly with tokens. So the real question is NOT "what dollar volume" but
"how BUSY must the box stay to win?" -> break-even UTILIZATION u*.

agent-calc roles:
  - finance/amortize : monthly cost of OWNED hardware (capex over depreciation @ cost-of-capital)
  - eval (rational)  : exact break-even utilization u* and volume V*

Definitions (monthly = 730 h):
  node_month   = gpus * gpu_$/hr * 730                      (rented)
               = amortize(gpus*card$, r, term) + power      (owned)
  cap100       = throughput_tok_s * 3600 * 730             (tokens/mo at 100% util)
  selfhost $/1M(u) = node_month * 1e6 / (cap100 * u)
  break-even:  u* = node_month * 1e6 / (cap100 * p_api),  V* = node_month * 1e6 / p_api
  If u* > 1  ->  self-host NEVER beats the API, even at full tilt.
"""
import json, subprocess
from fractions import Fraction as F

CALC="agent-calc"; HOURS_MO=730
def rn(fr): return {"kind":"rational","numerator":str(fr.numerator),"denominator":str(fr.denominator)}
def run(sub,req):
    r=subprocess.run([CALC,sub],input=json.dumps(req),capture_output=True,text=True)
    if r.returncode: raise RuntimeError(f"{sub}: {r.stderr}")
    return json.loads(r.stdout)
def ev(expr):
    res=run("eval",{"intent":"eval","expr":expr}); return F(int(res["exact"]["numerator"]),int(res["exact"]["denominator"]))
def mul(a,b): return {"kind":"mul","left":a,"right":b}
def div(a,b): return {"kind":"div","left":a,"right":b}
def amortize_payment(principal, annual_rate, months):
    res=run("finance",{"intent":"amortize","principal":{"kind":"integer","value":str(principal)},
        "annual_rate":rn(annual_rate),"periods":months,"periods_per_year":12})
    p=res["payment"]; return F(int(p["numerator"]),int(p["denominator"]))

# ---- shared assumptions ----
P_API   = F("0.195125")     # DeepSeek V3.2 @ DeepInfra blended $/1M (Ch01)
P_FLOOR = F("0.0896")       # DeepSeek V4 Flash @ Fireworks — the API floor
CAP_RATE=F(8,100); DEPREC=36; PUE=F(14,10); KWH=F(12,100)

# ---- node specs (data/gpu.md, observed 2026-06-30) ----
# name, gpus, $/hr on-demand, $/hr reserved, card$, watts, (thru_lo, thru_mid, thru_hi)
NODES = [
 ("8×H200 (Hopper)", 8, F("3.50"), F("2.45"), 31000, 700, (6000,7500,9000)),
 ("8×B200 (Blackwell)",8, F("6.11"), F("4.58"), 40000,1000, (24000,30000,38000)),
]

def cap100(thru): return thru*3600*HOURS_MO
def be_u(nm,thru): return ev(div(mul(rn(nm),rn(F(10**6))), mul(rn(F(cap100(thru))),rn(P_API))))
def be_V(nm):      return ev(div(mul(rn(nm),rn(F(10**6))),rn(P_API)))

def fmt_u(u): return f"{float(u)*100:.0f}%" + (" → NEVER" if u>1 else "")

for name,gpus,od,rv,card,watts,(tlo,tmid,thi) in NODES:
    rent_od = ev(mul(rn(od*gpus), rn(F(HOURS_MO))))
    rent_rv = ev(mul(rn(rv*gpus), rn(F(HOURS_MO))))
    amort   = amortize_payment(card*gpus, CAP_RATE, DEPREC)
    power   = ev(mul(mul(rn(F(watts*gpus,1000)),rn(KWH*PUE)), rn(F(HOURS_MO))))
    own     = amort + power
    print(f"\n=== {name} — DeepSeek V3.2 vs DeepInfra API (${float(P_API):.4f}/1M) ===")
    print(f"throughput {tmid} tok/s mid → node capacity {cap100(tmid)/1e9:.1f}B tok/mo @100% util")
    print(f"{'procurement':<24}{'$/node/mo':>11}{'self-host $/1M@100%':>20}{'break-even u*':>15}{'break-even V*/mo':>18}")
    print("-"*90)
    for label,nm in [("Rent on-demand",rent_od),("Rent 1-yr reserved",rent_rv),("Own (amort+power)",own)]:
        sh100 = ev(div(mul(rn(nm),rn(F(10**6))), rn(F(cap100(tmid)))))  # $/1M at 100% util
        u=be_u(nm,tmid); V=be_V(nm)
        print(f"{label:<24}{float(nm):>11.0f}{float(sh100):>20.4f}{fmt_u(u):>15}{float(V)/1e9:>15.1f}B")
    # throughput sensitivity on the best (owned) case
    print(f"  throughput band → owned break-even u*: ", end="")
    print(" | ".join(f"{t} tok/s: {fmt_u(be_u(own,t))}" for t in (tlo,tmid,thi)))

print(f"\nNote: vs the API FLOOR (V4 Flash @ Fireworks ${float(P_FLOOR):.4f}/1M), every break-even u* roughly DOUBLES.")
