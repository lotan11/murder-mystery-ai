"""Probe longer public Lewis narration through the real optional local worker.

Run with the core project Python after preparing the optional casting runtime/models.
No downloads, provider calls, room access or changes to live speech configuration.
Only the small report is checked in; waveform/sidecar/input remain under ignored data/.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import wave

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FIELDS = ('welcome', 'start', 'advance')
TIMEOUT_SECONDS = 40


def main():
    # Use only established public event narration, not evidence/solution/private cards.
    case_path = ROOT / 'backend/cases/blackthorn.json'
    case_bytes = case_path.read_bytes()
    case = json.loads(case_bytes)
    lines = [case['narration'][name] for name in PUBLIC_FIELDS]
    if any(not isinstance(line, str) or not line.strip() for line in lines):
        raise ValueError('Expected public narration fields are missing')
    text = ' '.join(lines)
    words = len(text.split())
    if not 40 <= words <= 80 or not 1 <= len(text) <= 1500:
        raise ValueError('Longer probe must remain a bounded 40–80 word public sample')
    runtime = ROOT / 'data/casting-runtime' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    if not runtime.is_file():
        raise RuntimeError('Prepare the optional local casting runtime first; this probe never installs or downloads it')
    output = ROOT / 'data/scholar-long-timing-proof'
    output.mkdir(parents=True, exist_ok=True)
    # Remove only this probe's fixed prior outputs so a missing fresh sidecar cannot reuse stale cues.
    for name in ('speech.wav', 'speech.json', 'speech-timing.json', 'worker-error.log'):
        path = output / name
        if path.is_file() or path.is_symlink():
            path.unlink()
    payload = output / 'input.json'
    payload.write_text(json.dumps({'text': text}, ensure_ascii=False), encoding='utf-8')
    started = time.monotonic()
    completed = subprocess.run(
        [str(runtime), str(ROOT / 'scripts/render-scholar-speech.py'), '--input', str(payload),
         '--output', str(output), '--models', str(ROOT / 'data/casting-models')],
        cwd=str(ROOT), capture_output=True, timeout=TIMEOUT_SECONDS,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
        env={key: value for key, value in os.environ.items()
             if 'API_KEY' not in key.upper() and not key.upper().endswith('_TOKEN')},
    )
    elapsed = time.monotonic() - started
    if completed.returncode:
        # Keep diagnostic details local, not in committed report or UI.
        (output / 'worker-error.log').write_bytes(completed.stderr)
        raise RuntimeError('Optional local worker failed; inspect ignored worker-error.log')
    sys.path.insert(0, str(ROOT))
    from backend.scholar_speech import _read_render
    result = _read_render(output, text)
    timing = result.get('phoneme_timing')
    if timing is None:
        raise RuntimeError('The worker produced no actual model timing; do not substitute guessed cues')
    audio_path = output / 'speech.wav'
    sidecar_path = output / 'speech-timing.json'
    with wave.open(str(audio_path), 'rb') as audio:
        frames = audio.getnframes()
        rate = audio.getframerate()
        if rate != 24000 or audio.getnchannels() != 1 or audio.getsampwidth() != 2:
            raise RuntimeError('Unexpected approved worker audio format')
    duration = frames / rate
    cues = timing['phonemes']
    if not cues or any(cue['start'] < 0 or cue['end'] > duration for cue in cues):
        raise RuntimeError('Model cue lies outside its own waveform')
    gaps = [cues[0]['start']] + [right['start'] - left['end'] for left, right in zip(cues, cues[1:])] + [duration - cues[-1]['end']]
    if min(gaps) < 0:
        raise RuntimeError('Model cues overlap')
    report = {
        'probe': 'longer public narration, real local worker',
        'case_id': case['id'], 'case_version': case['version'],
        'source': 'backend/cases/blackthorn.json', 'source_sha256': hashlib.sha256(case_bytes).hexdigest(),
        'public_source_fields': ['narration.' + name for name in PUBLIC_FIELDS],
        'concatenated_for_validation_only': True,
        'text': text, 'word_count': words, 'character_count': len(text),
        'punctuation_count': sum(text.count(mark) for mark in '.!?;:'),
        'voice': result['voice'], 'provider': result['provider'],
        'generation_speed': .92, 'approved_playback_rate': result['playback_rate'],
        'sample_rate': rate, 'frames': frames, 'duration_seconds': duration,
        'model_timing_source': timing['source'], 'timing_clock': timing['clock'],
        'phoneme_count': len(cues), 'zero_duration_cues': sum(cue['start'] == cue['end'] for cue in cues),
        'first_cue_start_seconds': cues[0]['start'], 'last_cue_end_seconds': cues[-1]['end'],
        'max_uncovered_gap_seconds': max(gaps), 'out_of_bounds_cues': 0, 'overlapping_cues': 0,
        'sidecar_bytes': sidecar_path.stat().st_size,
        'audio_sha256': hashlib.sha256(audio_path.read_bytes()).hexdigest(),
        'sidecar_sha256': hashlib.sha256(sidecar_path.read_bytes()).hexdigest(),
        'worker_elapsed_seconds_observed': round(elapsed, 3), 'worker_timeout_seconds': TIMEOUT_SECONDS,
        'validated_through': 'backend.scholar_speech._read_render using exact WAV frame clock',
        'paid_calls': False, 'downloads': False, 'live_game_modified': False,
        'limitations': [
            'One bounded concatenation of public narration, not every case line or the 1500-character maximum.',
            'Model-predicted spans are not manually annotated ground truth or a perceptual lip-sync evaluation.',
            'No claim about internal synthesis batch count; worker timing output is checked as delivered.',
            'Observed generation time is local evidence, not a performance guarantee on other machines.',
            'Waveform and timing sidecar belong to this same inference; repeated neural syntheses may differ.',
        ],
    }
    destination = ROOT / 'assets/character-production/lewis-long-timing-proof.json'
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ['word_count', 'duration_seconds', 'phoneme_count', 'sidecar_bytes', 'worker_elapsed_seconds_observed', 'out_of_bounds_cues', 'overlapping_cues']}))


if __name__ == '__main__':
    main()
