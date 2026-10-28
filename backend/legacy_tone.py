"""Normalize known earlier authored phrasing when restoring saved narration."""

REPLACEMENTS = {
    " Case closed. We may now return to the rather less mysterious dessert.": " The investigation is complete.",
    "An admirably direct question. I shall reserve the culprit until the reconstruction; even a good theory must survive the evidence. Ask for a recap or examine a released clue.": "The conclusion will be presented during the final reconstruction. For now, we can review the released evidence or examine a specific clue.",
    "At present our evidence consists chiefly of excellent posture. Ask the host to begin the case and reveal a clue; I shall then have something sturdier to discuss.": "No evidence has been released yet. Ask the host to begin the investigation and reveal the first clue.",
    " Certainty is more becoming than volume.": " Support your conclusion with the evidence.",
    "Means and opportunity deserve separate columns; an unfortunate personality is not a third column.": "Consider means and opportunity separately, and support each conclusion with a released fact.",
    " I recommend keeping both eyebrows available.": " Distinguish established facts from unresolved questions.",
    "; a clock that cannot keep time is a rather poor witness.": ". Establish which source can reliably place the events in time.",
    " Appearance is a famously unreliable investigator.": " Follow the physical evidence rather than appearances.",
    " A useful fact, mercifully, among the opinions.": " Consider what this establishes and what remains uncertain.",
    " Let us distinguish evidence from a well-tailored suspicion.": " We should distinguish established evidence from suspicion.",
    " Guesswork is plentiful; evidence is worth waiting for.": " Further conclusions require additional evidence.",
    " Kindly give me a topic; interpreting meaningful glances remains outside my fee.": " Please choose a topic to examine.",
    "Facts first; dramatic pointing can follow.": "We will base our conclusions on the evidence.",
    "A careful question is worth several impressive guesses.": "A careful question helps us distinguish fact from assumption.",
    "Let us give the evidence a turn before the theatrics.": "Let us review the evidence before drawing a conclusion.",
    "Steady reasoning remains a remarkably unfashionable advantage.": "We should proceed methodically and verify each inference.",
    "Good evening. Welcome to Blackthorn Manor. Keep your theories sharp and your fingerprints to yourself.": "Good evening. I am Detective Reginald P. Wobblebottom. We will examine the evidence carefully and establish what happened at Blackthorn Manor.",
    "A fresh investigation. Try to look surprised this time.": "The investigation has been reset. We will review the evidence from the beginning.",
    "Lord Blackthorn is dead. The tea is cold, the guests are nervous, and I have missed pudding. Let us begin.": "Lord Blackthorn has died. We must establish the circumstances, examine the evidence, and account for each guest’s movements.",
    " Do resist the urge to lick the evidence.": "",
    "The plot thickens. Unlike the soup, it now has substance. Examine the next evidence.": "We will now examine the next stage of the investigation.",
    "Good evening. I am Detective Reginald P. Wobblebottom. Kindly keep your theories sharp, and your fingerprints to yourself.": "Good evening. I am Detective Reginald P. Wobblebottom. We will examine the evidence carefully and establish the facts.",
    "An intriguing observation. Let us distinguish evidence from a stylish suspicion.": "We should examine that observation carefully and distinguish established evidence from suspicion."
}

def serious_saved_dialogue(text):
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    return text
