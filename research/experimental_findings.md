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

The scripts use a candidate-score cap of 5,000. Restart evaluations and validation computations are not accounted for uniformly by the original methods, and WalkSAT scans clauses. Elapsed time is descriptive. Repeated starts on an archived instance are correlated. Equal wall-clock comparisons, confidence intervals, allocation and operation counts, controlled ablations, learned selectors, other optimization families, and cryptographic experiments are outside the completed evidence. There is no measured key-recovery result or basis for a conclusion about encryption or complexity classes.

A follow-up should compare fixed and adaptive order with the same variable subset, use matched wall-clock budgets, and report paired intervals by independent instance.
