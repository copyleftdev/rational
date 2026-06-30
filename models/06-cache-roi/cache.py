#!/usr/bin/env python3
"""Chapter 6 — Prompt-cache ROI.

Caching a prompt prefix isn't free: a cache WRITE can cost more than a normal
input token (Anthropic 1.25x at 5-min TTL, 2x at 1-hr), while READS are cheap
(~0.1-0.5x). So caching pays only if you REUSE the prefix enough times before
it expires. How many reuses is "enough"?

For a prefix reused across N calls (write once, read N-1 times):
  no-cache = N · L · p_in
  cache    = L · p_write + (N-1) · L · p_read
  break-even:  N* = (p_write - p_read) / (p_in - p_read)
  savings(N) = 1 - [p_write + (N-1)p_read] / [N · p_in]
  ceiling (N→∞) = 1 - p_read/p_in

agent-calc roles:
  - eval (rational)          : exact break-even N* and savings%
  - interval/polynomial_range: cost BAND when reuse count N is uncertain
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
def sub(a,b): return {"kind":"sub","left":a,"right":b}
def div(a,b): return {"kind":"div","left":a,"right":b}

# ---- providers: in, cache-read, cache-write ($/1M). write=in means "no write fee". ----
P = [
 ("DeepInfra V3.2 (0.5× read)", F("0.26"), F("0.13"),  F("0.26")),
 ("DeepSeek direct (0.1× read)",F("0.27"), F("0.027"), F("0.27")),
 ("OpenAI GPT-5.1 (0.1× read)", F("1.25"), F("0.125"), F("1.25")),
 ("Fireworks (0.5× read)",      F("0.30"), F("0.15"),  F("0.30")),
 ("Anthropic Opus 5-min TTL",   F("5.00"), F("0.50"),  F("6.25")),  # write 1.25×
 ("Anthropic Opus 1-hr TTL",    F("5.00"), F("0.50"),  F("10.0")),  # write 2×
]

def Nstar(pin,pr,pw): return ev(div(sub(rn(pw),rn(pr)), sub(rn(pin),rn(pr))))
def savings(pin,pr,pw,N):
    num = rn(pw) if N==1 else {"kind":"add","left":rn(pw),"right":rn(pr*(N-1))}
    return F(1) - ev(div(num, rn(pin*N)))

print(f"{'provider':<30}{'break-even N*':>14}{'save@2':>9}{'save@5':>9}{'save@10':>9}{'ceiling':>9}")
print("-"*80)
for name,pin,pr,pw in P:
    ns=Nstar(pin,pr,pw); ceil=F(1)-pr/pin
    s2,s5,s10=(savings(pin,pr,pw,n) for n in (2,5,10))
    print(f"{name:<30}{float(ns):>14.2f}{float(s2)*100:>8.0f}%{float(s5)*100:>8.0f}%{float(s10)*100:>8.0f}%{float(ceil)*100:>8.0f}%")

print("\nN* = total calls sharing the prefix before caching pays. Even the strictest"
      "\n(Anthropic 1-hr write=2×) breaks even at 3 calls; most providers pay from call 2.\n")

# ---- interval: reuse count uncertain → cost band (Anthropic 1-hr, strictest) ----
# A Hermes agent task makes N tool-loop calls reusing an L-token prefix; N in [3,20].
L = 8000
pin,pr,pw = F("5.00"),F("0.50"),F("10.0")
# cache cost(N) = L·pw + (N-1)·L·pr = [L(pw-pr)] + [L·pr]·N   (linear in N)
c0 = L*(pw-pr)/10**6; c1 = L*pr/10**6
def prange(coef0,coef1,lo,hi):
    req={"intent":"polynomial_range",
         "polynomial":{"variable":"N","coefficients":[rn(coef0),rn(coef1)]},
         "domain":{"lower":{"kind":"integer","value":str(lo)},"upper":{"kind":"integer","value":str(hi)}}}
    r=run("interval",req)
    return F(int(r["lower"]["numerator"]),int(r["lower"]["denominator"])), F(int(r["upper"]["numerator"]),int(r["upper"]["denominator"]))
print(f"Reuse uncertain (N∈[3,20]) for an {L}-token agent prefix, Anthropic 1-hr TTL (via interval):")
clo,chi = prange(c0, c1, 3, 20)
nlo,nhi = prange(F(0), L*pin/10**6, 3, 20)
print(f"  cache     ${float(clo):.3f} … ${float(chi):.3f}  per task (3…20 reuses)")
print(f"  no-cache  ${float(nlo):.3f} … ${float(nhi):.3f}  per task")
print(f"  → at 20 reuses, caching cuts the prefix bill {(1-float(chi)/float(nhi))*100:.0f}%.")
