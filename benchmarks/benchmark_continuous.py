"""Compare bounded Taylor coordinate search with Powell on known optima."""
import csv
from pathlib import Path
from time import perf_counter

import numpy as np
from scipy.optimize import minimize


def objective(x, amplitude):
    return float(np.sum(x*x + amplitude * (1 - np.cos(2*np.pi*x))))


def coordinate_taylor(start, amplitude, order, budget):
    x = start.copy()
    radius = 1.
    current = objective(x, amplitude)
    evaluations = 1
    models = 0
    steps = np.array([-1., -.5, .5, 1.])
    frequency = 2*np.pi
    while evaluations < budget and radius > 1e-7 and current > 1e-8:
        displacement = np.clip(x[:, None] + radius*steps, -5.12, 5.12) - x[:, None]
        gradient = 2*x + amplitude*frequency*np.sin(frequency*x)
        prediction = gradient[:, None]*displacement
        if order >= 2:
            hessian = 2 + amplitude*frequency**2*np.cos(frequency*x)
            prediction += hessian[:, None]*displacement**2/2
        if order >= 3:
            third = -amplitude*frequency**3*np.sin(frequency*x)
            prediction += third[:, None]*displacement**3/6
        axis, index = np.unravel_index(prediction.argmin(), prediction.shape)
        models += prediction.size
        proposal = x.copy()
        proposal[axis] += displacement[axis, index]
        value = objective(proposal, amplitude)
        evaluations += 1
        if value < current:
            x, current = proposal, value
            radius = min(1., radius*1.25)
        else:
            radius *= .5
    return current, evaluations, models


def main():
    rng = np.random.default_rng(20261126)
    rows = []
    budget = 600
    for name, amplitude in (("sphere", 0), ("rastrigin", 10)):
        for n in (4, 12, 24):
            for trial in range(12):
                start = rng.uniform(-5.12, 5.12, n)
                for order in (0, 1, 2, 3):
                    started = perf_counter()
                    if order:
                        gap, evaluations, scores = coordinate_taylor(start, amplitude, order, budget)
                        method = f"taylor{order}"
                    else:
                        observed = []
                        def evaluate(x):
                            value = objective(x, amplitude)
                            observed.append(value)
                            return value
                        minimize(evaluate, start, method="Powell", bounds=[(-5.12, 5.12)]*n,
                                 options={"maxfev": budget})
                        gap, evaluations, scores = min(observed), len(observed), 0
                        method = "powell"
                    rows.append(dict(problem=name, variables=n, trial=trial,
                                     method=method, gap=gap, hit=int(gap <= 1e-8),
                                     evaluations=evaluations, model_scores=scores,
                                     elapsed_ms=1000*(perf_counter()-started)))
    with Path("results/raw/continuous.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} continuous trials")


if __name__ == "__main__":
    main()
