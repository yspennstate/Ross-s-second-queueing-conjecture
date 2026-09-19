#!/usr/bin/env python3
"""Exact arithmetic and finite regression checks for the Ross manuscript.

Python 3.10+, standard library only. Run: python verify.py
The analytic proofs are in main.tex. These tests are not a formal verification
of the infinite-history queue or of the universal service-law criterion.
"""
from __future__ import annotations
import argparse
import cmath
import hashlib
import itertools
import json
import math
import re
from fractions import Fraction as F
from pathlib import Path
from typing import Callable, Sequence


def record(x: F) -> dict[str, int | str]:
    return {"numerator": x.numerator, "denominator": x.denominator, "value": str(x)}


def exact_constants() -> dict[str, object]:
    pi_hi = F(22, 7)
    assert pi_hi**2 < 10
    b2 = F(30001, 30000)
    x0 = F(11, 224)
    damping = x0 / (1-x0**2/2) + F(1, 2048)
    assert damping == F(10192775, 205273088) < F(1, 20)
    endpoint = -F(1, 720) + F(399*400, 720*401**2)*F(23, 7)
    assert endpoint == F(363599, 115776720) > F(1, 320)
    assert endpoint-F(1, 320) == F(7187, 463106880)
    eps64 = F(1, 10000)
    rem64 = 27*eps64/(2*(1-3*eps64))
    assert rem64 == F(27, 19994) < F(1, 700)
    gap64 = F(1, 320)-F(1, 60000)-b2/700
    assert gap64 == F(5879, 3500000) > F(1, 600)
    assert gap64-F(1, 600) == F(137, 10500000)
    alpha, zeta = F(1, 10000), F(1, 100000)
    assert damping+zeta < F(1, 20)
    assert F(1, 20)-damping-zeta == F(215083341, 641478400000)
    assert alpha < F(3, 64)
    telegraph_loss = (alpha+zeta)*pi_hi/6
    assert telegraph_loss == F(121, 2100000)
    eps128 = F(1, 100000)
    rem128 = 125*eps128*b2/(2*(1-5*eps128))
    assert rem128 == F(30001, 47997600) < F(1, 1500)
    gap128 = F(1, 320)-telegraph_loss-F(1, 40000)-F(1, 1500)
    assert gap128 == F(1663, 700000) > F(1, 500)
    assert gap128-F(1, 500) == F(263, 700000)
    many = F(1, 40)-F(1, 96)-F(1, 60000)-b2/700
    assert many == F(275899, 21000000) > F(1, 100)
    for N in (1, 2, 3, 10, 100, 1000):
        L = N+1
        m = 1024*L**3
        assert F(32*L, 3*m) == F(1, 96*L**2)
        eps = F(1, 10000*L**2)
        b2L = 1+F(1, 30000*L**2)
        assert 27*eps*b2L/(2*(1-3*eps)) < b2/(700*L**2)
    return {
        "analytic_inputs": ["3 < pi < 22/7", "sin(x) <= x", "cos(x) >= 1-x^2/2",
            "exp(-x) >= 1-x for x>=0", "0 <= 1-exp(-x) <= x for x>=0",
            "tan(x)<2x on (0,pi/4); tan(x)>x on (0,pi/2)"],
        "damping_64_upper_bound": record(damping),
        "endpoint_gap_lower_bound": record(endpoint),
        "normalized_64_workload_gap_lower_bound": record(gap64),
        "normalized_64_claimed_bound": record(F(1,600)),
        "damping_128_upper_bound": record(damping+zeta),
        "telegraph_gap_loss_upper_bound": record(telegraph_loss),
        "normalized_128_remainder_upper_bound": record(rem128),
        "normalized_128_workload_gap_lower_bound": record(gap128),
        "normalized_128_claimed_bound": record(F(1,500)),
        "many_reversals_constant": record(many),
        "many_reversals_claimed_constant": record(F(1,100)),
        "waiting_gap_64_coefficient": record(F(1,1200)),
        "waiting_gap_128_coefficient": record(F(1,1500))}


def workload_and_shot(ages: Sequence[int], marks: Sequence[int]) -> tuple[int,int]:
    """Quarter-unit finite workloads. Zero mark means no arrival."""
    if len(ages) != len(marks):
        raise ValueError("Ages and marks must have equal lengths")
    if any(a <= 0 for a in ages) or any(a >= b for a,b in zip(ages,ages[1:])):
        raise ValueError("Ages must be positive and strictly increasing")
    total = workload = shot = 0
    for age, mark in zip(ages, marks):
        if mark < 0:
            raise ValueError("Service marks must be nonnegative")
        if mark:
            total += mark
            workload = max(workload, total-age)
            shot += max(mark-age, 0)
    return workload, shot


def insertion_checks() -> dict[str,object]:
    ages = (1,2,3,4,5,6,8)
    choices = (0,2,4,6)
    configs = list(itertools.product(choices, repeat=len(ages)))
    values = {m: workload_and_shot(ages,m) for m in configs}
    comparisons = 0
    for marks in configs:
        v,s = values[marks]
        assert v >= s
        for j,mark in enumerate(marks):
            if mark:
                continue
            for new_mark in choices[1:]:
                updated = marks[:j]+(new_mark,)+marks[j+1:]
                vp,sp = values[updated]
                assert vp-v >= max(new_mark-ages[j],0)
                assert vp-sp >= v-s
                comparisons += 1
    assert len(configs)==16384 and comparisons==86016
    return {"scope":"finite-grid regression, not the general proof",
            "configurations":len(configs),"single_insertion_comparisons":comparisons,
            "ages":[str(F(a,4)) for a in ages],"service_marks":["1/2","1","3/2"],"status":"PASS"}


def pair_checks() -> dict[str,object]:
    separations = (F(0),F(1,4),F(1,2),F(9,10),F(1),F(5,4),F(2))
    comparisons = 0
    for v in separations:
        breaks = sorted({F(0),F(1),F(3),max(F(0),1-v),max(F(0),2-v)})
        points = set(breaks)
        points.update((x+y)/2 for x,y in zip(breaks,breaks[1:]))
        for y in points:
            direct = max(F(0),1-y,2-y-v)-max(F(0),1-y)-max(F(0),1-y-v)
            piece = F(0) if v>=1 or y>=2-v else y if y<=1-v else 1-v if y<=1 else 2-v-y
            assert direct == piece
            comparisons += 1
        integral = F(0) if v>=1 else (1-v)**2/2+v*(1-v)+(1-v)**2/2
        assert integral == max(F(0),1-v)
    return {"point_comparisons":comparisons,"rational_separations":[str(x) for x in separations],"status":"PASS"}


def simpson(fn: Callable[[float],float], lo: float, hi: float, n: int=20000) -> float:
    if n<=0 or n%2:
        raise ValueError("Simpson panels must be positive and even")
    h=(hi-lo)/n
    total=fn(lo)+fn(hi)
    total+=4*math.fsum(fn(lo+j*h) for j in range(1,n,2))
    total+=2*math.fsum(fn(lo+j*h) for j in range(2,n,2))
    return h*total/3


def diagnostics() -> dict[str,object]:
    d=math.tan(math.pi/64)+1/2048
    c1,c2=2*math.pi,3*math.pi
    def I(c: float) -> float:
        z=c*complex(d,-1)
        return ((z-1+cmath.exp(-z))/z**2).real
    direct=(I(c2)-I(c1))/2
    formula=-d/(12*math.pi*(1+d*d))+(1-d*d)/(72*math.pi**2*(1+d*d)**2)*(-5+4*math.exp(-3*math.pi*d)+9*math.exp(-2*math.pi*d))
    quad=simpson(lambda u:.5*(1-u)*(math.exp(-d*c2*u)*math.cos(c2*u)-math.exp(-d*c1*u)*math.cos(c1*u)),0,1)
    assert abs(direct-formula)<1e-13 and abs(direct-quad)<1e-11
    def kernel(u: float) -> float:
        if u<=.99:
            return 1-u
        if u<1.01:
            return (1.01-u)**2/.04
        return 0.
    def gap(cov: Callable[[float],float]) -> float:
        fn=lambda u:kernel(u)*(cov(c2*u)-cov(c1*u))
        return simpson(fn,0,.99)+simpson(fn,.99,1.01)
    gap64=gap(lambda t:.5*math.exp(-d*t)*math.cos(t))
    alpha,zeta=1e-4,1e-5
    kp=lambda t:math.exp(-(alpha+zeta)*t)+.5*math.exp(-(d+zeta)*t)*math.cos(t)
    gap128=gap(kp)
    for t in (0.,.1,1.,math.pi,2*math.pi,100.,1000.):
        assert kp(t)>=.5*math.exp(-(alpha+zeta)*t)-1e-15
    for s in (.1,1.,3.,10.):
        q=2.
        numerical=simpson(lambda u:math.exp(-q*u)/q*math.cos(s*u),0,30)
        assert abs(numerical-1/(q*q+s*s))<1e-8
    return {"scope":"floating-point diagnostics, not simulated workloads or interval certificates",
            "damping_64":d,"unit_coefficient_gap_64":direct,"endpoint_formula_gap_64":formula,
            "independent_quadrature_gap_64":quad,"continuous_service_coefficient_gap_64":gap64,
            "continuous_service_coefficient_gap_128":gap128,
            "finite_covariance_and_exponential_service_checks":"PASS"}


def manuscript_checks(path: Path) -> dict[str,object]:
    text=path.read_text(encoding="utf-8")
    keys=re.findall(r"\\bibitem\{([^}]+)\}",text)
    cited={k.strip() for group in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}",text) for k in group.split(",")}
    assert len(keys)==len(set(keys))==50
    assert set(keys)==cited
    labels=re.findall(r"\\label\{([^}]+)\}",text)
    refs=re.findall(r"\\(?:eqref|ref)\{([^}]+)\}",text)
    assert len(labels)==len(set(labels)) and set(refs)<=set(labels)
    assert "The author has reviewed the manuscript and its proofs" in text
    assert not any(ord(c)<32 and c not in "\n\r\t" for c in text)
    return {"unique_references":50,"all_references_cited":True,
            "duplicate_labels":False,"all_crossreference_labels_present":True}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path(__file__).with_name("checks.json"))
    args=parser.parse_args()
    manuscript=Path(__file__).with_name("main.tex")
    result={"paper":"Finite-state counterexamples to Ross's second queueing conjecture",
            "scope":"Finite arithmetic and regression checks; analytic proofs are in main.tex",
            "exact_constants":exact_constants(),"marked_insertion_tests":insertion_checks(),
            "two_arrival_kernel_tests":pair_checks(),"floating_point_diagnostics":diagnostics(),
            "script_sha256":digest(Path(__file__)),"status":"ALL_FINITE_CHECKS_PASS"}
    if manuscript.exists():
        result["manuscript_sha256"]=digest(manuscript)
        result["manuscript_structure"]=manuscript_checks(manuscript)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("ALL_FINITE_CHECKS_PASS")
    print("16,384 configurations; 86,016 exact insertion comparisons.")
    print("64-state, positive-covariance and repeated-reversal constants are positive.")
    print("Exactly 50 distinct references, all cited, when main.tex is present.")
    print(f"Results: {args.output}")


if __name__=="__main__":
    main()
