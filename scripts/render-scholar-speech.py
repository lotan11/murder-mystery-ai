"""Render only approved Lewis at the approved generation pace, from a server JSON file.

No downloads, provider API, microphone, dynamic command evaluation or voice selection.
The game endpoint chooses current public dialogue; this script is an internal local worker.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def render(input_file, output_directory, model_directory):
    payload = json.loads(input_file.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict) or set(payload) != {"text"} or not isinstance(payload["text"], str) or not 1 <= len(payload["text"].strip()) <= 1500:
        raise ValueError("The internal worker expects bounded public dialogue only.")
    text = payload["text"]
    if importlib.metadata.version("kokoro-onnx") != "0.6.1":
        raise RuntimeError("Use the approved pinned optional Kokoro runtime.")
    source = ROOT / "scripts" / "prepare-casting.py"
    spec = importlib.util.spec_from_file_location("approved_casting_preparation", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("The approved model verifier is missing.")
    preparation = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(preparation)
    # Reuse the exact pinned model and voice asset verifier, explicitly forbidding downloads.
    preparation.ensure_models(model_directory, allow_download=False)
    import numpy as np
    import soundfile as sf
    from kokoro_onnx import Kokoro
    engine = Kokoro(str(model_directory / "kokoro-v1.0.onnx"), str(model_directory / "voices-v1.0.bin"))
    audio, rate = engine.create(text, voice="bm_lewis", speed=0.92, lang="en-gb")
    audio = np.asarray(audio, dtype=np.float32).reshape(-1)
    if rate != 24000 or not np.isfinite(audio).all() or not 0.1 <= len(audio) / rate <= 170 or float(np.sqrt(np.mean(audio * audio))) < 0.00001:
        raise RuntimeError("The neural worker returned an invalid waveform.")
    if not output_directory.is_dir():
        raise RuntimeError("The server output directory is missing.")
    sf.write(str(output_directory / "speech.wav"), audio, rate, subtype="PCM_16")
    manifest = {"text": text, "provider": "kokoro-onnx", "voice": "bm_lewis", "generation_speed": 0.92,
                "duration_ms": round(len(audio) * 1000 / rate, 2)}
    (output_directory / "speech.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--models", type=Path, default=ROOT / "data" / "casting-models")
    args = parser.parse_args()
    try:
        render(args.input.resolve(), args.output.resolve(), args.models.resolve())
    except Exception as exc:
        print(f"Approved local voice worker failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
