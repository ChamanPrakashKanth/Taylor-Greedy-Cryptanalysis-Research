"""Paired, exactly certified comparisons on dense and sparse binary quadratics."""
import csv
from itertools import combinations
from pathlib import Path
from time import perf_counter

import numpy as np


def solve(matrix, initial, method, seed, optimum, budget=2000):
    rng = np.random.default_rng(seed)
    x = initial.copy()
    started = perf_counter()
    energy = best = int(x @ matrix @ x)
    scores = 1
    i, j = np.triu_indices(len(x), 1)
    while best > optimum and scores < budget:
        sign = 1 - 2 * x
        singles = sign * (2 * (matrix @ x) + sign * matrix.diagonal())
        if method == "annealing":
            move = [rng.integers(len(x))]
            delta = singles[move[0]]
            temperature = 8 * (0.05 ** (scores / budget))
            scores += 1
            if delta > 0 and rng.random() >= np.exp(-delta / temperature):
                continue
        else:
            if scores + len(x) > budget:
                break
            scores += len(x)
            move = [int(singles.argmin())]
            delta = singles[move[0]]
            if delta >= 0 and method == "taylor2" and scores + len(i) <= budget:
                pairs = singles[i] + singles[j] + 2 * sign[i] * sign[j] * matrix[i, j]
                index = int(pairs.argmin())
                scores += len(i)
                move = [i[index], j[index]]
                delta = pairs[index]
            if delta >= 0:
                x = rng.integers(0, 2, len(x))
                energy = int(x @ matrix @ x)
                scores += 1
                best = min(best, energy)
                continue
        x[move] ^= 1
        energy += int(delta)
        assert energy == x @ matrix @ x
        best = min(best, energy)
    return dict(gap=best - optimum, hit=int(best == optimum), scores=scores,
                elapsed_ms=1000 * (perf_counter() - started))


def main():
    rng = np.random.default_rng(20261125)
    rows = []
    checked = 0
    for n in (8, 12, 16):
        states = (np.arange(2**n)[:, None] >> np.arange(n)) & 1
        for density in (0.2, 1.0):
            for instance in range(12):
                upper = np.triu(rng.integers(-5, 6, (n, n)) *
                                (rng.random((n, n)) < density), 1)
                matrix = upper + upper.T + np.diag(rng.integers(-5, 6, n))
                optimum = int(np.min(np.sum((states @ matrix) * states, axis=1)))
                initial = rng.integers(0, 2, n)
                seed = rng.integers(2**32)
                displacement = 1 - 2 * initial
                base = initial @ matrix @ initial
                for order in (1, 2, 3):
                    for bits in combinations(range(n), order):
                        step = np.zeros(n, dtype=int)
                        step[list(bits)] = displacement[list(bits)]
                        predicted = 2 * step @ matrix @ initial + step @ matrix @ step
                        assert predicted == (initial + step) @ matrix @ (initial + step) - base
                        checked += 1
                for method in ("restart1", "taylor2", "annealing"):
                    rows.append(dict(variables=n, density=density, instance=instance,
                                     method=method, optimum=optimum,
                                     **solve(matrix, initial, method, seed, optimum)))
    with Path("results/raw/qubo.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} trials, {checked} quadratic displacement checks")


if __name__ == "__main__":
    main()
