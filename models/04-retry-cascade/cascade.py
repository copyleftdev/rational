#!/usr/bin/env python3
"""Chapter 4 — The retry cascade.

Run a CHEAP model on every task; escalate to a RELIABLE premium model only on
the residual failures. The cheap model handles the easy majority; you pay the
premium only on the hard tail.

Cascade (cheap -> premium):
  P(escalate) = 1 - p_cheap
  P(solve)    = p_cheap + (1-p_cheap)·q     # q = P(premium solves | cheap failed)
  E[cost]     = C_cheap + (1-p_cheap)·C_prem
  cost/solved = E[cost] / P(solve)

KEY: retrying the SAME model never changes cost/solved (it stays C/p) and, for
deterministic failures, doesn't even raise coverage. Only escalating to a
DIFFERENT, better model moves both. q < p_prem captures failure CORRELATION
(tasks the cheap model failed are harder for the premium too) — swept below.

agent-calc roles:
  - stats/binomial_pmf : P(cheap fails) = (1-p)^1   (f64)
  - eval (rational)    : exact expected cost and cost-per-solved
"""
import json, subprocess
from fractions import Fraction as F

CALC="agent-calc"
def rn(fr): return {"kind":"rational","numerator":str(fr.numerator),"denominator":str(fr.denominator)}
def run(sub,req):
    r=subprocess.run([CALC,sub],input=json.dumps(req),capture_output=True,text=True)
    if r.returncode: raise RuntimeError(f"{sub}: {r.stderr}")
    return json.loads(r.stdout)
def ev(expr):
    res=run("eval",{"intent":"eval","expr":expr}); return F(int(res["exact"]["numerator"]),int(res["exact"]["denominator"]))
def mul(a,b): return {"kind":"mul","left":a,"right":b}
def add(a,b): return {"kind":"add","left":a,"right":b}
def binom_all_fail(N,p):
    """P(0 successes in N) = (1-p)^N, via agent-calc stats (f64)"""
    return F(run("stats",{"intent":"binomial_pmf","n":N,"p":float(p),"k":0})["value"]).limit_denominator(10**9)

# ---- task shape (consistent with Ch03) ----
I_IN, O_VIS, CACHE = 8000, 600, F(75,100)
def attempt_cost(pin,pc,pout,k):
    in_blend=(F(1)-CACHE)*pin + CACHE*pc
    in_part = F(I_IN)*in_blend / 10**6
    out_part= F(O_VIS*(1+k))*pout / 10**6
    return ev(add(rn(in_part),rn(out_part)))

# ---- the tiers (data/frontier.md + Ch00; reasoning multiplier k assumed) ----
CH  = dict(name="DeepSeek V3.2", c=attempt_cost(F("0.26"),F("0.13"),F("0.38"),4), p=F(77,100))  # cheap open
MID = dict(name="Gemini 3.1 Pro",c=attempt_cost(F("2.00"),F("0.20"),F("12.0"),3), p=F(81,100))  # mid frontier
PR  = dict(name="Claude Opus 4.8",c=attempt_cost(F("5.00"),F("0.50"),F("25.0"),3),p=F(88,100))  # top reliable

print(f"Task {I_IN}in/{O_VIS}out, 75% input cache-hit. (m = milli-dollars = $0.001 / task)")
for t in (CH,MID,PR): print(f"  {t['name']:<16} C={float(t['c'])*1000:7.3f}m  p={float(t['p']):.2f}")
print()

# ---- single-shot baselines ----
cps_cheap = CH["c"]/CH["p"]; cps_prem = PR["c"]/PR["p"]
print(f"{'strategy':<40}{'cost/solved':>12}{'coverage':>10}{'%→premium':>11}")
print("-"*74)
print(f"{'Cheap-only (single shot)':<40}{float(cps_cheap)*1000:>11.3f}m{float(CH['p'])*100:>9.1f}%{0.0:>10.1f}%")
print(f"{'Premium-only Opus (single shot)':<40}{float(cps_prem)*1000:>11.3f}m{float(PR['p'])*100:>9.1f}%{100.0:>10.1f}%")

# ---- 2-tier cascade: cheap -> Opus (q = P(Opus solves | cheap failed)) ----
def cascade2(q):
    pfail = binom_all_fail(1, CH["p"])                 # 1 - p_cheap
    e_cost = ev(add(rn(CH["c"]), rn(pfail*PR["c"])))
    p_solve = F(1) - pfail*(F(1)-q)
    return e_cost/p_solve, p_solve, pfail
cps,ps,pf = cascade2(PR["p"])
print(f"{'Cascade  V3.2 → Opus':<40}{float(cps)*1000:>11.3f}m{float(ps)*100:>9.1f}%{float(pf)*100:>10.1f}%")

# ---- 3-tier cascade: cheap -> Gemini -> Opus (independence) ----
f1 = binom_all_fail(1, CH["p"]); f2 = binom_all_fail(1, MID["p"])
e_cost3 = ev(add(add(rn(CH["c"]), rn(f1*MID["c"])), rn(f1*f2*PR["c"])))
p_solve3 = F(1) - f1*f2*(F(1)-PR["p"])
to_mid, to_top = f1, f1*f2
print(f"{'Cascade  V3.2 → Gemini → Opus':<40}{float(e_cost3/p_solve3)*1000:>11.3f}m{float(p_solve3)*100:>9.1f}%{float(to_top)*100:>10.1f}%")
print(f"   (traffic → Gemini {float(to_mid)*100:.1f}% , → Opus {float(to_top)*100:.1f}%)")

# ---- correlation sensitivity (2-tier) ----
print(f"\nFailure-correlation sensitivity (V3.2 → Opus):")
print(f"{'q = P(Opus solves | V3.2 failed)':<36}{'cost/solved':>12}{'coverage':>10}{'vs premium-only':>17}")
print("-"*75)
for qf in (F(88,100),F(70,100),F(50,100),F(30,100)):
    cps,ps,_ = cascade2(qf)
    tag = "  (independence)" if qf==PR["p"] else ""
    print(f"{f'q = {float(qf):.2f}'+tag:<36}{float(cps)*1000:>11.3f}m{float(ps)*100:>9.1f}%{float(cps_prem/cps):>13.1f}× cheaper")
