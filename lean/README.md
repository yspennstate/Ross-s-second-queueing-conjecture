# Machine-checked core of the light-traffic expansion

`Insertion.lean` proves, in Lean 4, the deterministic fact that makes the remainder in
Theorem 2.1 nonnegative. It needs no Mathlib and no build system: one file, one command.

```sh
lean lean/Insertion.lean
```

Checked with Lean 4.34.0 (`x86_64-w64-windows-gnu`, commit `293d5d0c`). Any Lean 4 of that
vintage will do; nothing here uses recent syntax.

## What is proved

The manuscript compares two ways of serving the same marked configuration of arrivals. One
rate-one server pools all the work; alternatively each customer gets its own rate-one server and
leaves behind a residual `(m - a)_+`. Write `V` for the first and `S` for the second. The expansion
in Section 2 needs

```
S ≤ V
```

so that the excess `V - S` is nonnegative, and with it the remainder `R` in the expansion. The file
proves exactly that:

| theorem | statement |
| --- | --- |
| `shot_le_workload` | `shot cfg ≤ workload cfg` — the excess over parallel service is nonnegative |
| `shot_le_total` | `shot cfg ≤ total cfg` — parallel service never exceeds the work that arrived |
| `workload_le_total` | `workload cfg ≤ total cfg` |
| `shot_zero_or_le` | the induction hypothesis that carries `shot_le_workload` |

These hold for arbitrarily many arrivals with arbitrary nonnegative ages and marks. The
increasing-age hypothesis used elsewhere in the paper turns out not to be needed for them.

## Why a proof and not a test

`verify.py` evaluates the same inequality on a grid of seven ages and four mark values, and is
explicit in its own output about the limits of that:

```
"scope": "finite-grid regression, not the general proof"
```

16,384 configurations is a regression test, not a theorem. The Lean file removes the restriction to
that grid.

## The definitions

Reich's recursion is transcribed directly. `run cfg T w` walks the configuration carrying the
running total `T` of service marks and the running maximum `w` of `total - age`:

```lean
def run : List Arrival → Nat → Nat → Nat × Nat
  | [],           T, w => (T, w)
  | (a, m) :: xs, T, w => run xs (T + m) (max w (T + m - a))
```

Natural-number subtraction is truncated, so `x - y` means `(x - y)₊`. That is the same convention
`verify.py` uses: `max(mark - age, 0)`, and a running maximum started at zero.

`shot` sums the parallel residuals; `workload` and `total` read the two components off `run`.

## The shape of the argument

Proving `S ≤ V` is easy from the oldest arrival backwards: the last customer still in parallel
service has a prefix total that absorbs every earlier residual. But `run` recurses from the
youngest arrival forwards, so that argument does not fit the recursion.

`shot_zero_or_le` is the restatement that does fit. Along any run, either nothing behind the
current point is still in parallel service, or the carried maximum already dominates the head start
plus the whole parallel workload:

```lean
theorem shot_zero_or_le (ys : List Arrival) :
    ∀ T w, shot ys = 0 ∨ T + shot ys ≤ (run ys T w).2
```

The left branch carries the induction until the first arrival with a positive residual appears; from
there the right branch holds and stays true, because each later step only adds to the total. The
main theorem is the case `T = w = 0`.

## Two checks to run yourself

**No holes.** The file ends with an axiom audit, so running it prints:

```
'RossInsertion.shot_le_workload' depends on axioms: [propext, Quot.sound]
'RossInsertion.shot_le_total' depends on axioms: [propext, Quot.sound]
'RossInsertion.workload_le_total' depends on axioms: [propext, Quot.sound]
'RossInsertion.shot_zero_or_le' depends on axioms: [propext, Quot.sound]
```

`propext` and `Quot.sound` are two of Lean's three standard axioms. `sorryAx` does not appear, so
nothing is assumed and no step is stubbed out.

**The right objects.** A proof about definitions that merely look like the paper's would be worth
nothing. `model_agreement.py` transcribes the Lean definitions back into Python and compares them
against `verify.py`'s own `workload_and_shot` on the whole grid:

```sh
python lean/model_agreement.py
```

```
the Lean definitions agree with verify.py's workload_and_shot on all 16384 configurations
and the proved inequalities shot <= workload <= total hold on every one of them
```

## What is not proved here

Only the deterministic core. The rest of Theorem 2.1 — the Poisson domination, the stationary
construction from the infinite past, the passage to a finite second service moment by monotone
truncation — is probabilistic and is not formalised. Two further deterministic facts that
`verify.py` also samples, the insertion gain `V' - V ≥ (m - a)₊` and the insertion-monotonicity of
the excess `V' - S' ≥ V - S`, are left as written proofs in the manuscript; the second follows from
the first.

Nothing in this directory bears on the counterexamples themselves, which are checked numerically in
`audit/independent_check.py` and argued in `main.tex`.
