# Finite-state counterexamples to Ross's second queueing conjecture

**Yitzchak Shmalo**  
Einstein Institute of Mathematics, The Hebrew University of Jerusalem

[Paper PDF](paper/Shmalo_Ross_Second_Conjecture.pdf) · [LaTeX and verification package](paper/Shmalo_Ross_AAP_Source.zip) · [Single-file LaTeX source](main.tex) · [Proof scope and literature review](REVIEW.md)

The precise source question is Problem 1 in the journal version of L. Leskelä, *Ross's second conjecture and supermodular stochastic ordering*, **Queueing Systems 100 (2022), 213–215**, DOI [10.1007/s11134-022-09824-0](https://doi.org/10.1007/s11134-022-09824-0). The paper concerns mean stationary workload under Cox arrivals with intensity `epsilon F(c t)`, independent identically distributed service requirements, and a rate-one server. It refutes universal monotonicity in the environmental speed `c`.

## Main results

- **64 states, positive rates, continuous service:** for service uniform on `[0.99,1.01]` and `0 < epsilon <= 10^-4`, the explicit environment satisfies `w(3 pi) - w(2 pi) > epsilon^2 / 600`.
- **Positive autocovariance at every lag:** an explicit 128-state environment with all off-diagonal rates positive and the same continuous service law satisfies `w(3 pi) - w(2 pi) > epsilon^2 / 500` for `0 < epsilon <= 10^-5`, despite strictly positive intensity autocovariance at every lag.
- **Arbitrarily many sampled reversals:** for each prescribed integer `N`, one finite-state environment and one bounded continuous service law yield `N` quantitatively separated peaks in a specified finite sequence of workload means. The environment depends on `N`; no fixed-environment infinite-oscillation assertion is made.
- **Finite-second-moment expansion:** a nonnegative explicit third-order remainder is uniform in modulation speed; bounded service is not required for the expansion.
- **Exact universal second-order service criterion:** the coefficient is nonincreasing for every bounded mean-square-continuous stationary environment exactly when `H_B(s) = E[1-cos(s B)]/s^2` is nonincreasing. Finite-state intensities with positive rates suffice to test this condition. Exponential mixtures satisfy it. This is not an all-traffic monotonicity theorem.

The manuscript also contains the averaged-environment variance formulation, the fixed-speed-pair light-traffic comparison for reversible chains, and an exact Palm identity transferring workload reversals to customer waiting times.

## Reproduce

Python 3.10 or later, standard library only:

```sh
python verify.py
```

The checker verifies the rational constants, 16,384 finite marked configurations, 86,016 insertion comparisons, and the count and use of all **50 distinct references**. Its floating-point quadratures are labeled diagnostics, not proofs or workload simulations. The general queueing and spectral arguments are written in the manuscript.

The GitHub Actions workflow builds with the official AAP `imsart` author package pinned at `e8642bdd9f3b232b5f9a0c05b8052c90b0ecdf55`. It commits the PDF, matching source ZIP, and `checks.json`. The source ZIP contains `main.tex`, `verify.py`, `checks.json`, `imsart.cls`, and `imsart.sty`. No font files are distributed. With these files in one directory:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

## Status

The manuscript uses the AAP author class with its public-preprint option. It has not been submitted or accepted by a journal through this workflow. Complete written proofs and internal arithmetic checks are not external peer review. The September dating issue and the remaining older-literature priority qualifications are recorded in [REVIEW.md](REVIEW.md). Author responsibility, AI contributions, funding, and competing interests are stated in the manuscript.
