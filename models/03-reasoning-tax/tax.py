#!/usr/bin/env python3
"""Chapter 3 — The reasoning-token tax.

Reasoning models emit hidden "thinking" tokens, billed at the OUTPUT rate. A
task whose visible answer is 600 tokens can bill 7,800 with a heavy reasoner.
The honest unit is NOT $/token or $/attempt — it's COST PER SOLVED TASK:

    cost_per_attempt = I_eff·price_in_blend + O·(1+k)·price_out
    cost_per_solved  = cost_per_attempt / p            (retry until success)

where k = thinking tokens ÷ visible output, p = per-task success probability.

agent-calc roles:
  - eval  (rational) : exact per-attempt and per-solved costs
  - solve (affine)   : the break-even success rate a model needs to match the champion
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

# ---- task shape (per attempt) ----
I_IN   = 8000      # input tokens (agent context + tools + prompt)
O_VIS  = 600       # visible output tokens (the answer / tool-call args)
CACHE  = F(75,100) # input cache-hit fraction

# ---- models: in, cached, out ($/1M); quality (Ch00); k = reasoning multiplier ----
# k and the quality->success mapping are ASSUMPTIONS (flagged); sensitivity below.
M = [
 ("MiniMax M2",   F("0.30"),F("0.03"),F("1.20"), 73,  2),
 ("Kimi K2",      F("0.50"),F("0.40"),F("2.00"), 66,  1),
 ("DeepSeek V3.2",F("0.26"),F("0.13"),F("0.38"), 77,  4),
 ("GLM-4.6",      F("0.60"),F("0.11"),F("2.20"), 71,  5),
 ("DeepSeek R1",  F("0.50"),F("0.35"),F("2.15"), 54, 12),
]
MM = F(10**6)

def attempt_cost(pin,pc,pout,k):
    in_blend = (F(1)-CACHE)*pin + CACHE*pc                     # $/1M effective input
    in_part  = ev(mul(rn(F(I_IN)*in_blend), rn(F(1,1)))) / MM  # I·in_blend /1e6
    out_part = ev(mul(rn(F(O_VIS*(1+k))*pout), rn(F(1,1)))) / MM
    return ev(add(rn(in_part), rn(out_part)))                  # exact $/attempt
def per_solved(ac,q):   return ac / F(q,100)

rows=[]
for name,pin,pc,pout,q,k in M:
    ac = attempt_cost(pin,pc,pout,k)
    think = ev(mul(rn(F(O_VIS*k)*pout), rn(F(1,1))))/MM        # the tax: thinking-token $
    tax_pct = float(think/ac*100)
    cps = per_solved(ac,q)
    rows.append((name,q,k,ac,tax_pct,cps))

champ = min(rows,key=lambda r:r[5])
print(f"Task: {I_IN} in / {O_VIS} visible out, {int(float(CACHE)*100)}% input cache-hit. p = quality/100 (proxy).\n")
print(f"{'model':<16}{'q':>4}{'k':>4}{'$/attempt':>12}{'think-tax':>11}{'$/solved':>12}{'×champion':>11}")
print("-"*72)
for name,q,k,ac,tax,cps in sorted(rows,key=lambda r:r[5]):
    print(f"{name:<16}{q:>4}{k:>4}{float(ac)*1000:>11.4f}m{tax:>10.0f}%{float(cps)*1000:>11.4f}m{float(cps/champ[5]):>10.2f}×")
print(f"\nchampion (lowest $/solved): {champ[0]}   ($/x are milli-dollars, i.e. $0.001)")

# ---- break-even success rate via agent-calc solve ----
# For model B to MATCH champion cost-per-solved:  CPS_champ · p − attempt_cost_B = 0
print(f"\nBreak-even success rate to match {champ[0]} (solve, exact):")
cps_champ = champ[5]
for name,q,k,ac,tax,cps in sorted(rows,key=lambda r:r[5]):
    if name==champ[0]: continue
    eqn={"intent":"solve","variable":"p","equation":{
        "left":{"kind":"sub","left":mul(rn(cps_champ),{"kind":"symbol","name":"p"}),"right":rn(ac)},
        "right":{"kind":"integer","value":"0"}}}
    sol=run("solve",eqn)["solutions"][0]
    pstar=F(int(sol["numerator"]),int(sol["denominator"]))
    flag = "  IMPOSSIBLE (>100%)" if pstar>1 else ""
    print(f"  {name:<16} needs p* = {float(pstar)*100:6.1f}%  (currently {q}%){flag}")

# ---- reasoning-multiplier sweep: R1 vs V3.2 as k grows ----
print(f"\nReasoning-tax sweep — $/solved as thinking burn k grows (DeepSeek R1, p={dict((r[0],r[1]) for r in rows)['DeepSeek R1']}%):")
pin,pc,pout,q = F('0.50'),F('0.35'),F('2.15'),54
for k in (0,2,4,8,12,20):
    cps=per_solved(attempt_cost(pin,pc,pout,k),q)
    print(f"  k={k:>2} (think={O_VIS*k:>5} tok): $/solved = {float(cps)*1000:.4f}m   ({float(cps/cps_champ):.1f}× champion)")
