import { test, expect } from "@playwright/test";

test("consecutive finalized microphone clips independently decode", async ({ page }) => {
  await page.context().grantPermissions(["microphone"]);
  await page.goto("/?view=character-lab");
  const result = await page.evaluate(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const candidates = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus", "audio/mp4"];
    const mimeType = candidates.find((candidate) => MediaRecorder.isTypeSupported(candidate));
    if (!mimeType) throw new Error("No supported MediaRecorder container is available.");
    const clips: Array<{ bytes: number; duration: number }> = [];
    try {
      for (let index = 0; index < 2; index += 1) {
        const recorder = new MediaRecorder(stream, { mimeType });
        const blob = await new Promise<Blob>((resolve, reject) => {
          const timeout = setTimeout(() => reject(new Error("Microphone clip did not finalize.")), 8000);
          recorder.onerror = () => { clearTimeout(timeout); reject(new Error("Fake microphone recorder failed.")); };
          recorder.ondataavailable = (event) => { if (event.data.size) resolve(event.data); };
          recorder.onstop = () => clearTimeout(timeout);
          recorder.start();
          setTimeout(() => recorder.stop(), 3000);
        });
        const context = new AudioContext();
        try {
          const audio = await context.decodeAudioData(await blob.arrayBuffer());
          clips.push({ bytes: blob.size, duration: audio.duration });
        } finally { await context.close(); }
      }
      return { mimeType, clips };
    } finally { stream.getTracks().forEach((track) => track.stop()); }
  });
  expect(result.clips).toHaveLength(2);
  for (const clip of result.clips) {
    expect(clip.bytes).toBeGreaterThan(0);
    expect(clip.bytes).toBeLessThan(512 * 1024);
    expect(clip.duration).toBeGreaterThan(2.5);
    expect(clip.duration).toBeLessThan(3.5);
  }
});

test("the local Uvicorn WebSocket validates a real finalized clip above the former 16 KiB limit", async ({ page }) => {
  await page.goto("/");
  await page.context().grantPermissions(["microphone"]);
  const outcome = await page.evaluate(async () => {
    const created = await fetch("/api/rooms", { method: "POST" }).then((response) => response.json());
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream, { mimeType: "audio/webm;codecs=opus" });
    const clip = await new Promise<Blob>((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error("Microphone clip did not finalize.")), 8000);
      recorder.onerror = () => { clearTimeout(timeout); reject(new Error("Fake microphone recorder failed.")); };
      recorder.ondataavailable = (event) => { if (event.data.size) resolve(event.data); };
      recorder.start();
      setTimeout(() => recorder.stop(), 3000);
    });
    const audioContext = new AudioContext();
    const duration = (await audioContext.decodeAudioData(await clip.arrayBuffer())).duration;
    await audioContext.close();
    const socket = new WebSocket(`ws://${location.host}/ws/${created.room_id}?role=guest`);
    const next = () => new Promise<MessageEvent>((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error("WebSocket response timed out.")), 5000);
      socket.addEventListener("message", (event) => { clearTimeout(timeout); resolve(event); }, { once: true });
      socket.addEventListener("close", () => { clearTimeout(timeout); reject(new Error("WebSocket closed before application validation.")); }, { once: true });
    });
    try {
      await next(); // initial room snapshot
      socket.send(JSON.stringify({ type: "join", name: "Payload Guest" }));
      await next(); // joined
      await next(); // state
      await next(); // private
      socket.send(JSON.stringify({ type: "listener.start", consent: true, source: "microphone" }));
      await next(); // explicit status
      socket.send(JSON.stringify({ type: "listener.audio", duration_seconds: duration, mime_type: recorder.mimeType }));
      await next(); // metadata acknowledgement
      socket.send(await clip.arrayBuffer());
      const result = JSON.parse((await next()).data as string);
      return { type: result.type, message: result.message, bytes: clip.size, duration };
    } finally { socket.close(); stream.getTracks().forEach((track) => track.stop()); }
  });
  expect(outcome.type).toBe("error");
  expect(outcome.message).toContain("Microphone transcription is disabled");
  expect(outcome.bytes).toBeGreaterThan(16 * 1024);
  expect(outcome.bytes).toBeLessThan(512 * 1024);
  expect(outcome.duration).toBeGreaterThan(2.5);
  expect(outcome.duration).toBeLessThan(3.5);
});
