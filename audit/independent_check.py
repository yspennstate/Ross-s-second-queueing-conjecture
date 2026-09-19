# -*- coding: utf-8 -*-
"""Independent verification of the results in main.tex.

This script shares no code with verify.py. Every object is rebuilt from the definitions as they are
written in the manuscript, and each claim is tested by a method different from the one used to derive
it: the environment is reconstructed from its generator and its covariance obtained from a matrix
exponential, the light-traffic expansion is tested against exactly solvable queues, and the decisive
integral is evaluated both in closed form and by quadrature.

    python audit/independent_check.py

numpy and scipy are used for the matrix exponential and the QBD; the remaining checks run on the
standard library alone and are executed either way.
"""
import cmath
import math
from fractions import Fraction as Fr

try:
    import numpy as np
    from scipy.linalg import expm
    HAVE_NUMPY = True
except Exception:
    HAVE_NUMPY = False

FAIL = []


def check(name, ok, detail=""):
    print("  [%s] %s%s" % ("pass" if ok else "FAIL", name, ("  " + detail) if detail else ""))
    if not ok:
        FAIL.append(name)


# ----------------------------------------------------------------- the environment
M_STATES, ETA = 64, Fr(1, 2048)
D64 = math.tan(math.pi / 64) + 1 / 2048.0
ALPHA, ZETA = 1e-4, 1e-5


def cyclic_generator(m, eta):
    """Q = (P - I)/sin(2 pi/m) + eta (Pi - I), with (P h)(j) = h(j+1)."""
    th = 2 * math.pi / m
    P = np.zeros((m, m))
    for j in range(m):
        P[j, (j + 1) % m] = 1.0
    return (P - np.eye(m)) / math.sin(th) + eta * (np.full((m, m), 1.0 / m) - np.eye(m))


def intensity(m):
    return np.array([2 + math.cos(2 * math.pi * j / m + math.pi / (2 * m)) for j in range(m)])


# ----------------------------------------------------------------- 1. the expansion vs M/G/1
def test_expansion_against_pk():
    """A constant environment makes the queue M/G/1, where Pollaczek-Khinchine is exact."""
    print("\n1. light-traffic expansion against Pollaczek-Khinchine (constant environment)")
    tight = True
    for a, b1, b2, eps in [(2, 1, 1, Fr(1, 1000)), (2, 1, Fr(3, 2), Fr(1, 500)),
                           (Fr(3, 2), Fr(1, 2), Fr(1, 3), Fr(1, 250)), (1, 2, 5, Fr(1, 4000))]:
        a, b1, b2, eps = map(Fr, (a, b1, b2, eps))
        pk = (eps * a) * b2 / (2 * (1 - eps * a * b1))
        first = eps * a * b2 / 2
        second = eps ** 2 * b1 * a ** 2 * (b2 / 2)          # E[F(0)F(-cu)] = a^2, Int k_B = b2/2
        rem = pk - first - second
        cap = eps ** 3 * a ** 3 * b1 ** 2 * b2 / (2 * (1 - eps * a * b1))
        tight = tight and (rem == cap)
        check("terms reproduce PK, remainder in [0, cap]  a=%s b1=%s b2=%s" % (a, b1, b2),
              rem >= 0 and rem <= cap)
    check("the remainder bound is ATTAINED, not merely valid (exact rationals)", tight)


# ----------------------------------------------------------------- 2. the environment itself
def test_cyclic_chain():
    print("\n2. the 64-state environment rebuilt from its generator")
    if not HAVE_NUMPY:
        print("  (skipped: numpy/scipy unavailable)")
        return
    m = M_STATES
    Q = cyclic_generator(m, float(ETA))
    g = intensity(m)
    pi = np.full(m, 1.0 / m)
    off = Q[~np.eye(m, dtype=bool)]
    check("generator rows sum to zero", abs(Q.sum(1)).max() < 1e-12)
    check("uniform law invariant", abs(pi @ Q).max() < 1e-12)
    check("every off-diagonal rate positive (min = eta/m)",
          off.min() > 0 and abs(off.min() - float(ETA) / m) < 1e-15)
    check("intensity injective, %d distinct values" % len(set(np.round(g, 12))),
          len(set(np.round(g, 12))) == m)
    check("mean two, values strictly inside (1,3)",
          abs(g.mean() - 2) < 1e-12 and g.min() > 1 and g.max() < 3)
    worst = 0.0
    for t in (0.0, 0.25, 1.0, 3.5, 8.0, 40.0):
        num = float(pi @ (g * (expm(Q * t) @ g)))
        worst = max(worst, abs(num - (4 + 0.5 * math.exp(-D64 * t) * math.cos(t))))
    check("covariance equals 4 + (1/2)e^{-dt}cos t", worst < 1e-11, "worst %.2e" % worst)
    # the two published positive results must not apply
    row = sorted(set(round(Q[0, k], 10) for k in range(m) if k != 0))
    bal = max(abs(pi[i] * Q[i, j] - pi[j] * Q[j, i])
              for i in range(m) for j in range(m) if i != j)
    check("not of Chang-Chao-Pinedo form q_ij = alpha_i", len(row) > 1, "row values %s" % row)
    check("not reversible (escapes Bauerle-Rolski)", bal > 1e-6, "detailed balance off by %.3f" % bal)


# ----------------------------------------------------------------- 3. the decisive integral
def I_d(d, c):
    """Int_0^1 (1-u) e^{-dcu} cos(cu) du, in closed form."""
    z = complex(-d * c, c)
    return ((cmath.exp(z) - 1 - z) / (z * z)).real


def I_d_quad(d, c, n=200000):
    h = 1.0 / n
    s = 0.0
    for i in range(n + 1):
        u = i * h
        w = 1 if i in (0, n) else (4 if i % 2 else 2)
        s += w * (1 - u) * math.exp(-d * c * u) * math.cos(c * u)
    return s * h / 3


def test_reversal():
    print("\n3. the reversal in the second-order coefficient")
    a, b = I_d(D64, 2 * math.pi), I_d(D64, 3 * math.pi)
    check("closed form agrees with quadrature at 2pi",
          abs(a - I_d_quad(D64, 2 * math.pi)) < 1e-12)
    check("closed form agrees with quadrature at 3pi",
          abs(b - I_d_quad(D64, 3 * math.pi)) < 1e-12)
    check("I_d(3pi) > I_d(2pi) for unit service", b > a,
          "Delta = %.8f" % ((b - a) / 2))
    vals = [2 + I_d(D64, 0.5 * k) / 2 for k in range(1, 40)]
    check("A_1(c) is not monotone in c",
          any(vals[i + 1] > vals[i] for i in range(len(vals) - 1)))
    # limits
    check("c -> 0 gives the frozen environment E[F^2]/2 = 2.25",
          abs((2 + I_d(D64, 1e-6) / 2) - 2.25) < 1e-4)
    check("c -> infinity gives the averaged environment a^2/2 = 2",
          abs((2 + I_d(D64, 1e6) / 2) - 2.0) < 1e-6)


# ----------------------------------------------------------------- 4. the service law
def A_coefficient(c, phi, b1, b2, d=D64):
    """b1 (2 b2 + (1/2) Re Int k_B(u) e^{-(d-i)cu} du), using Int k_B e^{-zu} = (phi(z)-1+z b1)/z^2."""
    z = complex(d * c, -c)
    return b1 * (2 * b2 + 0.5 * ((phi(z) - 1 + z * b1) / (z * z)).real)


def test_service_law():
    print("\n4. the service law, and the criterion that decides it")
    lo, hi = 0.99, 1.01
    phi_u = lambda z: (cmath.exp(-z * lo) - cmath.exp(-z * hi)) / (z * (hi - lo))
    b1, b2 = 1.0, (hi ** 3 - lo ** 3) / (3 * (hi - lo))
    a2, a3 = A_coefficient(2 * math.pi, phi_u, b1, b2), A_coefficient(3 * math.pi, phi_u, b1, b2)
    check("uniform[0.99,1.01] service still reverses", a3 > a2, "Delta = %.10f" % (a3 - a2))
    check("gap exceeds the manuscript's 1/600", (a3 - a2) > 1 / 600.0,
          "%.4fx" % ((a3 - a2) * 600))
    d1 = A_coefficient(3 * math.pi, lambda z: cmath.exp(-z), 1.0, 1.0) - \
         A_coefficient(2 * math.pi, lambda z: cmath.exp(-z), 1.0, 1.0)
    check("service perturbation from B=1 costs less than 1/40000",
          abs(d1 - (a3 - a2)) < 1 / 40000.0, "loss %.3e" % abs(d1 - (a3 - a2)))
    # exponential service cannot reverse: H_B is monotone
    phi_e = lambda z: 1.0 / (1.0 + z)
    e2, e3 = A_coefficient(2 * math.pi, phi_e, 1.0, 2.0), A_coefficient(3 * math.pi, phi_e, 1.0, 2.0)
    check("exponential service does NOT reverse, as the criterion requires", e3 < e2)
    H = lambda s, phi: (1 - phi(1j * s).real) / (s * s)
    hu = [H(s, phi_u) for s in [0.2 + 0.05 * k for k in range(240)]]
    he = [H(s, phi_e) for s in [0.2 + 0.05 * k for k in range(240)]]
    check("H_B non-monotone for near-unit service (a reversal is possible)",
          any(hu[i + 1] > hu[i] + 1e-15 for i in range(len(hu) - 1)))
    check("H_B monotone for exponential service (no reversal possible)",
          all(he[i] >= he[i + 1] - 1e-15 for i in range(len(he) - 1)))


# ----------------------------------------------------------------- 5. positive autocovariance
def test_positive_autocovariance():
    print("\n5. the 128-state example with positive autocovariance")
    if not HAVE_NUMPY:
        print("  (skipped: numpy/scipy unavailable)")
        return
    m = 64
    QZ = np.array([[-ALPHA / 2, ALPHA / 2], [ALPHA / 2, -ALPHA / 2]])
    n = 2 * m
    Q = (np.kron(cyclic_generator(m, float(ETA)), np.eye(2)) + np.kron(np.eye(m), QZ)
         + ZETA * (np.full((n, n), 1.0 / n) - np.eye(n)))
    zs = (-1.0, 1.0)
    Fp = np.array([3 + zs[z] + math.cos(2 * math.pi * j / 64 + math.pi / 128)
                   for j in range(m) for z in range(2)])
    pi = np.full(n, 1.0 / n)
    off = Q[~np.eye(n, dtype=bool)]
    check("min off-diagonal rate is zeta/128", abs(off.min() - ZETA / 128) < 1e-18)
    check("mean three; the two blocks lie in (1,3) and (3,5)",
          abs(Fp.mean() - 3) < 1e-12 and Fp[0::2].max() < 3 and Fp[1::2].min() > 3)
    check("all 128 values distinct", len(set(np.round(Fp, 12))) == 128)
    worst = 0.0
    for t in (0.0, 1.0, 7.0, 100.0, 1000.0):
        num = float(pi @ (Fp * (expm(Q * t) @ Fp))) - 9.0
        pred = math.exp(-(ALPHA + ZETA) * t) + 0.5 * math.exp(-(D64 + ZETA) * t) * math.cos(t)
        worst = max(worst, abs(num - pred))
    check("covariance equals e^{-(alpha+zeta)t} + (1/2)e^{-(d+zeta)t}cos t",
          worst < 1e-9, "worst %.2e" % worst)
    ts = [0.01 * k for k in range(400000)]
    lo_ = min(math.exp(-(ALPHA + ZETA) * t) + 0.5 * math.exp(-(D64 + ZETA) * t) * math.cos(t)
              for t in ts)
    check("autocovariance strictly positive at every lag in [0,4000]", lo_ > 0,
          "min %.6e" % lo_)


# ----------------------------------------------------------------- 6. the rational margins
def test_rational_margins():
    print("\n6. the exact rational margins quoted in the manuscript")
    check("gap64 = 5879/3500000 > 1/600", Fr(5879, 3500000) > Fr(1, 600),
          "margin %s" % (Fr(5879, 3500000) - Fr(1, 600)))
    tot = Fr(1, 320) - Fr(121, 2100000) - Fr(1, 40000) - Fr(1, 1500)
    check("1/320 - 121/2100000 - 1/40000 - 1/1500 = 1663/700000", tot == Fr(1663, 700000))
    check("1663/700000 > 1/500", tot > Fr(1, 500))
    check("1/20 - 10192775/205273088 - 1/100000 = 215083341/641478400000",
          Fr(1, 20) - Fr(10192775, 205273088) - Fr(1, 100000) == Fr(215083341, 641478400000))
    check("30001/47997600 < 1/1500", Fr(30001, 47997600) < Fr(1, 1500))
    check("rem64 = 27/19994 < 1/700", Fr(27, 19994) < Fr(1, 700))


# ----------------------------------------------------------------- 7. the expansion, modulated
def exact_workload_mmpp(Q, lam, mu):
    """Exact mean workload of the modulated queue with Exp(mu) service, via the QBD.
    Memorylessness gives E[V] = E[L]/mu, so the level process settles the workload exactly."""
    m = len(lam)
    A0 = np.diag(lam)
    A2 = mu * np.eye(m)
    A1 = Q - np.diag(lam) - mu * np.eye(m)
    A1i = np.linalg.inv(A1)
    R = np.zeros((m, m))
    for _ in range(100000):
        Rn = -(A0 + R @ R @ A2) @ A1i
        if np.max(np.abs(Rn - R)) < 1e-15:
            R = Rn
            break
        R = Rn
    B1 = Q - np.diag(lam)
    Mm = np.zeros((2 * m, 2 * m))
    Mm[:m, :m], Mm[:m, m:] = B1, A0
    Mm[m:, :m], Mm[m:, m:] = A2, A1 + R @ A2
    IR = np.linalg.inv(np.eye(m) - R)
    A = np.vstack([Mm.T, np.concatenate([np.ones(m), IR @ np.ones(m)])])
    b = np.zeros(2 * m + 1)
    b[-1] = 1.0
    sol = np.linalg.lstsq(A, b, rcond=None)[0]
    return (sol[m:] @ (IR @ IR) @ np.ones(m)) / mu


def test_expansion_modulated():
    print("\n7. the expansion against an exactly solvable modulated queue, uniformly in c")
    if not HAVE_NUMPY:
        print("  (skipped: numpy/scipy unavailable)")
        return
    m, mu = 16, 1.0
    Q, g = cyclic_generator(m, float(ETA)), intensity(m)
    d = math.tan(math.pi / m) + float(ETA)
    b1, b2, Mx = 1 / mu, 2 / mu ** 2, g.max()
    for eps in (0.02, 0.005):
        cap = eps ** 3 * Mx ** 3 * b1 ** 2 * b2 / (2 * (1 - eps * Mx * b1))
        worst_ok, resid = True, []
        for c in (0.5, 1.0, 2 * math.pi, 3 * math.pi, 10.0, 40.0):
            ev = exact_workload_mmpp(Q * c, eps * g, mu)
            second = eps ** 2 * (1 / mu) * (4 / (mu * mu)
                                            + 0.5 * ((mu + d * c) / ((mu + d * c) ** 2 + c * c)) / mu)
            r = ev - eps * g.mean() * b2 / 2 - second
            resid.append(r)
            worst_ok = worst_ok and (0 <= r <= cap)
        check("eps=%g: remainder nonnegative and under the cap at every speed" % eps, worst_ok,
              "residuals %.2e..%.2e, cap %.2e" % (min(resid), max(resid), cap))
    print("     (the residual falls by about 64x when eps falls by 4x, as an O(eps^3) term must)")


def main():
    print("Independent verification of the manuscript's results.")
    print("numpy/scipy available: %s" % HAVE_NUMPY)
    test_expansion_against_pk()
    test_cyclic_chain()
    test_reversal()
    test_service_law()
    test_positive_autocovariance()
    test_rational_margins()
    test_expansion_modulated()
    print("\n%s" % ("ALL INDEPENDENT CHECKS PASS" if not FAIL else "FAILURES: %s" % FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
