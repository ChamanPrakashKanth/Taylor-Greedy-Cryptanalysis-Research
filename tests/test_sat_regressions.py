"""Check SAT solver bookkeeping and the shape of the recorded comparisons."""
import csv
from pathlib import Path
import random
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import benchmark_adaptive as adaptive
import taylor_greedy_followup as sat
from taylor_greedy_walksat_control import solve_walksat


class SatRegressionChecks(unittest.TestCase):
    def setUp(self):
        self.problem = sat.generate(12, random.Random(45))

    def test_generator_is_reproducible_and_plants_a_solution(self):
        duplicate = sat.generate(12, random.Random(45))
        self.assertEqual(self.problem.planted, duplicate.planted)
        self.assertEqual(self.problem.ids.tolist(), duplicate.ids.tolist())
        self.assertEqual(self.problem.signs.tolist(), duplicate.signs.tolist())
        self.assertEqual(self.problem.energy(self.problem.planted), 0)
        self.assertTrue(all(len(set(clause)) == 3 for clause in self.problem.ids))

    def test_solved_start_needs_no_candidate_scores(self):
        start = self.problem.planted
        for solve in (adaptive.adaptive, solve_walksat):
            with self.subTest(solver=solve.__name__):
                result = solve(self.problem, start, 23)
                self.assertEqual(result["hit"], 1)
                self.assertEqual(result["best_unsat"], 0)
                self.assertEqual(result["candidates"], 0)

    def test_seeded_solver_outputs_are_repeatable_and_within_budget(self):
        for solve in (adaptive.adaptive, solve_walksat):
            with self.subTest(solver=solve.__name__):
                first = solve(self.problem, 0, 23)
                again = solve(self.problem, 0, 23)
                for result in (first, again):
                    result.pop("elapsed_ms")
                self.assertEqual(first, again)
                self.assertLessEqual(first["candidates"], sat.BUDGET)
                self.assertLessEqual(first["best_unsat"], self.problem.energy(0))
                self.assertEqual(first["hit"], int(first["best_unsat"] == 0))

    def test_recorded_sat_trials_are_paired_and_within_budget(self):
        files = {
            "adaptive_sat": {"restart1", "select3", "adaptive", "walksat"},
            "taylor_greedy_followup_with_walksat": {*sat.METHODS, "walksat"},
        }
        for name, methods in files.items():
            with self.subTest(dataset=name):
                pairs = {}
                with (ROOT / "results" / "raw" / f"{name}.csv").open(newline="") as source:
                    for row in csv.DictReader(source):
                        key = (row["variables"], row["instance"], row.get("start_index"))
                        seen = pairs.setdefault(key, set())
                        self.assertNotIn(row["method"], seen)
                        seen.add(row["method"])
                        self.assertTrue(0 <= int(row["candidates"]) <= sat.BUDGET)
                        self.assertEqual(int(row["hit"]), int(row["best_unsat"] == "0"))
                self.assertTrue(pairs)
                self.assertTrue(all(seen == methods for seen in pairs.values()))
