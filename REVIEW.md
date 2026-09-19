# Proof scope and literature review

Date: 19 September 2026.

This note is separate from the research manuscript. It distinguishes written mathematical proofs, exact finite checks, prior-agent contributions, bibliographic verification, and external peer review.

## Source and integration

The source problem is **Problem 1 in the journal version** of Lasse Leskelä, *Ross's second conjecture and supermodular stochastic ordering*, Queueing Systems 100 (2022), 213–215. The target is the mean stationary workload of a rate-one server under Cox intensity `epsilon F(c t)` with independent identically distributed service requirements. Universal ordering in `c` and a necessary-and-sufficient all-traffic characterization are different questions. Only the universal ordering is refuted here; the exact characterization proved in the manuscript concerns the second-order coefficient.

The prior research supplied a 1024-state cyclic counterexample, the bounded-service expansion, the parallel-workload insertion argument, and the variance and Palm formulations. A separate agent's full manuscript supplied the stronger **64-state positive-rate, continuous-service counterexample** and the endpoint identity. That proof was recovered and checked rather than inferred from a status label. It is now Theorem 1.1, with its proof in Section 3.

The current synthesis adds the finite-second-service-moment extension, the **128-state counterexample with positive autocovariance at every lag**, the arbitrary finite repeated-reversal construction, and the exact service-law criterion for universal second-order ordering. These additions have complete arguments in the manuscript and internal checks. They have not received independent human peer review in this workflow.

## Mathematical checks performed

1. The thinning construction preserves Cox input and independent service marks. The uniform Poisson domination establishes stationarity and exponential workload moments for bounded service.
2. Inserting a marked arrival increases the single-server workload by at least its parallel residual service. Therefore the excess over parallel service is nonnegative and insertion-monotone. The square-workload balance and the exact homogeneous-queue excess produce the speed-uniform nonnegative remainder.
3. Service truncation uses monotone convergence of workloads and stop-loss kernels. It does not assume a second moment of the limiting workload. Under `E B^2 < infinity` it establishes a finite mean; exponential moments are claimed only for the bounded-service examples.
4. The cyclic covariance follows from a Fourier eigenfunction. The refresh term shifts the decay rate and makes every off-diagonal rate positive. Injectivity is checked, so the intensity itself, not only a hidden environment, is Markov.
5. The 64-state damping and endpoint bounds, service perturbation loss, and normalized workload margin are rationally checked. The resulting bound is `epsilon^2/600` for `epsilon <= 10^-4`.
6. In the 128-state example, the slow two-state component dominates the possible negative oscillatory covariance at every lag. A separate quantitative bound controls its loss in the workload comparison. The resulting gap is `epsilon^2/500` for `epsilon <= 10^-5`. Positive covariance is not mislabeled as association or a supermodular process order.
7. The repeated-reversal proof handles all integers `N` analytically through `L=N+1`, `m=1024 L^3`, and common rational inequalities. Finite sampled values of `N` in the checker are only regression tests. The theorem is not an assertion of infinitely many oscillations for one fixed environment.
8. The service criterion uses the covariance spectral measure and the identity `integral k_B(u) cos(su) du = E[1-cos(sB)]/s^2`. Necessity is witnessed by finite cyclic chains whose damping tends to zero. Dominated convergence requires only `integral k_B = E B^2/2 < infinity`. The equivalence is for the second-order coefficient, not arbitrary positive traffic.
9. The Palm waiting-time identity follows from compensation, not from applying PASTA to Cox arrivals. It extends to finite-second-moment services by the same monotone truncation.

`verify.py` checks all displayed rational margins, **16,384 marked configurations and 86,016 exact insertion comparisons**, the two-arrival piecewise kernel, and exactly **50 distinct bibliography entries, all cited**. Floating-point quadrature checks are labeled diagnostic. Neither these tests nor a successful LaTeX build amount to formal verification or external peer review.

## Bibliography

The paper has 50 references, including Leskelä's note and all 14 references listed in that note. Citations are attached to their actual uses: Ross-type comparisons, stochastic orderings, classical light-traffic expansions, Cox and point-process foundations, stationary queues, Palm identities, reversible spectral theory, and exponential-mixture service laws. Books are counted as references, not falsely described as journal papers. No uncited padding entries are included.

Publisher, author, and primary-source bibliographic records were used. This is not a claim that every reference was read in full. In particular, the complete Heyman (1982) and Miyoshi–Rolski (2004) texts were not obtained in this workflow, so an exhaustive first-solution priority clearance is not certified.

Useful primary records:

- Leskelä journal article: https://doi.org/10.1007/s11134-022-09824-0
- Journal issue showing the 2022 date and pp. 213–215: https://link.springer.com/journal/11134/volumes-and-issues/100-3
- Author-hosted journal PDF: https://acris.aalto.fi/ws/portalfiles/portal/89616571/Ross_s_second_conjecture_and_supermodular_stochastic_ordering.pdf
- Leskelä's publication list: https://math.aalto.fi/~lleskela/publications.html
- Miyoshi–Rolski publisher issue with pp. 121–131: https://onlinelibrary.wiley.com/toc/1467842x/2004/46/1
- Heyman article: https://doi.org/10.2307/3213936
- Gupta et al. author-hosted paper: https://www.varungupta.info/papers/SIGM06.pdf

The fluctuating-load model in Gupta et al. includes environment-dependent service rates. It must not be identified with the fixed-rate server and independent service requirements of this manuscript. The classical use of light traffic, Palm calculus, or a stationary covariance spectral representation is not claimed as new.

## September 2026 question

The alleged September 2026 item with the exact title *Ross's second conjecture and supermodular stochastic ordering* and pages 213–215 is **the 2022 Leskelä paper**. Its publisher identifies publication on 1 May 2022, volume 100. A current issue date elsewhere on a cumulative journal-index page does not redate this entry. It is not a September 2026 competing disproof.

Bounded searches through 19 September 2026 for the exact title, Ross's second queueing conjecture, counterexample/disproof, and September 2026 did not identify an accessible source-matching external counterexample. Many broad queries returned irrelevant material. A negative search does not prove worldwide absence, and the manuscript does not claim a certified first-publication priority. The historical September 10 research memo recovered in this project concerned a separate three-state supermodular-order result and referred back to the project's earlier cyclic counterexample; it was not evidence of an outside September competitor.

## Annals preparation

The paper uses the official AAP `imsart` class, with its `preprint` option so the public PDF does not falsely state that a journal submission has occurred. The upstream author package is pinned in the build workflow. The manuscript is a single TeX document, with author affiliation, keywords, MSC classifications, acknowledgment and responsibility statement, funding and competing interests, bibliography, and a supplementary-code description.

The workflow does not submit the manuscript to a journal. No acceptance, external referee approval, or exhaustive priority certificate is asserted. The mathematical scope is substantially stronger than the initial single-counterexample note; journal acceptance remains an editorial and peer-review decision.
