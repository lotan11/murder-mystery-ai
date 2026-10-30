"""Claims must be explicit, scoped and grounded before they can drive an interruption."""
import pytest

from backend.listener import _claims, _released_alibi, accept_utterance, empty_memory
from backend.mystery import EVIDENCE


@pytest.mark.parametrize("text", [
    "Ada was not in the library at 9:20.",
    "Ada was never in the library at 9:20.",
    "I heard Ada was in the library at 9:20.",
    "According to the note, Ada was in the library at 9:20.",
    "Rumour: Ada was in the library at 9:20.",
    "Ada was in the library at 9:20 on tape.",
    "Ada might have been in the library at 9:20.",
    "Was Ada in the library at 9:20?",
    "Ada was in the library at 9:20. Felix was in the music room at 9:40.",
])
def test_ambiguous_reported_negative_or_multi_clause_claims_abstain(text):
    assert _claims(text) == []


@pytest.mark.parametrize(("text", "expected"), [
    ("Ada was in the library at 9:20.", {"subject": "ada", "place": "library", "time": "9:20 PM"}),
    ("Felix remained in the music room at 9:15 PM.", {"subject": "felix", "place": "music_room", "time": "9:15 PM"}),
    ("Dr. Margot Vale stood in the conservatory at 9:40.", {"subject": "margot", "place": "conservatory", "time": "9:40 PM"}),
])
def test_single_direct_affirmative_claim_is_scoped(text, expected):
    assert _claims(text) == [expected]


def test_fully_scoped_clauses_remain_independent_without_cross_assignment():
    expected = [
        {"subject": "ada", "place": "library", "time": "9:20 PM"},
        {"subject": "felix", "place": "music_room", "time": "9:40 PM"},
    ]
    assert _claims("Ada was in the library at 9:20; Felix was in the music room at 9:40.") == expected
    assert _claims("Ada was in the library at 9:20 and Felix was in the music room at 9:40.") == expected


@pytest.mark.parametrize("text", [
    "Ada was in the library at 9:20 and Felix was in the music room.",
    "Ada and Felix were in the music room at 9:20.",
    "Ada was in the library and music room at 9:20.",
])
def test_partially_scoped_or_shared_subject_clauses_abstain(text):
    assert _claims(text) == []


@pytest.mark.parametrize(("subject", "time", "places"), [
    ("ada", "9:14 PM", ("music_room",)),
    ("ada", "9:31 PM", ("music_room",)),
    ("ada", "9:20 AM", ("music_room",)),
    ("margot", "9:20 PM", ("music_room",)),
    ("felix", "9:20 PM", ("library",)),
])
def test_released_alibi_does_not_support_wrong_person_time_or_place(subject, time, places):
    assert _released_alibi(EVIDENCE, subject, time, places) is None


def test_released_alibi_requires_exact_server_authored_evidence_and_supported_window():
    clue = next(item for item in EVIDENCE if item["id"] == "alibi")
    assert _released_alibi([clue], "ada", "9:15 PM", ("music_room",)) == clue
    altered = {**clue, "description": "Altered evidence"}
    assert _released_alibi([altered], "ada", "9:20 PM", ("music_room",)) is None


def test_reported_claim_cannot_create_false_contradiction_or_cite_alibi():
    memory = empty_memory()
    for guest_id, name, text in (
        ("g1", "One", "Ada was in the library at 9:20."),
        ("g2", "Two", "Felix remained in the music room at 9:20."),
        ("g3", "Three", "I heard Ada remained in the music room at 9:20 on the recording."),
    ):
        result = accept_utterance(memory, guest_id=guest_id, guest_name=name, text=text, evidence=EVIDENCE)
    assert result["utterance"]["claims"] == []
    assert all(event["type"] != "listener.contradiction" for event in result["events"])
    assert memory["follow_up"] is None


def test_theory_references_are_pruned_with_transcript_retention():
    memory = empty_memory()
    for _ in range(200):
        accept_utterance(memory, guest_id="g1", guest_name="Guest",
                         text="I suspect Ada because of the clock.", evidence=[])
    retained = {item["id"] for item in memory["utterances"]}
    refs = memory["theories"]["ada"]["supporting"] + memory["theories"]["ada"]["challenging"]
    assert len(memory["utterances"]) == 120
    assert len(refs) <= 120
    assert set(refs).issubset(retained)
