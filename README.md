# Taylor–Greedy optimization research

Does higher-order Taylor information help greedy search reach known optima? This repository contains **2,012 recorded solver trials** on planted 3-SAT, binary quadratic objectives, continuous functions, and a synthetic classroom cipher.

| Benchmark | What the trials showed |
|---|---|
| Planted 3-SAT | On 80 fresh instances, adaptive and fixed selective Taylor-3 each solved 44. Restarted greedy solved 43 and WalkSAT-style search solved 79. |
| Dense and sparse QUBO | Taylor-2 and restarted greedy each reached 72 of 72 certified optima. Simulated annealing reached 70. |
| Rastrigin | Powell solved 36 of 36 trials to the specified tolerance. Each of the three Taylor coordinate policies solved zero. |
| Classroom cipher | Uniform random search found 13 of 27 holdout-valid matches. Both greedy variants found 8. Exhaustive enumeration supplied the reference. |

The experiments did not establish a Taylor–Greedy advantage over the strongest tested baselines. The [research report](research/experimental_findings.md) explains the exact Taylor identities, the ring counterexample, budget differences, and what remains untested. The cipher results apply only to the custom classroom construction.

## Reproduce the results

From the repository root, use Python 3.11 in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python benchmarks/taylor_greedy_followup.py
python benchmarks/taylor_greedy_walksat_control.py
python benchmarks/benchmark_adaptive.py
python benchmarks/benchmark_qubo.py
python benchmarks/benchmark_continuous.py
python benchmarks/benchmark_toy.py
python benchmarks/summarize.py
```

Run the archived SAT benchmark before its WalkSAT control, which reads the first script's CSV. Seeds are fixed in the scripts. Elapsed times vary by machine.

Browse the [SAT comparison tables](results/summaries/sat.md), [scaling plot](figures/sat_scaling.png), and [raw outputs](results/raw/). The archived SAT-only CSV is also included as an intermediate result and is counted once within the combined SAT results.
