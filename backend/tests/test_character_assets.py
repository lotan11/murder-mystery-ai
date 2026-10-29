import importlib.util
import struct
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('character_inspector',ROOT/'scripts'/'inspect-character.py')
inspector=importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)


def test_existing_sample_inventory_distinguishes_silence_target_from_full_approval():
    report=inspector.inspect(ROOT/'frontend/public/audition/mpfb.glb')
    assert report['vertices']>10000 and report['joint_count']==67
    assert report['missing_bones']==[] and report['missing_expressions']==[]
    assert report['missing_visemes']==['viseme_sil']
    assert report['external_resources']==[]
    assert 'separate review' in report['approval']


def test_scholar_blockout_contains_actual_embedded_geometry():
    report=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-blockout.glb')
    assert report['vertices']>1000 and report['triangles']>1000
    assert report['mesh_count']>0 and report['external_resources']==[]
    assert report['approval'].startswith('Structural inventory only')


@pytest.mark.parametrize('data',[b'bad asset file bytes!!',struct.pack('<4sII',b'glTF',2,999)+b'\0'*20])
def test_malformed_model_is_not_presented_as_a_valid_inventory(tmp_path,data):
    path=tmp_path/'bad.glb';path.write_bytes(data)
    with pytest.raises(ValueError):inspector.inspect(path)
