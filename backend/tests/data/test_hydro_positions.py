import unittest

from scripts.data.audit_hydro_positions import varied_positions


class HydroPositionsTests(unittest.TestCase):
    def test_reports_only_positions_that_change(self):
        positions, alphabet = varied_positions(['AAAA', 'ALAA', 'AAAV'], 'AAAA')
        self.assertEqual(positions, [1, 3])
        self.assertEqual(alphabet, 'ALV')


if __name__ == '__main__':
    unittest.main()
