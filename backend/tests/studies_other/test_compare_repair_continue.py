import unittest

from scripts.multiprotein.compare_repair_continue import classify


class CompareRepairContinueTests(unittest.TestCase):
    def test_ties_use_the_study_tolerance(self):
        self.assertEqual(classify(1.0 + 1e-13, 1.0), 'tied')
        self.assertEqual(classify(1.1, 1.0), 'higher')
        self.assertEqual(classify(0.9, 1.0), 'lower')


if __name__ == '__main__':
    unittest.main()
