# Taylor–Greedy: Extended Controlled Benchmark

**Date:** 23 November 2026

## Executive result

On 180 planted-satisfiable random 3-SAT tests (5 sizes × 12 generated instances × 3 starts), the selective third-order Taylor–Greedy heuristic improved upon ordinary single-start greedy in each size but lost substantially to a WalkSAT-style SAT-specific randomized baseline, which found a satisfying assignment in all 180 attempts under the candidate-score cap. None of this establishes complexity-class results or security implications.

## Experimental setup

- **Workload:** Planted satisfiable 3-SAT; N=12,20,32,48,64; 4.3N clauses, each clause uses three distinct variables; planted assignments are **hidden** from optimizers.
- **Methods:** Six algorithms, all using the same starting assignments for each case, and fixed pseudorandom seeds.
- **Budget:** At most 5,000 scored candidate moves per attempt. This is not equivalent to equal wall-clock time or arithmetic work; recorded CPU times supplement candidate counts.
- **Certificate:** A satisfying planted assignment exists by construction, so success E=0 is globally optimal. Algorithms are **not** given the planted assignment.
- **Taylor math:** The multilinear violated-clause function is degree three. Taylor derivatives of degrees 1, 2, 3 are exact, and 1,440 independently tested gain calculations matched direct recomputation. A third-order model is already globally exact in *function representation*; it is not a global optimizer.
- **Algorithm definitions:** First-order greedy only; greedy + restarts; exhaustive 2-flip lookahead plus restarts; interaction-ranked subset of 16 variables with exact Taylor gains for pairs/triples plus restarts; random 2-flip escape kicks; WalkSAT-style clause-focused stochastic flips at noise 0.5.
- **Controls:** All methods were seeded deterministically and assigned shared starting states. Repeated starts of a single instance are not independent problem draws.

## Results: success at exact optimum

| Variables | Single greedy | Greedy + restart | Exact 2-flip + restart | Selective Taylor-3 + restart | Greedy + kicks | WalkSAT-style |
|---:|---:|---:|---:|---:|---:|---:|
| 12 | 15/36 | 36/36 | 36/36 | 36/36 | 36/36 | 36/36 |
| 20 | 6/36 | 34/36 | 34/36 | 34/36 | 34/36 | 36/36 |
| 32 | 3/36 | 27/36 | 20/36 | 19/36 | 30/36 | 36/36 |
| 48 | 2/36 | 7/36 | 11/36 | 11/36 | 16/36 | 36/36 |
| 64 | 0/36 | 1/36 | 0/36 | 1/36 | 4/36 | 36/36 |

## Median computational work

| Variables | Method | Median candidate scores | Median CPU time (ms) | Median remaining unsatisfied clauses |
|---:|---|---:|---:|---:|
| 12 | Single-start greedy (1-flip) | 36 | 0.13 | 1.0 |
| 12 | Greedy + random restarts | 60 | 0.27 | 0.0 |
| 12 | Greedy + exact 2-flip lookahead + restarts | 102 | 0.16 | 0.0 |
| 12 | Selective 3rd-order Taylor–Greedy + restarts | 102 | 0.19 | 0.0 |
| 12 | Greedy + random uphill kicks | 80 | 0.32 | 0.0 |
| 12 | WalkSAT-style clause search | 21 | 0.33 | 0.0 |
| 20 | Single-start greedy (1-flip) | 120 | 0.25 | 2.0 |
| 20 | Greedy + random restarts | 710 | 1.95 | 0.0 |
| 20 | Greedy + exact 2-flip lookahead + restarts | 665 | 0.62 | 0.0 |
| 20 | Selective 3rd-order Taylor–Greedy + restarts | 1690 | 1.13 | 0.0 |
| 20 | Greedy + random uphill kicks | 508 | 1.52 | 0.0 |
| 20 | WalkSAT-style clause search | 75 | 1.01 | 0.0 |
| 32 | Single-start greedy (1-flip) | 256 | 0.40 | 3.0 |
| 32 | Greedy + random restarts | 2224 | 4.17 | 0.0 |
| 32 | Greedy + exact 2-flip lookahead + restarts | 4848 | 2.20 | 0.0 |
| 32 | Selective 3rd-order Taylor–Greedy + restarts | 3716 | 2.93 | 0.0 |
| 32 | Greedy + random uphill kicks | 2263 | 3.96 | 0.0 |
| 32 | WalkSAT-style clause search | 126 | 1.85 | 0.0 |
| 48 | Single-start greedy (1-flip) | 576 | 0.73 | 4.0 |
| 48 | Greedy + random restarts | 4992 | 6.22 | 1.0 |
| 48 | Greedy + exact 2-flip lookahead + restarts | 4968 | 1.95 | 1.0 |
| 48 | Selective 3rd-order Taylor–Greedy + restarts | 4976 | 4.01 | 1.5 |
| 48 | Greedy + random uphill kicks | 4976 | 6.20 | 1.0 |
| 48 | WalkSAT-style clause search | 184 | 2.95 | 0.0 |
| 64 | Single-start greedy (1-flip) | 960 | 0.99 | 5.5 |
| 64 | Greedy + random restarts | 4992 | 5.52 | 3.0 |
| 64 | Greedy + exact 2-flip lookahead + restarts | 4960 | 2.98 | 3.5 |
| 64 | Selective 3rd-order Taylor–Greedy + restarts | 4992 | 4.44 | 3.5 |
| 64 | Greedy + random uphill kicks | 4951 | 5.97 | 2.0 |
| 64 | WalkSAT-style clause search | 392 | 6.88 | 0.0 |

## Strong adversarial counterexample for strict local improvement

For cyclic binary variables x_1,...,x_N, define:

E(x)=2Σ_i(x_i−x_{i+1})²+(1−x_1)(1−x_2)(1−x_3).

This objective is a degree-three polynomial, so its third-order Taylor expansion is **exact everywhere**. Nonetheless E(0^N)=1 and E(1^N)=0, while every other binary assignment is nonuniform and has E≥4. Thus strict cost-decreasing moves that change fewer than all N bits cannot escape the all-zero state. Checked all 69,352 1-, 2-, 3-bit moves for N=12,20,32,48,64; none improved. This shows a limitation of bounded-move *strict local greedy* algorithms, not a lower bound for all optimization algorithms.

## Interpretation

1. **The improvement over the weakest baseline is real on these instances**, but not enough to compete with a reasonable SAT-specific search heuristic.
2. **The ability to represent a Boolean objective with a low-order Taylor polynomial does not solve the discrete optimization problem.** SAT objectives are degree ≤3, yet selecting a satisfying assignment is the hard part.
3. **Search strategy, exploration, and exploiting problem structure matter.** Random walks or focused clause selection may be more useful than exhaustive local Taylor neighborhoods.
4. **Results do not establish polynomial-time performance.** The instances are small and distribution-specific; solving all attempts under a fixed budget does not imply any worst-case guarantee.
5. **Candidate budget is not a uniform work budget.** WalkSAT evaluates three candidates per step but also scans all clauses; Taylor–Greedy builds derivatives; both are reflected imperfectly by candidate counts, and runtime may favor different methods on different platforms.
6. **Uploaded PDF report is a separate preliminary study.** Its claimed random-QUBO results cannot be reproduced from the uploaded PDF alone because `test_tg.py` and `test_tg2.py` were not provided. This follow-up is an independent experiment on planted 3-SAT, not a reproduction of the PDF’s QUBO/Rastrigin experiments.

## Reproducibility

- Python 3.13.5, NumPy 2.3.5; run `python taylor_greedy_followup.py` then `python taylor_greedy_walksat_control.py` from the same directory.
- Seed: 20261123 for SAT generator and starts. WalkSAT noise=0.5. Selective candidate subset size=16. 12 independent SAT instances per N, 3 shared initial states.
- `taylor_greedy_followup_with_walksat.csv` contains all 1,080 rows, original seeds encoded in scripts. Sanity checks include: 1,440 analytic Taylor checks, 69,352 adversarial candidate checks, 1,080 unique method/instance/start tuples, candidate counts ≤5,000, and consistency between the reported hit flag and final best violated-clause count.

## Next research-quality step

To properly investigate the value of Taylor information, test *matched wall-clock budgets* versus WalkSAT and established SAT solvers on multiple generators, including randomly generated and adversarial cases, and report confidence intervals over independent problem instances. Avoid claiming either that higher-order correction always works or that all such algorithms are refuted by these finite experiments.
