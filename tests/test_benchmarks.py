import csv
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))
from benchmark_continuous import coordinate_taylor
from benchmark_qubo import solve
from benchmark_toy import trial
from simulations.toy_cipher import encrypt


class SolverChecks(unittest.TestCase):
    def test_qubo_reaches_certified_minimum(self):
        matrix = np.diag([-3, 2, -4])
        for method in ("restart1", "taylor2", "annealing"):
            with self.subTest(method=method):
                result = solve(matrix, np.zeros(3, dtype=int), method, 23, -7, budget=100)
                self.assertEqual(result["gap"], 0)
                self.assertLessEqual(result["scores"], 100)

    def test_qubo_pair_can_escape_a_single_flip_trap(self):
        matrix = np.array([[1, -2], [-2, 1]])
        result = solve(matrix, np.zeros(2, dtype=int), "taylor2", 23, -2, budget=4)
        self.assertEqual(result["hit"], 1)
        self.assertEqual(result["scores"], 4)

    def test_continuous_orders_converge_on_sphere(self):
        for order in (1, 2, 3):
            with self.subTest(order=order):
                gap, evaluations, scores = coordinate_taylor(
                    np.array([1.8, -2.4]), 0, order, 250
                )
                self.assertLessEqual(gap, 1e-8)
                self.assertLessEqual(evaluations, 250)
                self.assertEqual(scores, 8 * (evaluations - 1))

    def test_toy_cipher_is_a_permutation_for_fixed_key(self):
        for rounds in (2, 4, 8):
            self.assertEqual(len({encrypt(m, 37, 8, rounds) for m in range(256)}), 256)

    def test_toy_exhaustive_reference_recovers_planted_key(self):
        reference = next(row for row in trial(8, 2, 123) if row["method"] == "exhaustive")
        self.assertEqual(reference["valid_match"], 1)
        self.assertEqual(reference["planted_key_found"], 1)
        self.assertEqual(reference["scores"], 256)


class RecordedResultsChecks(unittest.TestCase):
    def test_trial_counts(self):
        expected = {
            "taylor_greedy_followup_with_walksat": 1080,
            "adaptive_sat": 320,
            "qubo": 216,
            "continuous": 288,
            "toy": 108,
        }
        for dataset, count in expected.items():
            with self.subTest(dataset=dataset):
                with (ROOT / "results" / "raw" / f"{dataset}.csv").open(newline="") as source:
                    self.assertEqual(sum(1 for _ in csv.DictReader(source)), count)
