#!/usr/bin/env python3
"""Chapter 1 — Optimal multi-provider routing as a linear program.

Minimize blended $/1M across a menu of open-weights pairings, subject to:
  - all traffic allocated         (sum x = 1)
  - weighted quality >= Q_floor   (don't drop below a reliability bar)
  - per-endpoint capacity cap     (rate-limit realism / no single point of failure)
  - US-jurisdiction share >= theta (the privacy knob we sweep)

agent-calc does TWO jobs here:
  1. `linear`  -> solve the LP (f64) for the optimal allocation x*
  2. `eval`    -> re-verify the cost of x* in EXACT rationals (no float drift)

Workload blend (production agentic): 85% input / 15% output, 75% input cache-hit.
"""
import json, subprocess
from fractions import Fraction as F

CALC = "agent-calc"
W_FRESH, W_CACHE, W_OUT = F(85,100)*F(25,100), F(85,100)*F(75,100), F(15,100)

# --- proven Tier-1 menu: (label, model@provider, in, cached, out, quality, US?) ---
MENU = [
 ("A","DeepSeek V3.2 @ OpenRouter","0.23","0.023","0.34",77,0),
 ("B","DeepSeek V3.2 @ DeepInfra","0.26","0.13","0.38", 77,1),
 ("C","MiniMax M2 @ MiniMax",     "0.30","0.03","1.20", 73,0),
 ("E","GLM-4.6 @ z.ai",           "0.60","0.11","2.20", 71,0),
 ("F","Kimi K2 @ DeepInfra",      "0.50","0.40","2.00", 66,1),
 ("H","DeepSeek R1 @ DeepInfra",  "0.50","0.35","2.15", 54,1),
]
CAP    = 0.60   # max share per endpoint (rate-limit / SPOF realism)
QFLOOR = 74.0   # weighted-average agentic quality floor

# ---------- agent-calc plumbing ----------
def rn(fr): return {"kind":"rational","numerator":str(fr.numerator),"denominator":str(fr.denominator)}
def add(*n):
    x=n[0]
    for y in n[1:]: x={"kind":"add","left":x,"right":y}
    return x
def mul(a,b): return {"kind":"mul","left":a,"right":b}
def run(sub,req):
    r=subprocess.run([CALC,sub],input=json.dumps(req),capture_output=True,text=True)
    if r.returncode: raise RuntimeError(f"{sub}: {r.stderr}")
    return json.loads(r.stdout)

def blended_exact(pin,pc,pout):
    """exact Fraction $/1M via agent-calc eval"""
    e=add(mul(rn(W_FRESH),rn(F(pin))), mul(rn(W_CACHE),rn(F(pc))), mul(rn(W_OUT),rn(F(pout))))
    res=run("eval",{"intent":"eval","expr":e})
    return F(int(res["exact"]["numerator"]),int(res["exact"]["denominator"]))

# precompute exact blended cost per menu item
BLEND = [blended_exact(pin,pc,pout) for (_,_,pin,pc,pout,_,_) in MENU]
QUAL  = [q for *_,q,_ in [ (m[0],m[5],m[6]) and m for m in MENU ]]  # noqa
QUAL  = [m[5] for m in MENU]
USv   = [m[6] for m in MENU]
n     = len(MENU)

def solve_lp(theta):
    cons=[
        {"coefficients":[1]*n,                    "relation":"eq","rhs":1.0},        # sum=1
        {"coefficients":[float(q) for q in QUAL], "relation":"ge","rhs":QFLOOR},     # quality
        {"coefficients":[float(u) for u in USv],  "relation":"ge","rhs":theta},      # US share
    ]
    req={"intent":"solve_lp","direction":"minimize",
         "objective":[float(b) for b in BLEND],
         "constraints":cons,
         "variables":[{"lower":0.0,"upper":CAP,"kind":"continuous"} for _ in range(n)]}
    return run("linear",req)

def exact_cost(weights):
    """exact $/1M of an allocation: sum(w_i * blend_i), w_i as exact Fractions"""
    terms=[mul(rn(w),rn(b)) for w,b in zip(weights,BLEND)]
    res=run("eval",{"intent":"eval","expr":add(*terms)})
    return F(int(res["exact"]["numerator"]),int(res["exact"]["denominator"])), res["decimal"]

# ---------- sweep the privacy knob ----------
print(f"Menu blended $/1M (exact): "+", ".join(f'{MENU[i][0]}={float(BLEND[i]):.4f}' for i in range(n)))
print(f"Caps={CAP}, quality floor={QFLOOR}\n")
print(f"{'US floor θ':>10}{'min $/1M':>10}{'$/mo@1B':>10}{'avg qual':>9}  allocation")
print("-"*100)
prev=None
for k in range(0,11):
    theta=round(0.10*k,2)
    sol=solve_lp(theta)
    status=sol.get("status")
    if status!="optimal":
        print(f"{theta:>10.2f}   — INFEASIBLE (privacy wall): status={status}")
        continue
    vals = sol["variables"]
    # round f64 allocation to exact rationals (1e-6 grid) for exact re-cost
    weights=[F(round(v,6)).limit_denominator(1000000) for v in vals]
    cexact,cdec=exact_cost(weights)
    avgq=sum(float(w)*QUAL[i] for i,w in enumerate(weights))
    alloc=", ".join(f"{MENU[i][0]}={float(weights[i]):.2f}" for i in range(n) if float(weights[i])>0.005)
    print(f"{theta:>10.2f}{float(cdec):>10.4f}{float(cdec)*1000:>10.2f}{avgq:>9.1f}  {alloc}")
