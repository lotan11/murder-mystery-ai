"""Generate nine fixed-scene, local neural voice samples; no paid API or game integration.

Reproduce in a separate Python 3.12 environment:
  python -m venv data/casting-runtime
  data/casting-runtime/Scripts/python -m pip install -r requirements-casting.txt
  data/casting-runtime/Scripts/python scripts/prepare-casting.py --download

The --download flag retrieves only two pinned public release assets, verifies their
published SHA-256 digests, then runs inference locally. Models and output stay ignored.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MODEL_FILES = {
    "kokoro-v1.0.onnx": {
        "url": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx",
        "bytes": 325505369,
        "sha256": "beb0d1848dee9a49da392cc3df26958d46cfa35d321edf434f52949153f0df3a",
    },
    "voices-v1.0.bin": {
        "url": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/voices-v1.0.bin",
        "bytes": 28214398,
        "sha256": "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d",
    },
}


def content():
    # Read literal public constants without importing FastAPI into this optional runtime.
    # Authored scenes have one authority: backend/casting.py.
    tree = ast.parse((ROOT / "backend" / "casting.py").read_text(encoding="utf-8"))
    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in {"VOICES", "SCENES", "PROVENANCE"}:
                values[name] = ast.literal_eval(node.value)
    if set(values) != {"VOICES", "SCENES", "PROVENANCE"}:
        raise RuntimeError("The authored casting content is missing.")
    return values


def verified(path, metadata):
    if not path.is_file() or path.stat().st_size != metadata["bytes"]:
        return False
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest() == metadata["sha256"]


def ensure_models(directory, allow_download):
    directory.mkdir(parents=True, exist_ok=True)
    for name, metadata in MODEL_FILES.items():
        destination = directory / name
        if verified(destination, metadata):
            print("Verified cached", name, flush=True)
            continue
        if not allow_download:
            raise RuntimeError(f"Missing or unverified {name}; run again with --download for the pinned public release.")
        temporary = directory / (name + ".partial")
        request = urllib.request.Request(metadata["url"], headers={"User-Agent": "Wobblebottom-Casting-Generator/1.0"})
        print("Downloading public model asset", name, flush=True)
        count, progress = 0, 0
        with urllib.request.urlopen(request, timeout=60) as response, temporary.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                count += len(chunk)
                if count > metadata["bytes"]:
                    raise RuntimeError("The public model download exceeded its pinned size.")
                output.write(chunk)
                if count - progress >= 50 * 1024 * 1024:
                    progress = count
                    print(f"  {count // (1024 * 1024)} MiB", flush=True)
        if not verified(temporary, metadata):
            raise RuntimeError("The model asset failed its published size/SHA-256 check; it was not activated.")
        temporary.replace(destination)
        print("Verified", name, flush=True)


def generate(output, model_dir, download=False):
    definitions = content()
    ensure_models(model_dir, download)
    try:
        import numpy as np
        import soundfile as sf
        from kokoro_onnx import Kokoro
    except ImportError as exc:
        raise RuntimeError("Install requirements-casting.txt in the optional isolated casting runtime first.") from exc
    if importlib.metadata.version("kokoro-onnx") != "0.6.1":
        raise RuntimeError("Use pinned kokoro-onnx 0.6.1 for this approval comparison.")
    output.mkdir(parents=True, exist_ok=True)
    print("Loading local full-precision Kokoro v1.0 model...", flush=True)
    kokoro = Kokoro(str(model_dir / "kokoro-v1.0.onnx"), str(model_dir / "voices-v1.0.bin"))
    available = set(kokoro.get_voices())
    if not set(definitions["VOICES"]) <= available:
        raise RuntimeError("The verified voice set does not contain all three British male candidates.")
    voices = []
    for voice_id, name in definitions["VOICES"].items():
        scenes = []
        for scene_id, (title, text) in definitions["SCENES"].items():
            started = time.monotonic()
            audio, rate = kokoro.create(text, voice=voice_id, speed=0.92, lang="en-gb")
            audio = np.asarray(audio, dtype=np.float32).reshape(-1)
            if rate != 24000 or not np.isfinite(audio).all() or not 0.5 <= len(audio) / rate <= 60 or float(np.sqrt(np.mean(audio * audio))) < 0.00001:
                raise RuntimeError("The local neural renderer returned an invalid waveform.")
            filename = f"{voice_id}-{scene_id}.wav"
            sf.write(str(output / filename), audio, rate, subtype="PCM_16")
            duration = round(len(audio) * 1000 / rate, 2)
            scenes.append({"id": scene_id, "title": title, "text": text, "duration_ms": duration})
            print(f"Prepared {filename}: {duration / 1000:.2f}s audio ({time.monotonic() - started:.2f}s local inference)", flush=True)
        voices.append({"id": voice_id, "name": name, "locale": "en-GB", "gender": "Male", "samples": scenes})
    manifest = {"version": 1, "provider": "kokoro-onnx", "test_fixture": False,
                "voices": voices, "provenance": {**definitions["PROVENANCE"],
                    "speed": 0.92, "sample_rate": 24000,
                    "model_assets": {name: value["sha256"] for name, value in MODEL_FILES.items()}}}
    temporary = output / "manifest.json.partial"
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(output / "manifest.json")
    print("Nine real local neural samples prepared. No paid provider was called; no game avatar was changed.", flush=True)
    print("MIT runtime, Apache-2.0 model. Compare candidates; voice quality and perceived age require listening approval.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "casting")
    parser.add_argument("--model-dir", type=Path, default=ROOT / "data" / "casting-models")
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    try:
        generate(args.output.resolve(), args.model_dir.resolve(), args.download)
    except Exception as exc:
        print(f"Casting preparation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
