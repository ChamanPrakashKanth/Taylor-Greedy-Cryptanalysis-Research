# Taylor–Greedy controlled follow-up benchmark

**Date:** 23 November 2026. **Result:** empirical heuristic comparison only, no theorem, and no cryptographic implications.
**Design:** 900 runs, 12 planted-satisfiable random 3-SAT problems x 3 shared starting states per size, N=(12, 20, 32, 48, 64); 5 methods; clause ratio=4.3; max 5000 scored candidate moves each. The planted satisfying assignment certifies the global objective minimum zero. Fixed random seed=20261123.
**Validation:** 1440 exact Taylor gain checks passed across 1-,2-,3-bit moves; 69352 adversarial ring-trap moves checked.
**Taylor model:** 3-SAT clause violations are multilinear polynomials of degree <=3. Derivatives of orders 1,2,3 are computed analytically. Third-order representation is exact globally, but searching all assignments is a separate problem.
**Methods:** greedy1=single-bit steepest descent, stop on plateau; restart1=greedy + random restarts; restart2=single-bit then exhaustive 2-bit improvements then restart; select3=single-bit then exact pair and triple changes restricted to a 16-variable interaction-ranked subset then restart; kick1=single-bit then random two-bit perturbations (may temporarily worsen objective).
**Budget fairness:** all methods have the same maximum number of candidate-move scores, not equivalent arithmetic operations. Derivative builds and CPU timings shown separately. No parameter tuning on test instances.

| N | Method | Success | Median scored candidates | Median runtime (ms) | Median unsatisfied clauses |
|---:|---|---:|---:|---:|---:|
| 12 | greedy1 | 15/36 (41.7%) | 36 | 0.18 | 1.0 |
| 12 | restart1 | 36/36 (100.0%) | 60 | 0.31 | 0.0 |
| 12 | restart2 | 36/36 (100.0%) | 102 | 0.27 | 0.0 |
| 12 | select3 | 36/36 (100.0%) | 102 | 0.30 | 0.0 |
| 12 | kick1 | 36/36 (100.0%) | 80 | 0.42 | 0.0 |
| 20 | greedy1 | 6/36 (16.7%) | 120 | 0.42 | 2.0 |
| 20 | restart1 | 34/36 (94.4%) | 710 | 2.53 | 0.0 |
| 20 | restart2 | 34/36 (94.4%) | 665 | 0.92 | 0.0 |
| 20 | select3 | 34/36 (94.4%) | 1690 | 1.48 | 0.0 |
| 20 | kick1 | 34/36 (94.4%) | 508 | 1.92 | 0.0 |
| 32 | greedy1 | 3/36 (8.3%) | 256 | 0.69 | 3.0 |
| 32 | restart1 | 27/36 (75.0%) | 2224 | 6.20 | 0.0 |
| 32 | restart2 | 20/36 (55.6%) | 4848 | 3.86 | 0.0 |
| 32 | select3 | 19/36 (52.8%) | 3716 | 4.30 | 0.0 |
| 32 | kick1 | 30/36 (83.3%) | 2263 | 6.55 | 0.0 |
| 48 | greedy1 | 2/36 (5.6%) | 576 | 1.28 | 4.0 |
| 48 | restart1 | 7/36 (19.4%) | 4992 | 11.19 | 1.0 |
| 48 | restart2 | 11/36 (30.6%) | 4968 | 3.61 | 1.0 |
| 48 | select3 | 11/36 (30.6%) | 4976 | 6.07 | 1.5 |
| 48 | kick1 | 16/36 (44.4%) | 4976 | 11.72 | 1.0 |
| 64 | greedy1 | 0/36 (0.0%) | 960 | 1.97 | 5.5 |
| 64 | restart1 | 1/36 (2.8%) | 4992 | 10.24 | 3.0 |
| 64 | restart2 | 0/36 (0.0%) | 4960 | 6.01 | 3.5 |
| 64 | select3 | 1/36 (2.8%) | 4992 | 7.59 | 3.5 |
| 64 | kick1 | 4/36 (11.1%) | 4951 | 10.59 | 2.0 |

## High-priority caveats
1. Planted-satisfiable random SAT is not a representative distribution of NP-complete instances; 0 is known to be feasible but not given to the solvers.
2. A local Taylor expansion is not an efficient global search oracle. The exact cubic representation does not make exhaustive search polynomial.
3. On binary SAT, raising Taylor order and increasing the move neighborhood are different operations; select3 uses exact cubic derivatives to evaluate chosen triple flips. A different search policy might work better or worse.
4. Candidate-score budgets are not CPU budgets. Runtime includes coefficient computation, temporary arrays, and candidate selection. Python runtime is platform-specific and affected by measurement noise.
5. Shared starting states permit paired method comparisons; outcomes for repeated starts of the same instance are not statistically independent.
6. Ring trap: E=2 sum_i (x_i-x_{i+1})^2+(1-x_1)(1-x_2)(1-x_3), cyclic boundary. E(0^N)=1, E(1^N)=0, and any other bitstring E>=4. Strictly improving k-bit local search with k<N cannot leave 0^N despite a globally exact cubic Taylor expansion. This is not a lower bound for arbitrary algorithms.

## Follow-up
Compare against WalkSAT/GSAT and modern SAT solvers, multiple generators, matched wall-time budgets and larger independent samples; investigate learning a variable subset without requiring dense high-order tensors.
