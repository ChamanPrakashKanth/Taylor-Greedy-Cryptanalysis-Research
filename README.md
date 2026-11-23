# Taylor–Greedy optimization research

Does higher-order Taylor information help greedy search reach known optima? This repository contains **2,012 recorded solver trials** on planted 3-SAT, binary quadratic objectives, continuous functions, and a synthetic classroom cipher.

| Benchmark | What the trials showed |
|---|---|
| Planted 3-SAT | On 80 fresh instances, adaptive and fixed selective Taylor-3 each solved 44. Restarted greedy solved 43 and WalkSAT-style search solved 79. |
| Dense and sparse QUBO | Taylor-2 and restarted greedy each reached 72 of 72 certified optima. Simulated annealing reached 70. |
| Rastrigin | Powell solved 36 of 36 trials to the specified tolerance. Each of the three Taylor coordinate policies solved zero. |
| Classroom cipher | Uniform random search found 13 of 27 holdout-valid matches. Both greedy variants found 8. Exhaustive enumeration supplied the reference. |

The experiments did not establish a Taylor–Greedy advantage over the strongest tested baselines. The [research report](research/experimental_findings.md) explains the exact Taylor identities, the ring counterexample, budget differences, and what remains untested. The cipher results apply only to the custom classroom construction.

## Start here

An optimization problem gives each possible answer a score. The **objective** is the function that computes that score. In this project, a smaller score is better, and a **global optimum** is the smallest score any answer can achieve.

In 3-SAT, each variable is true or false. Each clause is an OR of three literals, where a literal is a variable or its negation. The objective counts clauses that are false. A score of zero means every clause is satisfied. In a *planted* instance, the generator first chooses a satisfying assignment and then builds clauses consistent with it. The search starts from a separate assignment and does not receive the planted answer.

### What does Taylor–Greedy do?

A greedy solver checks nearby answers, takes an improving move, and repeats. For a bit string, the simplest move flips one bit. If every single flip leaves the score unchanged or makes it worse, the solver can get stuck.

Consider the two-bit objective `f(x, y) = x + y - 4xy`. At `(0, 0)` the score is zero. Flipping either bit alone raises it to one. Flipping both gives `(1, 1)`, with a score of −2. The interaction term `-4xy` explains why the pair behaves differently from its two individual flips.

Taylor terms describe how the objective changes as variables move. First order describes individual effects, second order adds pair interactions, and third order adds triple interactions. On the polynomial objectives used here, these terms can give exact scores for selected moves. The solver still has to choose which moves to inspect. An exact score for each nearby move does not guarantee a path to the global optimum.

The SAT benchmarks compare single-flip greedy, random restarts, pair and triple lookahead, an adaptive order policy, and a WalkSAT-style baseline. WalkSAT-style search focuses on an unsatisfied clause and may take a randomized flip. QUBO, short for *quadratic unconstrained binary optimization*, uses binary variables and an objective with terms of degree at most two. Rastrigin uses real variables and has many local minima.

## Quick start

You need Git and Python 3.11. Use a virtual environment so the pinned packages stay separate from system Python.

```bash
git clone https://github.com/ChamanPrakashKanth/Taylor-Greedy-Cryptanalysis-Research.git
cd Taylor-Greedy-Cryptanalysis-Research
python3.11 --version
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

On Debian-based Linux, if Python 3.11 is installed but reports that `ensurepip` is unavailable, install your distribution's Python 3.11 venv package (often `python3.11-venv`) and rerun the environment creation command. An `OK` at the end of the test output means the local suite passed.

### Run one experiment

```bash
python benchmarks/benchmark_adaptive.py
head -n 6 results/raw/adaptive_sat.csv
```

Each data row is one method on one instance. `hit=1` means the method satisfied every clause. Otherwise, `best_unsat` tells you how many clauses remained unsatisfied in the best assignment it found. `candidates` counts scored moves under the method's accounting. `elapsed_ms` records elapsed time in milliseconds. Candidate counts do not capture all work: derivative construction and clause scans can cost different amounts.

## Reproduce all recorded benchmarks

Run from the repository root with the virtual environment active:

```bash
python benchmarks/taylor_greedy_followup.py
python benchmarks/taylor_greedy_walksat_control.py
python benchmarks/benchmark_adaptive.py
python benchmarks/benchmark_qubo.py
python benchmarks/benchmark_continuous.py
python benchmarks/benchmark_toy.py
python benchmarks/summarize.py
```

The WalkSAT control reads the archived SAT rerun's CSV, so run those two scripts in the listed order. The scripts overwrite their output files. Seeds are fixed in the source, and elapsed times vary by machine. In QUBO, `gap` is the best value found minus the minimum certified by exhaustive enumeration. On Sphere and Rastrigin, a gap of at most `1e-8` counts as a hit. In the toy cipher CSV, `valid_match` records agreement on separate verification messages, while `planted_key_found` records recovery of the generated key.

## Find your way around

| Location | What to open it for |
|---|---|
| [benchmarks/](benchmarks/) | Experiment entry points and solver implementations |
| [tests/](tests/) | Mathematical checks, solver regressions, and checks on recorded results |
| [results/raw/](results/raw/) | Individual runs, including unsuccessful ones |
| [results/summaries/sat.md](results/summaries/sat.md) | SAT results grouped by size and method |
| [figures/sat_scaling.png](figures/sat_scaling.png) | Visual comparison of SAT success rates |
| [research/experimental_findings.md](research/experimental_findings.md) | Methods, counterexample, findings, and limitations |

The 2,012 total counts solver runs, including multiple methods on the same problem. The archived SAT-only CSV is an intermediate output already represented in the combined SAT CSV. The strongest result here is specific to these experiments: trying more Taylor terms did not consistently improve search, and the finite runs do not establish a worst-case complexity bound.
