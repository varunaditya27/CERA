#!/usr/bin/env python3
"""Download and verify the optional FLIP GB1 and ProteinGym GFP assays."""
import gzip
import hashlib
import io
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
GB1_URL = 'https://flip.protein.properties/assets/splits/gb1/low_vs_high.csv.gz'
ZIP_URL = 'https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/DMS_ProteinGym_substitutions.zip'
REF_URL = 'https://raw.githubusercontent.com/OATML-Markslab/ProteinGym/144fe22b07dfaeec2b366f2346203a9838a55b4c/reference_files/DMS_substitutions.csv'

def check(data, digest):
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError('Checksum mismatch')
    return data

def fetch(url):
    with urlopen(url, timeout=180) as response:
        return response.read()

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

def main():
    gz = ROOT / 'data/raw/flip/gb1/low_vs_high.csv.gz'
    data = gz.read_bytes() if gz.exists() else fetch(GB1_URL)
    check(data, '5dde43a6d5f623f5822ef86939fef515424bf336930aaffeba024f965b7bc724')
    if not gz.exists(): save(gz, data)
    csv = gz.with_suffix('')
    extracted = gzip.decompress(data)
    if csv.exists() and csv.read_bytes() != extracted: raise ValueError('GB1 CSV differs from archive')
    if not csv.exists(): save(csv, extracted)
    gfp = ROOT / 'data/raw/proteingym/GFP_AEQVI_Sarkisyan_2016.csv'
    digest = '05b97d36a23363331b271edc56f1496b9a539109fd006e65532f91e9903a0838'
    if gfp.exists(): check(gfp.read_bytes(), digest)
    else:
        archive = check(fetch(ZIP_URL), '3a83766254ac9ac9984ec25cb73c6e010ea4418f5e35f143933e6b6e6473b921')
        with ZipFile(io.BytesIO(archive)) as z:
            save(gfp, check(z.read('DMS_ProteinGym_substitutions/GFP_AEQVI_Sarkisyan_2016.csv'), digest))
    ref = ROOT / 'data/raw/proteingym/DMS_substitutions_reference.csv'
    expected = 'a8f498011532a74aa9fe556a50555a75e928c5837d19c06a87592ae04049b308'
    if ref.exists(): check(ref.read_bytes(), expected)
    else: save(ref, check(fetch(REF_URL), expected))
    print('Optional files verified.')

if __name__ == '__main__': main()
