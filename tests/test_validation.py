import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks"))
import taylor_greedy_followup as sat


class Validation(unittest.TestCase):
    def test_sat_taylor(self):
        self.assertEqual(sat.verify_taylor(), 1440)

    def test_ring_trap(self):
        self.assertEqual(sat.adversarial_check(), 69352)


if __name__ == "__main__":
    unittest.main()
