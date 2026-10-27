"""Authored role cards remain coherent, private and readable on guest phones."""
import json

from backend.characters import CHARACTERS
from backend.mystery import EVIDENCE, SUSPECTS, TITLE


def test_named_character_identity_matches_the_authoritative_suspects():
    assert set(CHARACTERS) == {"ada", "felix", "margot", "investigator"}
    for suspect in SUSPECTS:
        card = CHARACTERS[suspect["id"]]
        assert card["id"] == suspect["id"]
        assert card["name"] == suspect["name"]
    assert CHARACTERS["investigator"]["name"] == "Visiting investigator"


def test_public_introductions_do_not_disclose_the_solution_or_private_motive():
    public = " ".join(card["public_intro"] for card in CHARACTERS.values()).lower()
    for hidden_fact in ("poison", "forged", "invoice", "culprit", "cyanide", "9:22"):
        assert hidden_fact not in public
    assert "Ada Blackthorn" in CHARACTERS["ada"]["public_intro"]
    assert "Felix Finch" in CHARACTERS["felix"]["public_intro"]
    assert "Dr. Margot Vale" in CHARACTERS["margot"]["public_intro"]


def test_role_cards_are_phone_sized_and_offer_three_playable_objectives():
    fields = {"id", "name", "public_intro", "private_brief", "objectives", "performance_notes"}
    for card in CHARACTERS.values():
        assert set(card) == fields
        assert len(card["private_brief"].split()) <= 80
        assert len(card["private_brief"]) <= 650
        assert len(card["public_intro"]) <= 160
        assert len(card["performance_notes"]) <= 170
        assert len(card["objectives"]) == 3
        assert all(isinstance(goal, str) and 15 <= len(goal) <= 110 for goal in card["objectives"])


def test_culprit_actor_knows_guilt_but_no_player_must_fabricate_evidence():
    margot = CHARACTERS["margot"]["private_brief"]
    assert "You are the culprit" in margot
    assert "forged invoices" in margot
    assert "need not lie" in margot
    for identity in ("ada", "felix"):
        brief = CHARACTERS[identity]["private_brief"]
        assert "did not kill" in brief
        assert "alibi" in brief
        assert not any(time in brief for time in ("9:15", "9:22", "9:23", "9:27"))
    investigator = CHARACTERS["investigator"]["private_brief"]
    assert "not a fourth suspect" in investigator
    assert "no secret evidence" in investigator


def test_role_details_are_not_added_to_public_case_definitions():
    public_case = json.dumps({"title": TITLE, "suspects": SUSPECTS, "evidence": EVIDENCE})
    for card in CHARACTERS.values():
        assert card["private_brief"] not in public_case
        assert card["performance_notes"] not in public_case
        assert all(goal not in public_case for goal in card["objectives"])
