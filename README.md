# Taylor–Greedy optimization research

This repository contains a reproduction of the supplied planted 3-SAT benchmark and a fresh-seed comparison of a cost-aware Taylor order selector against restarted greedy, selective Taylor-3, and WalkSAT-style search.

Run from the repository root with Python 3.11 and the pinned dependencies:

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests
python3 benchmarks/taylor_greedy_followup.py
python3 benchmarks/taylor_greedy_walksat_control.py
python3 benchmarks/benchmark_adaptive.py
python3 benchmarks/benchmark_qubo.py
python3 benchmarks/benchmark_continuous.py
python3 benchmarks/benchmark_toy.py
python3 benchmarks/summarize.py
```

See [findings](research/experimental_findings.md), [tables](results/summaries/sat.md), and the [scaling figure](figures/sat_scaling.png). Raw CSVs include all completed trials.
