"""Compare plateau policies on fresh planted SAT instances."""
import csv
from pathlib import Path
import random
import time

import numpy as np

import taylor_greedy_followup as sat
from taylor_greedy_walksat_control import solve_walksat


def adaptive(problem, state, seed):
    rng = random.Random(seed)
    started = time.perf_counter()
    energy = best = problem.energy(state)
    scores = 0
    # Track improvement per score, with a prior that tries each order.
    reward = {2: 1.0, 3: 1.0}
    cost = {2: 1, 3: 1}
    neighborhoods = {k: sat.combinations(min(12, problem.n), k) for k in (2, 3)}
    while best and scores + problem.n <= sat.BUDGET:
        sign, gradient, hessian = problem.taylor(state)
        scores += problem.n
        choice = int(gradient.argmin())
        delta = int(gradient[choice])
        move = 1 << choice
        if delta >= 0:
            priority = gradient + np.minimum(hessian, 0).sum(axis=0)
            selected = np.sort(np.argsort(priority, kind="stable")[:12])
            for order in sorted(reward, key=lambda k: -reward[k] / cost[k]):
                moves = selected[neighborhoods[order]]
                if scores + len(moves) > sat.BUDGET:
                    continue
                gains = sat.gains_for_moves(gradient, hessian, problem.cubic, sign, moves)
                index = int(gains.argmin())
                delta = int(gains[index])
                scores += len(moves)
                cost[order] += len(moves)
                reward[order] += max(0, -delta)
                if delta < 0:
                    move = sat.flipmask(moves[index])
                    break
        if delta < 0:
            state ^= move
            energy += delta
            assert energy == problem.energy(state)
        elif scores < sat.BUDGET:
            state = rng.getrandbits(problem.n)
            energy = problem.energy(state)
            scores += 1
        best = min(best, energy)
    return dict(hit=int(best == 0), best_unsat=best, candidates=scores,
                elapsed_ms=1000 * (time.perf_counter() - started))


def main():
    seed = 20261124
    rng = random.Random(seed)
    rows = []
    fields = ('hit', 'best_unsat', 'candidates', 'elapsed_ms')
    for n in sat.SIZES:
        pairs = sat.combinations(n, 2)
        for instance in range(16):
            problem = sat.generate(n, rng)
            state = rng.getrandbits(n)
            run_seed = rng.randrange(2**32)
            for method in ('restart1', 'select3', 'adaptive', 'walksat'):
                if method == 'adaptive':
                    results = adaptive(problem, state, run_seed)
                elif method == 'walksat':
                    results = solve_walksat(problem, state, run_seed)
                else:
                    results = sat.solve(problem, state, method, run_seed, pairs)
                rows.append(dict(variables=n, instance=instance, method=method,
                                 **{field: results[field] for field in fields}))
    with Path('results/raw/adaptive_sat.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    main()
