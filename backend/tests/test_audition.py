"""Audition assets are fixed public samples, never a live synthesizer or room export."""
import copy
import json
import wave

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.audition import MAX_MANIFEST_BYTES, SAMPLES, SYNTHETIC_TIMING_SOURCE, TIMING_SOURCE, router


@pytest.fixture
def assets(tmp_path, monkeypatch):
    monkeypatch.setenv("MYSTERY_AUDITION_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def client(assets):
    # The standalone router has no room-store lifespan or private game data access.
    standalone = FastAPI()
    standalone.include_router(router)
    with TestClient(standalone) as client:
        yield client


def prepare(root, timing_source=TIMING_SOURCE):
    samples = []
    for sample_id, (title, text) in SAMPLES.items():
        words = text.split()
        with wave.open(str(root / f"david-{sample_id}.wav"), "wb") as audio:
            audio.setnchannels(1); audio.setsampwidth(2); audio.setframerate(16000)
            audio.writeframes(b"\0\0" * 48000)
        samples.append({"id": sample_id, "title": title, "text": text,
                        "words": words, "wtimes": [100 * i for i in range(len(words))],
                        "wdurations": [80] * len(words)})
    manifest = {"version": 1, "timing_source": timing_source, "voices": [
        {"id": "david", "name": "Local David test slot", "locale": "en-US", "gender": "Male", "samples": samples}
    ]}
    write(root, manifest)
    return manifest


def write(root, manifest):
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def test_missing_assets_are_unavailable_without_creating_files_or_rooms(client, assets):
    response = client.get("/api/audition")
    assert response.status_code == 200
    assert response.json()["available"] is False and response.json()["voices"] == []
    assert "prepare-audition.ps1" in response.json()["message"]
    assert list(assets.iterdir()) == []
    assert client.get("/api/audition/audio/david/greeting").status_code == 404


def test_manifest_exposes_authored_samples_and_safe_audio_routes(client, assets):
    original = prepare(assets)
    response = client.get("/api/audition")
    assert response.status_code == 200
    result = response.json()
    assert result["available"] and result["synthetic"] is False
    assert result["timing_source"] == TIMING_SOURCE
    assert result["voices"][0]["samples"][0]["words"] == original["voices"][0]["samples"][0]["words"]
    for sample in result["voices"][0]["samples"]:
        assert sample["audio_url"] == f"/api/audition/audio/david/{sample['id']}"
        assert sample["duration_ms"] == 3000
        audio = client.get(sample["audio_url"])
        assert audio.status_code == 200 and audio.headers["content-type"] == "audio/wav"
        assert audio.content[:4] == b"RIFF" and audio.headers["cache-control"] == "no-store"
    assert client.get("/api/audition/audio/zira/greeting").status_code == 404
    assert list(assets.glob("*.sqlite3")) == []


def test_synthetic_fixture_is_explicitly_labeled_not_real_speech(client, assets):
    prepare(assets, SYNTHETIC_TIMING_SOURCE)
    result = client.get("/api/audition").json()
    assert result["available"] and result["synthetic"] is True
    assert result["timing_source"] == SYNTHETIC_TIMING_SOURCE


def test_json_bom_from_windows_powershell_is_supported(client, assets):
    manifest = prepare(assets)
    (assets / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8-sig")
    assert client.get("/api/audition").json()["available"] is True


@pytest.mark.parametrize("change", [
    lambda m: m.update(version=True),
    lambda m: m.update(version=999),
    lambda m: m.update(voices=[]),
    lambda m: m.update(timing_source="private-room-secret"),
    lambda m: m["voices"][0].update(id="../private"),
    lambda m: m["voices"][0].update(locale="xx-private"),
    lambda m: m["voices"][0].update(samples=[]),
    lambda m: m["voices"][0]["samples"][0].update(id="../private"),
    lambda m: m["voices"][0]["samples"][0].update(text="Unapproved private room text"),
    lambda m: m["voices"][0]["samples"][0].update(words=["A different secret"]),
    lambda m: m["voices"][0]["samples"][0].update(wtimes=[-1] * 18),
    lambda m: m["voices"][0]["samples"][0].update(wtimes=[float("nan")] * 18),
    lambda m: m["voices"][0]["samples"][0].update(wdurations=[]),
    lambda m: m["voices"][0]["samples"][0].update(wdurations=[9000] * 18),
])
def test_malformed_manifest_is_unavailable_not_a_server_error(client, assets, change):
    manifest = prepare(assets)
    change(manifest)
    write(assets, manifest)
    response = client.get("/api/audition")
    assert response.status_code == 200 and response.json()["available"] is False
    assert "private" not in json.dumps(response.json()).lower()
    assert client.get("/api/audition/audio/david/greeting").status_code == 404


def test_oversized_or_invalid_json_is_unavailable(client, assets):
    for text in ("{invalid-json", "x" * (MAX_MANIFEST_BYTES + 1)):
        (assets / "manifest.json").write_text(text, encoding="utf-8")
        assert client.get("/api/audition").json()["available"] is False


@pytest.mark.parametrize("voice_id,sample_id", [("private", "greeting"), ("david", "secret"), ("..", "greeting")])
def test_audio_allowlist_rejects_unknown_ids(client, assets, voice_id, sample_id):
    prepare(assets)
    (assets / "private.wav").write_bytes(b"Not a permitted recording")
    assert client.get(f"/api/audition/audio/{voice_id}/{sample_id}").status_code == 404


def test_truncated_audio_invalidates_manifest_without_exposing_bytes(client, assets):
    prepare(assets)
    audio = assets / "david-greeting.wav"
    audio.write_bytes(audio.read_bytes()[:60])
    assert client.get("/api/audition").json()["available"] is False
    assert client.get("/api/audition/audio/david/greeting").status_code == 404


def test_symlink_outside_asset_directory_is_not_served(client, assets, tmp_path):
    prepare(assets)
    outside = tmp_path.parent / (tmp_path.name + "-outside.wav")
    source = assets / "david-greeting.wav"
    outside.write_bytes(source.read_bytes())
    source.unlink()
    try:
        source.symlink_to(outside)
    except OSError:
        pytest.skip("This Windows account cannot create symlinks")
    assert client.get("/api/audition").json()["available"] is False
    assert client.get("/api/audition/audio/david/greeting").status_code == 404
