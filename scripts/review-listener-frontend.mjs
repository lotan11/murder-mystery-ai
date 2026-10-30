// Offline review of the original listener branch. No real microphone or provider.
// Run from repo root: node scripts/review-listener-frontend.mjs
// Optional LISTENER_REVIEW_URL changes the local secure-context origin.
import vm from 'node:vm';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import ts from '../frontend/node_modules/typescript/lib/typescript.js';
import { chromium } from '../frontend/node_modules/playwright/index.mjs';

const directory = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(directory, '..');
const revision = execFileSync('git', ['rev-parse', process.env.LISTENER_REVIEW_REF || '1f8bab0bcf7092b360b213b8796af778d94654d7'], { cwd: root, encoding: 'utf8' }).trim();
const app = execFileSync('git', ['show', `${revision}:frontend/src/App.tsx`], { cwd: root, encoding: 'utf8' });
const source = app.slice(app.indexOf('  async function startListener('), app.indexOf('  useEffect(() => {\n    if (state?.paused'));
if (!source.includes('function stopListener')) throw Error('Original listener function extraction failed');
let release;
const pending = new Promise(resolve => { release = resolve; });
let tracksStopped = 0, captureStarts = 0;
const messages = [];
class Recorder {
  static isTypeSupported() { return true; }
  constructor() { this.state = 'inactive'; }
  start() { captureStarts++; this.state = 'recording'; }
  stop() { this.state = 'inactive'; }
}
const stream = {
  getTracks: () => [{ stop() { tracksStopped++; } }],
  getAudioTracks: () => [{ getSettings: () => ({ echoCancellation: true }) }],
};
const context = {
  joined: true, state: { paused: false, listener: { usage: { enabled: true } } },
  window: { confirm: () => true }, send: message => (messages.push(message.type), true),
  setListening: value => { context.listening = value; }, setMuted: value => { context.muted = value; },
  setListenerStatus: value => { context.status = value; },
  navigator: { mediaDevices: { getUserMedia: () => pending } }, MediaRecorder: Recorder,
  recorder: { current: null }, mediaStream: { current: null },
  socket: { current: { readyState: 1 } }, WebSocket: { OPEN: 1 },
};
vm.runInNewContext(ts.transpile(source + ';globalThis.start=startListener;globalThis.stop=stopListener;', { target: ts.ScriptTarget.ES2022 }), context);
const started = context.start(true);
context.stop(false);
release(stream);
await started;
const delayedPermission = {
  scenario: 'Original startListener: Stop while permission is pending, then resolve permission',
  messages: [...messages], captureStarts, tracksStopped, listening: context.listening,
  recorderState: context.recorder.current?.state, status: context.status,
};
context.stop(true);
context.stop(!context.muted); // exact branch Resume button expression
const resume = {
  scenario: 'Original Mute followed by Resume button expression',
  messages: [...messages], listening: context.listening, muted: context.muted,
};

const browser = await chromium.launch({ headless: true, args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'] });
let chunks;
try {
  const browserContext = await browser.newContext({ permissions: ['microphone'] });
  const page = await browserContext.newPage();
  await page.goto(process.env.LISTENER_REVIEW_URL || 'http://127.0.0.1:8018/?view=character-lab');
  chunks = await page.evaluate(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
    const blobs = [];
    try {
      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(Error('Fake capture timed out')), 15000);
        recorder.onerror = () => { clearTimeout(timeout); reject(Error('Fake capture failed')); };
        recorder.ondataavailable = event => {
          if (event.data.size) blobs.push(event.data);
          if (blobs.length === 2) { clearTimeout(timeout); recorder.stop(); resolve(); }
        };
        recorder.start(3000); // exact branch timeslice
      });
      const audio = new AudioContext();
      try {
        const results = [];
        for (const blob of blobs.slice(0, 2)) {
          const buffer = await blob.arrayBuffer();
          let independentDecode;
          try { independentDecode = { durationSeconds: (await audio.decodeAudioData(buffer.slice(0))).duration }; }
          catch (error) { independentDecode = { error: error.name }; }
          results.push({ bytes: buffer.byteLength, prefix: [...new Uint8Array(buffer).slice(0, 4)], independentDecode });
        }
        return results;
      } finally { await audio.close(); }
    } finally {
      if (recorder.state === 'recording') recorder.stop();
      stream.getTracks().forEach(track => track.stop());
    }
  });
} finally { await browser.close(); }

const evidence = {
  observedAt: new Date().toISOString(), branchRevision: revision,
  scope: 'Original frontend functions in mocked VM plus real Chromium fake-device MediaRecorder; no paid provider or real microphone',
  delayedPermission, resume, mediaRecorder: { mimeType: 'audio/webm;codecs=opus', timesliceMs: 3000, chunks },
};
fs.mkdirSync(path.join(root,'data/listener-review-frontend'),{recursive:true});
fs.writeFileSync(path.join(root,'data/listener-review-frontend/evidence.json'), JSON.stringify(evidence, null, 2) + '\n');
console.log(JSON.stringify(evidence, null, 2));
