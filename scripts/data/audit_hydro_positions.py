#!/usr/bin/env python3
"""List the positions that vary across the Hydro variants of each protein, and the amino acids seen there."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
START = {'P06241': 85, 'P01053': 22, 'P0A9X9': 5}


def varied_positions(sequences, reference):
    """Return the zero-based positions where any sequence differs from the reference, and the amino acids seen there."""
    positions = sorted({i for sequence in sequences for i, (a, b) in enumerate(zip(sequence, reference)) if a != b})
    return positions, ''.join(sorted(Counter(sequence[i] for sequence in sequences for i in positions)))


def main():
    with (ROOT / 'data/raw/flip2/hydro/low_to_high.csv').open() as handle:
        sequences = [row['sequence'] for row in csv.DictReader(handle)]
    report = {}
    for protein, start in START.items():
        reference = ''.join((ROOT / f'data/hydro_references/{protein}.fasta').read_text().splitlines()[1:])
        group = [sequence for sequence in sequences if len(sequence) == len(reference)]
        positions, alphabet = varied_positions(group, reference)
        report[protein] = {'variants': len(group), 'varied_positions_in_segment': positions,
                           'uniprot_residue_numbers': [start + i for i in positions], 'amino_acids_seen': alphabet}
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
