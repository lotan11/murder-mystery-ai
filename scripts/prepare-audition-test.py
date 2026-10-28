"""Generate a clearly labeled synthetic waveform fixture, never a voice-quality sample."""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.audition import SAMPLES


def prepare(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    voices = []
    for voice_id, frequency in (("david", 180), ("zira", 240)):
        samples = []
        for sample_id, (title, text) in SAMPLES.items():
            words = text.split()
            duration_seconds = max(8.0, len(words) * 0.13 + 0.2)
            sample = {"id": sample_id, "title": title, "text": text,
                      "words": words,
                      "wtimes": [index * 130 for index in range(len(words))], "wdurations": [110] * len(words),
                      "duration_ms": duration_seconds * 1000}
            with wave.open(str(output / f"{voice_id}-{sample_id}.wav"), "wb") as audio:
                audio.setnchannels(1)
                audio.setsampwidth(2)
                audio.setframerate(22050)
                frames = []
                for index in range(int(22050 * duration_seconds)):
                    time = index / 22050
                    envelope = min(1.0, time * 30, max(0.0, (duration_seconds - time) * 30))
                    frames.append(struct.pack("<h", int(2500 * envelope * math.sin(2 * math.pi * frequency * time))))
                audio.writeframes(b"".join(frames))
            samples.append(sample)
        voices.append({"id": voice_id, "name": f"TEST waveform ({voice_id} slot, not speech)",
                       "locale": "en-US", "gender": "Male" if voice_id == "david" else "Female",
                       "samples": samples})
    manifest = {"version": 1, "timing_source": "Synthetic test waveform and timings; not recorded speech",
                "voices": voices}
    (output / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    prepare(parser.parse_args().output)
