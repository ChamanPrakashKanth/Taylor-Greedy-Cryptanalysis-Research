# Experimental findings

## Abstract

We tested whether giving a greedy search access to higher-order interactions improves its ability to solve planted 3-SAT. The archived selective Taylor-3 method solved 101 of 180 attempts, compared with 105 for restarted single-flip greedy and 180 for WalkSAT-style search. On 80 fresh instances, the adaptive variant and archived Taylor-3 each solved 44, restarted greedy solved 43, and WalkSAT-style search solved 79. These trials support classifications D and G for the measured planted SAT workloads.

## Provenance and method

The ZIP with a numbered filename contained both archived scripts. Their output paths were made relative for reproduction. The two named PDFs, original benchmark and scaling scripts, and earlier QUBO and Rastrigin sources were unavailable. All 1,080 archived rows matched the supplied CSV across every field except elapsed time, which was measured anew. The rerun used Python 3.11.2 and NumPy 1.24.2.

The original suite uses seed 20261123, twelve instances and three starts per size. The fresh suite uses seed 20261124, sixteen independent instances and one shared start per size. Both use 12, 20, 32, 48 and 64 variables. The adaptive policy searches singles first, then prioritizes pairs or triples by cumulative objective improvement per candidate scored during that run. It limits the higher-order neighborhood to twelve variables selected using the gradient and negative Hessian interactions. It restarts when neither neighborhood yields an improving move. Its narrower neighborhood and adaptive ordering both differ from the archived Taylor-3 variant, so this comparison cannot isolate the effect of either choice.

## Mathematical analysis

Each 3-SAT clause violation is a product of three affine factors, one per variable. Expanding the product in the displacement produces exactly its constant, linear, quadratic, and cubic terms. Summing over clauses preserves exactness. With a quadratic objective the same algebra stops after degree two. Validation exercised 1,440 exact SAT score comparisons for moves of size one through three.

A cyclic ring gives a strict local trap. For binary variables let the cost be twice the number of cyclic transitions plus a penalty of one when the first three bits are zero. The all-zero state costs one and the all-one state costs zero. Every nonuniform state has at least two transitions and costs at least four. A strict descent algorithm starting at zero must change all bits at once to improve. The reproduced code checks 69,352 moves of size up to three.

For the archived dense SAT implementation, building the cubic coefficient array uses cubic storage and initial allocation, and building the gradient and Hessian at a state costs O(m + N²) for m clauses. An exact candidate score uses O(1) arithmetic for each move of at most three bits after derivative construction. A scan of moves up to fixed size k has O(N^k) candidates. Allowing every size gives 2^N - 1 candidates. A candidate cap bounds experimental work but supplies no bound on time to find an optimum.

## Limits and follow-up

The scripts use a candidate-score cap of 5,000. Restart evaluations and validation computations are not accounted for uniformly by the original methods, and WalkSAT scans clauses. Elapsed time is descriptive. Repeated starts on an archived instance are correlated. Equal wall-clock comparisons, confidence intervals, allocation and operation counts, controlled ablations, learned selectors, and additional optimization families are outside the completed evidence. The separate extension below reports a classroom cipher experiment.

A follow-up should compare fixed and adaptive order with the same variable subset, use matched wall-clock budgets, and report paired intervals by independent instance.

## Additional experiments

### Binary quadratics

Dense and sparse random symmetric integer matrices, sizes 8, 12, and 16, with twelve draws per size and density. Exhaustive enumeration certified each minimum of xᵀQx. Direct recomputation checked second-order displacement formulas on one-, two-, and three-bit moves. The tables count candidate scores under the implemented policies, including restart draws. The annealing baseline scores one selected flip per step. The current code builds all single-flip deltas on each annealing step, so candidate counts alone understate its arithmetic costs.

| Method | Exact minima |
|---|---:|
| Greedy with restarts | 72/72 |
| Taylor-2 with restarts | 72/72 |
| Simulated annealing | 70/72 |

### Continuous objectives

Each method had up to 600 direct objective evaluations on the same starts. Taylor coordinate search evaluated four candidate displacements per coordinate using its local model, directly scored the best prediction, and reduced the search radius after rejection. Powell used SciPy 1.10.1. Both functions have optimum zero and the hit threshold was 1e-8.

| Method | Sphere hits | Rastrigin hits | Median Rastrigin gap |
|---|---:|---:|---:|
| Powell | 36/36 | 36/36 | 6.64e-28 |
| Taylor-1 | 36/36 | 0/36 | 86.06 |
| Taylor-2 | 36/36 | 0/36 | 89.55 |
| Taylor-3 | 36/36 | 0/36 | 93.03 |

Both functions are separable. These scores characterize the tested coordinate policy and do not measure performance on coupled engineering objectives.

### Classroom cipher

A custom substitution and rotation construction used synthetic 8-, 12-, and 16-bit keys and 2, 4, or 8 rounds. The objective counted ciphertext disagreements across four messages. A candidate with zero disagreements was checked on four distinct holdout messages. Exhaustive enumeration established the reference sets. Heuristics were capped at the smaller of 1,024 evaluations and the keyspace size.

| Method | Found a holdout-valid match |
|---|---:|
| Exhaustive reference | 27/27 |
| Uniform random without replacement | 13/27 |
| Restarted single-flip greedy | 8/27 |
| Restarted single/pair greedy | 8/27 |

The pair search scores actual neighbors and serves as a neighborhood baseline. These results apply to this classroom construction. The raw table distinguishes holdout-valid matches from recovery of the particular planted key.

### Outstanding work

The study has 2,012 completed solver trials across five batches. The requested verified unsatisfiable and additional SAT generators, larger instances, independent Ising and engineering workloads, learned selector, ablations, uncertainty intervals, matched wall-clock runs and standard-cipher seed recovery were not completed.
