# -*- coding: utf-8 -*-
"""The Lean file proves theorems about `run`, `workload` and `shot`.  Those are only worth
something if they are the same objects `verify.py` evaluates.  This transcribes the Lean
definitions literally into Python and compares them with `verify.py`'s `workload_and_shot`
on the whole grid it checks: 7 ages, 4 mark values, 16,384 configurations.

    python lean/model_agreement.py
"""
import importlib.util
import itertools
import os
import sys


def lean_run(cfg, T, w):
    """Literal transcription of `RossInsertion.run`; Nat subtraction is truncated."""
    for (a, m) in cfg:
        T = T + m
        w = max(w, max(0, T - a))
    return T, w


def lean_workload(cfg):
    return lean_run(cfg, 0, 0)[1]


def lean_total(cfg):
    return lean_run(cfg, 0, 0)[0]


def lean_shot(cfg):
    return sum(max(0, m - a) for (a, m) in cfg)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("v", os.path.join(here, os.pardir, "verify.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)

    ages = (1, 2, 3, 4, 5, 6, 8)
    choices = (0, 2, 4, 6)
    n = 0
    for marks in itertools.product(choices, repeat=len(ages)):
        vw, vs = v.workload_and_shot(ages, marks)
        cfg = list(zip(ages, marks))
        lw, ls = lean_workload(cfg), lean_shot(cfg)
        if (vw, vs) != (lw, ls):
            print("MISMATCH at %s: verify.py=(%d,%d) lean=(%d,%d)" % (marks, vw, vs, lw, ls))
            return 1
        # the three properties the Lean file proves, re-evaluated here
        assert ls <= lw, marks
        assert lw <= lean_total(cfg), marks
        n += 1
    print("the Lean definitions agree with verify.py's workload_and_shot on all %d configurations" % n)
    print("and the proved inequalities shot <= workload <= total hold on every one of them")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
