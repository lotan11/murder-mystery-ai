import test from "node:test";
import assert from "node:assert/strict";
import ts from "typescript";
import { readFileSync } from "node:fs";
const source = ts.transpileModule(
  readFileSync(new URL("./client.ts", import.meta.url), "utf8"),
  { compilerOptions: { module: ts.ModuleKind.ESNext } },
).outputText;
const { socketURL, decodeState, decodePrivate, dialogueStatus } = await import(
  `data:text/javascript;base64,${Buffer.from(source).toString("base64")}`
);
test("secure socket URL preserves organizer credentials", () => {
  const u = new URL(
    socketURL("a b", "organizer", "secret&value", "https://example.com"),
  );
  assert.equal(u.protocol, "wss:");
  assert.equal(u.searchParams.get("token"), "secret&value");
  assert.equal(u.pathname, "/ws/a%20b");
});
test("malformed server input produces recovery error", () =>
  assert.ok(decodeState("oops").error));
test("server error is not treated as snapshot", () =>
  assert.deepEqual(decodeState('{"type":"error","message":"Paused"}'), {
    error: "Paused",
  }));
test("unknown event does not overwrite room state", () =>
  assert.deepEqual(decodeState('{"type":"performance","data":{}}'), {}));

const snapshot = {
  room_id: "ABC123",
  title: "The Last Toast",
  act: 0,
  paused: false,
  revision: 0,
  guests: [],
  evidence: [],
  suspects: [],
  dialogue: "Welcome",
  votes: {},
  solution: null,
};
test("complete authoritative snapshots replace room state", () => {
  assert.deepEqual(
    decodeState(JSON.stringify({ type: "state", data: snapshot })),
    { state: snapshot },
  );
});
test("incomplete snapshots cannot reach rendering", () => {
  for (const data of [
    { evidence: [] },
    { ...snapshot, guests: [null] },
    { ...snapshot, evidence: [{ id: "clue" }] },
    { ...snapshot, suspects: [{ id: "suspect", name: null }] },
    { ...snapshot, votes: { suspect: "one" } },
  ])
    assert.ok(decodeState(JSON.stringify({ type: "state", data })).error);
});
test("structured error payload cannot crash the error banner", () => {
  assert.equal(
    typeof decodeState('{"type":"error","message":{"unexpected":true}}').error,
    "string",
  );
});

test("host clue gating accepts server list and rejects malformed metadata", () => {
  const clue = { id: "glass", title: "The untouched port", act: 1 };
  const complete = { ...snapshot, act: 1, available_evidence: [clue] };
  assert.deepEqual(
    decodeState(JSON.stringify({ type: "state", data: complete })).state
      .available_evidence,
    [clue],
  );
  for (const available_evidence of [
    null,
    {},
    [null],
    [{ ...clue, title: null }],
    [{ ...clue, act: "one" }],
  ]) {
    assert.ok(
      decodeState(
        JSON.stringify({
          type: "state",
          data: { ...snapshot, available_evidence },
        }),
      ).error,
    );
  }
});

test("released evidence accepts optional summaries without trusting structured content", () => {
  const clue = {
    id: "note",
    title: "The dismissal letter",
    description: "Full notebook record.",
    act: 3,
    summary: "A short dossier summary.",
  };
  const full = { ...snapshot, act: 3, evidence: [clue] };
  assert.equal(
    decodeState(JSON.stringify({ type: "state", data: full })).state.evidence[0]
      .summary,
    clue.summary,
  );
  const invalid = {
    ...full,
    evidence: [{ ...clue, summary: { unexpected: true } }],
  };
  assert.ok(
    decodeState(JSON.stringify({ type: "state", data: invalid })).error,
  );
});

const privateCard = {
  guest_id: "guest-ada",
  character: {
    id: "ada",
    name: "Ada Blackthorn",
    public_intro: "I am the heir.",
    private_brief: "A private dramatic objective.",
    objectives: ["Ask a careful question."],
    performance_notes: "Keep your composure.",
  },
  introduction_submitted: false,
  own_vote: null,
};
test("private character updates have a separate decoder and never replace public state", () => {
  const packet = JSON.stringify({ type: "private", data: privateCard });
  assert.deepEqual(decodeState(packet), {});
  assert.deepEqual(decodePrivate(packet), { privateState: privateCard });
  assert.deepEqual(
    decodePrivate(JSON.stringify({ type: "state", data: snapshot })),
    {},
  );
});
test("private decoder rejects malformed roles, objectives and vote reasons", () => {
  for (const data of [
    { ...privateCard, character: { ...privateCard.character, id: "unknown" } },
    {
      ...privateCard,
      character: { ...privateCard.character, private_brief: { hidden: true } },
    },
    {
      ...privateCard,
      character: { ...privateCard.character, objectives: [null] },
    },
    {
      ...privateCard,
      own_vote: { suspect: "margot", rationale: { hidden: true } },
    },
    { ...privateCard, own_vote: { suspect: "unknown", rationale: "A reason" } },
  ])
    assert.ok(decodePrivate(JSON.stringify({ type: "private", data })).error);
});
test("extended public participation records validate without accepting early rationales", () => {
  const data = {
    ...snapshot,
    guests: [
      {
        id: "guest",
        name: "Morgan",
        character_id: "ada",
        character_name: "Ada Blackthorn",
        introduced: true,
      },
    ],
    introductions: [
      {
        guest_id: "guest",
        name: "Morgan",
        character_name: "Ada Blackthorn",
        text: "A public introduction.",
      },
    ],
    accusations: [],
  };
  assert.deepEqual(
    decodeState(JSON.stringify({ type: "state", data })).state,
    data,
  );
  assert.ok(
    decodeState(
      JSON.stringify({
        type: "state",
        data: { ...data, introductions: [null] },
      }),
    ).error,
  );
  const accusation = {
    guest_id: "guest",
    name: "Morgan",
    suspect: "margot",
    rationale: "The tray.",
  };
  assert.ok(
    decodeState(
      JSON.stringify({
        type: "state",
        data: { ...data, accusations: [accusation] },
      }),
    ).error,
  );
  assert.ok(
    decodeState(
      JSON.stringify({
        type: "state",
        data: { ...data, act: 4, accusations: [accusation] },
      }),
    ).state,
  );
});

const dialogueMeta = {
  provider: "openai",
  source: "model",
  reason: "ready",
  calls_used: 1,
  calls_limit: 20,
  available: true,
  busy: false,
};
test("dialogue metadata validates optional provider status and request usage", () => {
  assert.deepEqual(
    decodeState(
      JSON.stringify({
        type: "state",
        data: { ...snapshot, dialogue_meta: dialogueMeta },
      }),
    ).state.dialogue_meta,
    dialogueMeta,
  );
  for (const change of [
    { provider: "unknown" },
    { provider: ["openai"] },
    { source: { unexpected: true } },
    { reason: { secret: true } },
    { calls_used: -1 },
    { calls_used: 1.5 },
    { calls_limit: "20" },
    { available: 1 },
    { busy: null },
  ])
    assert.ok(
      decodeState(
        JSON.stringify({
          type: "state",
          data: { ...snapshot, dialogue_meta: { ...dialogueMeta, ...change } },
        }),
      ).error,
    );
});
test("dialogue labels reflect the actual response source and preserve legacy scripted mode", () => {
  assert.equal(dialogueStatus().label, "Scripted detective");
  assert.equal(dialogueStatus().aiAvailable, false);
  assert.equal(dialogueStatus(dialogueMeta).label, "AI-assisted detective");
  assert.equal(
    dialogueStatus({ ...dialogueMeta, source: "scripted" }).label,
    "Scripted detective",
  );
  assert.equal(
    dialogueStatus({ ...dialogueMeta, source: "fallback", reason: "timeout" })
      .label,
    "Scripted fallback",
  );
  assert.match(
    dialogueStatus({ ...dialogueMeta, source: "fallback", reason: "timeout" })
      .reason,
    /took too long/,
  );
  assert.equal(dialogueStatus({ ...dialogueMeta, busy: true }).busy, true);
  assert.equal(
    dialogueStatus({ ...dialogueMeta, available: false }).aiAvailable,
    false,
  );
});
test("provider diagnostics use safe fixed copy instead of raw reason strings or inherited properties", () => {
  for (const reason of [
    "secret diagnostic with user data",
    "__proto__",
    "constructor",
    "toString",
  ]) {
    const presentation = dialogueStatus({
      ...dialogueMeta,
      source: "fallback",
      reason,
    });
    assert.equal(typeof presentation.reason, "string");
    assert.ok(!presentation.reason.includes(reason));
  }
  assert.match(
    dialogueStatus({ ...dialogueMeta, reason: "missing_api_key" }).reason,
    /no key configured/,
  );
  assert.match(
    dialogueStatus({ ...dialogueMeta, reason: "budget_exhausted" }).reason,
    /allowance/,
  );
});
