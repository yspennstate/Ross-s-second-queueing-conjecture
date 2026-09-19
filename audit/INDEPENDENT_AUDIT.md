# Independent audit

Date: 19 September 2026.

This note records a verification of the manuscript carried out separately from `verify.py`. It
shares no code with that script. Every object was rebuilt from the definitions as they appear in
`main.tex`, and each claim was tested by a route different from the one used to derive it. Files:

- `audit/independent_check.py` — the reconstruction, 34 checks, standard library plus numpy/scipy
- `lean/Insertion.lean` — a machine-checked proof of the deterministic core, core Lean 4
- `lean/model_agreement.py` — evidence that the Lean definitions are the ones `verify.py` evaluates

## Testing the expansion against queues whose answer is already known

The light-traffic expansion of Theorem 2.1 is the step that carries the counterexample: without a
remainder that is nonnegative and bounded uniformly in the modulation speed, a gap in the
second-order coefficient says nothing about the workload. Two exactly solvable cases were used to
test it from outside.

**A constant environment.** Setting `F = a` makes the queue M/G/1, where Pollaczek–Khinchine is
exact. The expansion reproduces the first two terms exactly, and the true remainder equals the
upper bound `eps^3 M^3 b1^2 b2 / (2(1 - eps M b1))` **as exact rationals**, not merely to within it.
The bound of Theorem 2.1 is therefore attained, and the constant environment is the case that
attains it.

**A modulated environment.** A Markov-modulated arrival stream with exponential service is a
quasi-birth-death process, and memorylessness gives `E[V] = E[L]/mu`, so the mean workload can be
computed exactly rather than simulated. Solving it for the cyclic environment at speeds
`c = 0.5, 1, 2pi, 3pi, 10, 40` and at `eps = 0.02` and `0.005`: the residual is nonnegative at every
speed, below the stated cap at every speed, and falls by a factor 66 when `eps` falls by 4, against
the factor 64 an `O(eps^3)` term requires.

## The environment and the reversal

The 64-state chain was rebuilt from its generator. Rows sum to zero, the uniform law is invariant,
every off-diagonal rate is positive with minimum exactly `eta/m`, the intensity takes 64 distinct
values strictly inside `(1,3)` with mean two, and the covariance `4 + (1/2)e^{-d|t|}cos t` is
reproduced to `1e-12` by matrix exponential at a range of lags. The 128-state chain reproduces its
covariance to `5e-11`, and its autocovariance is positive at every lag examined, with minimum
`0.571` over `[0, 4000]`.

The decisive integral was evaluated in closed form and by Simpson quadrature, agreeing to `1e-16`:
`I_d(2pi) = 0.0146`, `I_d(3pi) = 0.0234`. With the manuscript's service law, uniform on
`[0.99, 1.01]`, the coefficient gap is `0.0043968`, which is 2.64 times the `1/600` the argument
needs; the loss against unit service is `1.1e-5`, inside the `1/40000` allowed by Lemma 5.2. Every
rational margin quoted in the manuscript reproduces exactly, including `5879/3500000`,
`1663/700000`, `215083341/641478400000` and `30001/47997600`. The limits are as they should be:
`A_1(c)` tends to `E[F^2]/2 = 2.25` as `c` tends to zero and to `a^2/2 = 2` as `c` grows.

## Consistency with the positive results in the literature

A counterexample has to fail the hypotheses of every theorem that proves the ordering, and this one
does, by construction rather than by accident. Detailed balance fails by `0.159`, so the environment
is not reversible and the Bäuerle–Rolski conditions do not apply. The off-diagonal rates in a row
take two values, `10.20` and `7.6e-6`, so the environment is not of the form `q_ij = alpha_i`
studied by Chang, Chao and Pinedo.

Two further observations support the service criterion of Section 6 rather than merely restating it.
Exponential service produces no reversal at all, in the exact quasi-birth-death computation above
and in the coefficient; this is what the criterion predicts, since `H_B(s) = 1/(mu^2 + s^2)` is
monotone. Erlang-`k` service reverses only once it is concentrated enough: the sign changes between
`k = 40` and `k = 100` and the gap tends to the deterministic value `0.0044` as `k` grows.
Similarly, the reversal needs `d` below about `0.09`, and since `d = tan(pi/m) + eta`, a 16-state
cycle cannot exhibit it and a 32-state cycle is marginal. The state count in Theorem 3.1 is a real
constraint, not a convenience.

## The deterministic core, machine-checked

`verify.py` samples the insertion facts of Section 2 on a finite grid and labels them in its own
output as "finite-grid regression, not the general proof". `lean/Insertion.lean` proves the
load-bearing one in general, in core Lean 4 with no Mathlib:

```
theorem shot_le_workload (cfg : List Arrival) : shot cfg ≤ workload cfg
```

for arbitrarily many arrivals with arbitrary nonnegative ages and marks; the increasing-age
hypothesis is not needed. `shot_le_total` and `workload_le_total` are proved alongside it. The
theorems depend only on `propext` and `Quot.sound`; there is no `sorry` and no additional axiom.
`lean/model_agreement.py` checks that the Lean definitions of `workload` and `shot` agree with
`verify.py`'s `workload_and_shot` on all 16,384 configurations of its grid, so the formal statement
concerns the same objects.

## What this audit does not establish

The written proof of Theorem 2.1 was not refereed line by line. What is recorded above is that its
conclusions hold exactly in two solvable regimes and that its deterministic core is now a theorem;
neither is the same as checking the argument as written. The remaining steps of that proof — the
Poisson domination, the stationary construction, and the passage to a finite second service moment
by monotone truncation — rest on point-process facts outside what was formalised here.

No exact end-to-end computation of the counterexample's own workload was performed. It would need
service concentrated enough to reverse, which at 64 environment states puts the quasi-birth-death
system beyond a dense solver.

The effect is small. It holds for `eps` below roughly `3.3e-4`, where the difference in mean
workload is of order `1e-11`. That is sufficient to refute a universal ordering, which is what the
manuscript claims, but the reversal is not of a size that any simulation would show.
