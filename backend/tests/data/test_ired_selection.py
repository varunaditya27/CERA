import unittest

from scripts.data.audit_ired_selection import compare


def row(sequence, changes, indel='False', stop='False', readthrough='False'):
    return {'aa_seq': sequence + '*', 'Nham_aa': str(changes), 'indel': indel, 'STOP': stop, 'STOP_readthrough': readthrough}


class IredSelectionTests(unittest.TestCase):
    def test_flagged_and_long_rows_are_left_out(self):
        active = [row('AAA', 1), row('AAB', 2), row('AAC', 3, indel='True'), row('AAD', 4, stop='True'), row('AAE', 30)]
        result = compare(active, {'AAA', 'AAB'})
        self.assertEqual(result['active_rows_left_out'], 3)
        self.assertEqual(result['left_out_flags'], {'indel': 1, 'STOP': 1, 'STOP_readthrough': 0})
        self.assertEqual(result['flag_free_left_out_amino_acid_changes'], [30.0])
        self.assertEqual(result['flagged_rows_in_split'], 0)
        self.assertEqual(result['split_rows_missing_from_active'], 0)
        self.assertEqual(result['flag_free_rows_with_changes_between_split_maximum_and_smallest_left_out'], 0)

    def test_split_sequence_absent_from_active_table_is_reported(self):
        self.assertEqual(compare([row('AAA', 1)], {'AAA', 'ZZZ'})['split_rows_missing_from_active'], 1)


if __name__ == '__main__':
    unittest.main()
