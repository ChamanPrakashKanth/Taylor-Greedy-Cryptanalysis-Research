"""Build tables and a scaling plot from completed SAT trials."""
import csv
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt

lines = []
figure, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
for filename, title, axis in zip(
    ("taylor_greedy_followup_with_walksat", "adaptive_sat"),
    ("Archived benchmark rerun", "Fresh-seed comparison"), axes,
):
    with Path(f"results/raw/{filename}.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    lines += [f"## {title}", "",
              "| Variables | Method | Solved | Median scores | Median elapsed ms |",
              "|---:|---|---:|---:|---:|"]
    sizes = sorted({int(row["variables"]) for row in rows})
    for method in sorted({row["method"] for row in rows}):
        rates = []
        for n in sizes:
            group = [row for row in rows if row["method"] == method
                     and int(row["variables"]) == n]
            hits = sum(int(row["hit"]) for row in group)
            rates.append(hits / len(group))
            scores = median(int(row["candidates"]) for row in group)
            elapsed = median(float(row["elapsed_ms"]) for row in group)
            lines.append(f"| {n} | {method} | {hits}/{len(group)} | {scores:g} | {elapsed:.2f} |")
        axis.plot(sizes, rates, marker="o", label=method)
    lines.append("")
    axis.set(title=title, xlabel="Variables", ylabel="Fraction solved", ylim=(-0.04, 1.06))
    axis.legend(fontsize=8)
Path("results/summaries/sat.md").write_text("\n".join(lines))
figure.savefig("figures/sat_scaling.png", dpi=150)
