import test from "node:test";
import assert from "node:assert/strict";
import vm from "node:vm";
import ts from "typescript";
import fs from "node:fs";

const source = fs.readFileSync(new URL("./listenerAudio.ts", import.meta.url), "utf8");
const compiled = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText;

function createCaptureRuntime({ permission, current = () => true } = {}) {
  const timers = new Map();
  let timerId = 0, now = 0, tracksStopped = 0, requestedConstraints;
  const recorders = [];
  class FakeRecorder {
    static isTypeSupported() { return true; }
    constructor(_stream, options) { this.mimeType = options?.mimeType || "audio/webm"; this.state = "inactive"; recorders.push(this); }
    start() { this.state = "recording"; }
    stop() {
      if (this.state !== "recording") return;
      this.state = "inactive";
      this.ondataavailable?.({ data: new Blob([`EBML-${recorders.length}-complete-clip`], { type: "audio/webm" }) });
      this.onstop?.();
    }
  }
  const stream = {
    getTracks: () => [{ stop() { tracksStopped++; } }],
    getAudioTracks: () => [{ getSettings: () => ({ echoCancellation: true }) }],
  };
  const context = {
    exports: {},
    require() { return {}; },
    navigator: { mediaDevices: { getUserMedia: constraints => { requestedConstraints = constraints; return permission ?? Promise.resolve(stream); } } },
    MediaRecorder: FakeRecorder,
    performance: { now: () => now },
    setTimeout(callback, delay) { const id = ++timerId; timers.set(id, { callback, delay }); return id; },
    clearTimeout(id) { timers.delete(id); },
  };
  vm.runInNewContext(compiled, context);
  return {
    open: context.exports.openListenerCapture,
    recorders, stream,
    get requestedConstraints() { return requestedConstraints; },
    advance(milliseconds = 3000) {
      now += milliseconds;
      const [id, timer] = timers.entries().next().value || [];
      if (timer) { timers.delete(id); timer.callback(); }
    },
    isCurrent: current,
    get tracksStopped() { return tracksStopped; },
    timerCount: () => timers.size,
  };
}

test("late microphone permission resolution immediately releases tracks and never starts recording", async () => {
  let resolvePermission;
  const permission = new Promise(resolve => { resolvePermission = resolve; });
  const runtime = createCaptureRuntime({ permission, current: () => false });
  const pending = runtime.open({ isCurrent: runtime.isCurrent, onChunk() {}, onError() {}, onStatus() {} });
  resolvePermission(runtime.stream);
  const stop = await pending;
  assert.equal(runtime.recorders.length, 0);
  assert.equal(runtime.tracksStopped, 1);
  stop();
  assert.equal(runtime.tracksStopped, 1);
});

test("capture finalizes each interval with a fresh recorder and stops cleanly", async () => {
  const runtime = createCaptureRuntime();
  const clips = [];
  const stop = await runtime.open({ isCurrent: runtime.isCurrent, onChunk: chunk => clips.push(chunk), onError: assert.fail, onStatus() {} });
  assert.equal(runtime.requestedConstraints.audio.echoCancellation.ideal, true);
  assert.equal(runtime.requestedConstraints.audio.noiseSuppression.ideal, true);
  assert.equal(runtime.requestedConstraints.audio.autoGainControl.ideal, true);
  assert.equal(runtime.recorders.length, 1);
  runtime.advance(3000);
  runtime.advance(0); // start the next independently finalized container segment
  assert.equal(runtime.recorders.length, 2);
  runtime.advance(3000);
  runtime.advance(0);
  assert.equal(runtime.recorders.length, 3);
  await new Promise(resolve => setImmediate(resolve)); // serialized blob delivery completes asynchronously
  assert.equal(clips.length, 2);
  assert.deepEqual(clips.map(chunk => chunk.durationSeconds), [3, 3]);
  assert.notEqual(runtime.recorders[0], runtime.recorders[1]);
  stop();
  assert.equal(runtime.tracksStopped, 1);
  assert.equal(runtime.timerCount(), 0);
});

test("a segment finalized after Stop is discarded", async () => {
  let current = true;
  const runtime = createCaptureRuntime({ current: () => current });
  const clips = [];
  const stop = await runtime.open({ isCurrent: runtime.isCurrent, onChunk: chunk => clips.push(chunk), onError: assert.fail, onStatus() {} });
  current = false;
  stop();
  assert.equal(clips.length, 0);
});
