"""The approval sandbox serves fixed scenes and neural clips, never synthesizes over HTTP."""
import json
import wave

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.casting import MAX_MANIFEST_BYTES, SCENES, VOICES, router


@pytest.fixture
def assets(tmp_path, monkeypatch):
    monkeypatch.setenv("MYSTERY_CASTING_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def client(assets):
    application = FastAPI()
    application.include_router(router)
    with TestClient(application) as client:
        yield client


def write(root, manifest):
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def prepare(root):
    voices = []
    for voice_id, name in VOICES.items():
        samples = []
        for scene_id, (title, text) in SCENES.items():
            with wave.open(str(root / f"{voice_id}-{scene_id}.wav"), "wb") as audio:
                audio.setnchannels(1); audio.setsampwidth(2); audio.setframerate(24000)
                audio.writeframes(b"\0\0" * 24000)
            samples.append({"id": scene_id, "title": title, "text": text, "duration_ms": 999999})
        voices.append({"id": voice_id, "name": name, "locale": "en-GB", "gender": "Male", "samples": samples})
    manifest = {"version": 1, "provider": "kokoro-onnx", "voices": voices, "test_fixture": True}
    write(root, manifest)
    return manifest


def test_missing_casting_files_leave_working_game_independent(client, assets):
    response = client.get("/api/casting")
    assert response.status_code == 200 and response.json()["available"] is False
    assert response.json()["voices"] == [] and "prepare-casting.py" in response.json()["message"]
    assert list(assets.iterdir()) == []
    assert response.headers["cache-control"] == "no-store"
    assert client.post("/api/casting", json={"text": "No live synthesis"}).status_code == 405


def test_three_voices_share_identical_authored_scenes_and_valid_audio(client, assets):
    prepare(assets)
    response = client.get("/api/casting")
    assert response.status_code == 200
    result = response.json()
    assert result["available"] and result["provider"] == "kokoro-onnx" and result["test_fixture"] is True
    assert result["provenance"]["model_license"] == "Apache-2.0"
    assert result["provenance"]["code_license"] == "MIT"
    assert "no word timings" in result["provenance"]["timing"]
    assert result["provenance"]["speed"] == 0.92
    assert result["provenance"]["sample_rate"] == 24000
    assert "GPLv3+" in result["provenance"]["dependency_notice"]
    assert "not a voice-quality sample" in result["provenance"]["speech_source"]
    assert len(result["provenance"]["model_assets"]["kokoro-v1.0.onnx"]) == 64
    assert {voice["id"] for voice in result["voices"]} == set(VOICES)
    for voice in result["voices"]:
        assert voice["locale"] == "en-GB" and voice["gender"] == "Male"
        for scene in voice["samples"]:
            assert scene["text"] == SCENES[scene["id"]][1]
            assert scene["duration_ms"] == 1000
            assert "words" not in scene and "wtimes" not in scene
            expected = f"/api/casting/audio/{voice['id']}/{scene['id']}"
            assert scene["audio_url"] == expected
            audio = client.get(expected)
            assert audio.status_code == 200 and audio.content[:4] == b"RIFF"
            assert audio.headers["content-type"] == "audio/wav" and audio.headers["cache-control"] == "no-store"
    assert list(assets.glob("*.sqlite3")) == []


@pytest.mark.parametrize("change", [
    lambda m: m.update(version=True),
    lambda m: m.update(provider="paid-external"),
    lambda m: m.update(voices=[]),
    lambda m: m.update(test_fixture="not a boolean"),
    lambda m: m["voices"][0].update(id="../private"),
    lambda m: m["voices"][0].update(name="Unapproved speaker"),
    lambda m: m["voices"][0].update(locale="en-US"),
    lambda m: m["voices"][0].update(samples=[]),
    lambda m: m["voices"][0]["samples"][0].update(id="../private"),
    lambda m: m["voices"][0]["samples"][0].update(text="Hidden game solution or private role"),
    lambda m: m["voices"][0]["samples"][0].update(title="Wrong script"),
])
def test_malformed_manifest_is_unavailable_not_a_server_error(client, assets, change):
    manifest = prepare(assets)
    change(manifest)
    write(assets, manifest)
    result = client.get("/api/casting")
    assert result.status_code == 200 and result.json()["available"] is False
    assert "private role" not in result.text
    assert client.get("/api/casting/audio/bm_george/arrival").status_code == 404


@pytest.mark.parametrize("voice_id,scene_id", [("private", "arrival"), ("bm_george", "secret"), ("bm_george", "..")])
def test_only_fixed_voice_and_scene_ids_can_be_requested(client, assets, voice_id, scene_id):
    prepare(assets)
    (assets / "private.wav").write_bytes(b"An unrelated file")
    assert client.get(f"/api/casting/audio/{voice_id}/{scene_id}").status_code == 404


def test_duplicate_voice_or_scene_rejected(client, assets):
    manifest = prepare(assets)
    manifest["voices"][1] = manifest["voices"][0]
    write(assets, manifest)
    assert client.get("/api/casting").json()["available"] is False
    manifest = prepare(assets)
    manifest["voices"][0]["samples"][1] = manifest["voices"][0]["samples"][0]
    write(assets, manifest)
    assert client.get("/api/casting").json()["available"] is False


def test_oversized_invalid_json_or_truncated_audio_rejected(client, assets):
    for text in ("{invalid", "x" * (MAX_MANIFEST_BYTES + 1)):
        (assets / "manifest.json").write_text(text, encoding="utf-8")
        assert client.get("/api/casting").json()["available"] is False
    prepare(assets)
    audio = assets / "bm_george-arrival.wav"
    audio.write_bytes(audio.read_bytes()[:60])
    assert client.get("/api/casting").json()["available"] is False
    assert client.get("/api/casting/audio/bm_george/arrival").status_code == 404


def test_asset_symlink_outside_casting_directory_is_rejected(client, assets, tmp_path):
    prepare(assets)
    source = assets / "bm_george-arrival.wav"
    outside = tmp_path.parent / (tmp_path.name + "-outside.wav")
    outside.write_bytes(source.read_bytes()); source.unlink()
    try:
        source.symlink_to(outside)
    except OSError:
        pytest.skip("This Windows account cannot create symlinks")
    assert client.get("/api/casting").json()["available"] is False
    assert client.get("/api/casting/audio/bm_george/arrival").status_code == 404
