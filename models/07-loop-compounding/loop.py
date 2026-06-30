#!/usr/bin/env python3
"""Chapter 7 — Agent-loop compounding (the O(K²) tax).

A multi-turn agent re-sends its growing context every step: at step k the input
is the base prompt B plus every prior tool call/result. Input grows LINEARLY
per step, so CUMULATIVE input over K steps grows QUADRATICALLY:

  step-k input        = B + (k-1)·δ
  cumulative over K    = Σ (B+(k-1)δ) = (δ/2)·K² + (B-δ/2)·K      ← polynomial in K

Three regimes:
  NAIVE      : pay full input price on the quadratic
  CACHED     : the re-sent prefix bills at the cache-read rate (slope ×read/in)
  COMPACTED  : cap context at a window W → input flattens → LINEAR

agent-calc roles:
  - polynomial/evaluate : exact cumulative-token polynomial at each K
  - eval (rational)      : exact $ per regime
"""
import json, subprocess
from fractions import Fraction as F

CALC="agent-calc"
def rn(fr): return {"kind":"rational","numerator":str(fr.numerator),"denominator":str(fr.denominator)}
def run(sub,req):
    r=subprocess.run([CALC,sub],input=json.dumps(req),capture_output=True,text=True)
    if r.returncode: raise RuntimeError(f"{sub}: {r.stderr}")
    return json.loads(r.stdout)
def poly_eval(coeffs, atK):
    """exact value of polynomial (ascending coeffs) at integer K"""
    req={"intent":"evaluate",
         "polynomial":{"variable":"K","coefficients":[rn(c) for c in coeffs]},
         "at":{"kind":"integer","value":str(atK)}}
    res=run("polynomial",req); ex=res["exact"] if "exact" in res else res["value"]
    if isinstance(ex,dict): return F(int(ex["numerator"]),int(ex["denominator"]))
    return F(ex)

# ---- workload ----
B   = 8000          # base context: system + tools + skills
D   = 1500          # tokens added per step (prior tool call + result)
W   = 20000         # compaction window cap (tokens of history kept)
PIN = F("0.26")     # input $/1M  (DeepSeek V3.2 @ DeepInfra)
PRD = F("0.13")     # cache-read $/1M (0.5×)
MM  = 10**6

# cumulative-token polynomial (naive): (D/2)K^2 + (B-D/2)K   → coeffs [0, B-D/2, D/2]
CUM = [F(0), F(B)-F(D,2), F(D,2)]

def cum_naive(K):  return poly_eval(CUM, K)                       # total input tokens, naive
def step_input(k): return B + (k-1)*D                            # per-step input tokens
def cum_compact(K):
    # steps grow until cap, then flat at B+W
    cap = B + W; tot=0
    for k in range(1,K+1): tot += min(B+(k-1)*D, cap)
    return F(tot)

def cost_naive(K):   return cum_naive(K)*PIN/MM
def cost_cached(K):
    # unique tokens (billed once at input) + re-reads (billed at read rate)
    unique = F(B + (K-1)*D)
    rereads = cum_naive(K) - unique
    return (unique*PIN + rereads*PRD)/MM
def cost_compact(K): return cum_compact(K)*PIN/MM               # cached+compacted lower still; show input-priced floor

print(f"Agent loop: base {B} tok, +{D}/step, compaction window {W}. Price {float(PIN)}/{float(PRD)} $/M in/read.\n")
print(f"step-k input grows linearly:  step1={step_input(1)}  step10={step_input(10)} ({step_input(10)/step_input(1):.1f}×)  step50={step_input(50)} ({step_input(50)/step_input(1):.1f}×)\n")
print(f"{'K steps':>8}{'cum tokens (naive)':>20}{'naive $':>11}{'cached $':>11}{'compact $':>12}{'naive/compact':>15}")
print("-"*78)
for K in (5,10,20,50,100):
    cn,cc,cp = cost_naive(K),cost_cached(K),cost_compact(K)
    print(f"{K:>8}{int(cum_naive(K)):>20,}{float(cn):>11.4f}{float(cc):>11.4f}{float(cp):>12.4f}{float(cn/cp):>14.1f}×")

print(f"\nThe quadratic is real: 100-step naive cumulative = {int(cum_naive(100)):,} tokens vs"
      f" {int(cum_naive(10)):,} at 10 steps — {float(cum_naive(100)/cum_naive(10)):.1f}× the tokens for 10× the steps.")
