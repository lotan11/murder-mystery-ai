import test from "node:test";
import assert from "node:assert/strict";
import ts from "typescript";
import { readFileSync } from "node:fs";
const source = ts.transpileModule(
  readFileSync(new URL("./client.ts", import.meta.url), "utf8"),
  { compilerOptions: { module: ts.ModuleKind.ESNext } },
).outputText;
const { socketURL, decodeState } = await import(
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
  room_id: "ABC123", title: "The Last Toast", act: 0, paused: false,
  revision: 0, guests: [], evidence: [], suspects: [], dialogue: "Welcome",
  votes: {}, solution: null,
};
test("complete authoritative snapshots replace room state", () => {
  assert.deepEqual(decodeState(JSON.stringify({ type: "state", data: snapshot })), { state: snapshot });
});
test("incomplete snapshots cannot reach rendering", () => {
  for (const data of [
    { evidence: [] },
    { ...snapshot, guests: [null] },
    { ...snapshot, evidence: [{ id: "clue" }] },
    { ...snapshot, suspects: [{ id: "suspect", name: null }] },
    { ...snapshot, votes: { suspect: "one" } },
  ]) assert.ok(decodeState(JSON.stringify({ type: "state", data })).error);
});
test("structured error payload cannot crash the error banner", () => {
  assert.equal(typeof decodeState('{"type":"error","message":{"unexpected":true}}').error, "string");
});
