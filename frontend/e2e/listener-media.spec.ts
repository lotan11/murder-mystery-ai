import { test, expect, type Page } from "@playwright/test";

async function interceptedMicrophoneGuest(
  page: Page,
  room?: { room_id: string; organizer_token?: string },
  permissionMode: "normal" | "denied" | "pending" = "normal",
) {
  const created = room ?? await page.request.post("/api/rooms", { data: {} }).then(response => response.json());
  let socket: { send: (message: string) => void } | null = null;
  await page.routeWebSocket(/\/ws\//, routed => {
    socket = routed;
    const server = routed.connectToServer();
    server.onMessage(message => {
      if (typeof message === "string") {
        try {
          const event = JSON.parse(message);
          if (event.type === "state" && event.data?.listener?.usage)
            event.data.listener.usage.enabled = true;
          message = JSON.stringify(event);
        } catch { /* pass non-JSON WebSocket messages through */ }
      }
      routed.send(message);
    });
    routed.onMessage(message => server.send(message));
  });
  await page.context().grantPermissions(["microphone"]);
  await page.addInitScript(({ mode }) => {
    const original = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
    Object.defineProperty(window, "__listenerTestStreams", { value: [], configurable: true });
    Object.defineProperty(navigator.mediaDevices, "getUserMedia", {
      configurable: true,
      value: async (constraints: MediaStreamConstraints) => {
        if (mode === "denied") throw new DOMException("Permission denied", "NotAllowedError");
        if (mode === "pending") return new Promise<MediaStream>((resolve) => {
          (window as any).__resolveListenerPermission = async () => {
            const stream = await original(constraints);
            (window as any).__listenerTestStreams.push(stream);
            resolve(stream);
          };
        });
        const stream = await original(constraints);
        (window as any).__listenerTestStreams.push(stream);
        return stream;
      },
    });
  }, { mode: permissionMode });
  await page.goto(`/?view=guest&room=${created.room_id}`);
  await page.getByLabel("Your name", { exact: true }).fill("Listener Guest");
  await page.getByRole("button", { name: "Join the investigation" }).click();
  await expect(page.getByRole("heading", { name: "Detective at the table" })).toBeVisible();
  page.on("dialog", dialog => dialog.accept());
  return { roomId: created.room_id as string, organizerToken: created.organizer_token as string | undefined, socket: () => socket };
}

async function micTracksEnded(page: Page) {
  return page.evaluate(() => {
    const streams = (window as any).__listenerTestStreams as MediaStream[];
    return streams.length > 0 && streams.every(stream => stream.getTracks().every(track => track.readyState === "ended"));
  });
}

async function micTracksEnabled(page: Page) {
  return page.evaluate(() => {
    const streams = (window as any).__listenerTestStreams as MediaStream[];
    return streams.length > 0 && streams.every(stream => stream.getAudioTracks().every(track => track.enabled));
  });
}

async function holdDeviceNarration(page: Page) {
  await page.addInitScript(() => {
    const win = window as any;
    win.__deviceNarration = null;
    win.__listenerRecorderStarts = 0;
    win.__listenerAudioHeaders = 0;
    Object.defineProperty(speechSynthesis, "cancel", { configurable: true, value: () => {} });
    Object.defineProperty(speechSynthesis, "speak", {
      configurable: true,
      value: (utterance: SpeechSynthesisUtterance) => {
        win.__deviceNarration = utterance;
        utterance.onstart?.(new Event("start") as SpeechSynthesisEvent);
      },
    });
    const start = MediaRecorder.prototype.start;
    MediaRecorder.prototype.start = function (...args: Parameters<MediaRecorder["start"]>) {
      win.__listenerRecorderStarts += 1;
      return start.apply(this, args);
    };
    const send = WebSocket.prototype.send;
    WebSocket.prototype.send = function (data) {
      if (typeof data === "string") {
        try { if (JSON.parse(data).type === "listener.audio") win.__listenerAudioHeaders += 1; }
        catch { /* non-JSON application messages are unrelated to this check */ }
      }
      return send.call(this, data);
    };
  });
}

async function beginDeviceNarration(page: Page, guest: Awaited<ReturnType<typeof interceptedMicrophoneGuest>>) {
  const state = await page.request.get(`/api/rooms/${guest.roomId}/state`).then(response => response.json());
  state.dialogue = "This device's detective narration is speaking.";
  state.scholar_speaking = false;
  state.listener.usage.enabled = true;
  guest.socket()?.send(JSON.stringify({ type: "state", data: state }));
  await expect.poll(() => page.evaluate(() => Boolean((window as any).__deviceNarration))).toBe(true);
}

async function endDeviceNarration(page: Page) {
  await page.evaluate(() => {
    const win = window as any;
    win.__deviceNarration.onend?.(new Event("end"));
  });
}

async function publishScholarSpeaking(page: Page, room: string, token: string, speaking: boolean) {
  return page.evaluate(({ roomId, capability, active }) => new Promise<void>((resolve, reject) => {
    const win = window as any;
    let ws = win.__scholarSignalSocket as WebSocket | undefined;
    const url = new URL(`/ws/${encodeURIComponent(roomId)}`, location.origin);
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
    url.searchParams.set("role", "tv"); url.searchParams.set("token", capability);
    if (!ws || ws.readyState > WebSocket.OPEN) {
      ws = new WebSocket(url); win.__scholarSignalSocket = ws;
    }
    const timeout = setTimeout(() => reject(new Error("TV speaking state was not acknowledged.")), 8000);
    const onMessage = (event: MessageEvent) => {
      const packet = JSON.parse(event.data);
      if (packet.type === "error") { clearTimeout(timeout); reject(new Error(packet.message)); }
      if (packet.type === "state" && packet.data?.scholar_speaking === active) {
        clearTimeout(timeout); ws?.removeEventListener("message", onMessage); resolve();
      }
    };
    ws.addEventListener("message", onMessage);
    if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: "scholar.speaking", speaking: active }));
    else ws.addEventListener("open", () => ws?.send(JSON.stringify({ type: "scholar.speaking", speaking: active })), { once: true });
  }), { roomId: room, capability: token, active: speaking });
}

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
  expect(outcome.type).toBe("listener.error");
  expect(outcome.message).toContain("Microphone transcription is disabled");
  expect(outcome.bytes).toBeGreaterThan(16 * 1024);
  expect(outcome.bytes).toBeLessThan(512 * 1024);
  expect(outcome.duration).toBeGreaterThan(2.5);
  expect(outcome.duration).toBeLessThan(3.5);
});

test("lobby reset stops live capture and Resume clears a stale confirmation", async ({ browser, page }) => {
  const organizerContext = await browser.newContext();
  const organizer = await organizerContext.newPage();
  const created = await page.request.post("/api/rooms", { data: {} }).then(response => response.json());
  const token = created.organizer_token as string;
  await organizer.addInitScript(({ room, organizerToken }) => localStorage.setItem(`organizer:${room}`, organizerToken),
    { room: created.room_id, organizerToken: token });
  organizer.on("dialog", dialog => dialog.accept());
  await organizer.goto(`/?view=organizer&room=${created.room_id}`);
  const guest = await interceptedMicrophoneGuest(page, { room_id: created.room_id, organizer_token: token });
  expect(guest.roomId).toBe(created.room_id);

  await page.getByRole("button", { name: "Enable microphone" }).click();
  await expect(page.getByText(/Microphone live/)).toBeVisible();
  const state = await page.request.get(`/api/rooms/${guest.roomId}/state`).then(response => response.json());
  const guestRow = state.guests.find((entry: { name: string }) => entry.name === "Listener Guest");
  guest.socket()?.send(JSON.stringify({ type: "listener.confirmation_required", id: "old", text: "A stale sentence." ,
    guests: [{ id: guestRow.id, name: guestRow.name }] }));
  await expect(page.getByText("A stale sentence.", { exact: true })).toBeVisible();
  await expect.poll(() => micTracksEnded(page)).toBe(true);

  await page.getByRole("button", { name: "Resume listening" }).click();
  await expect(page.getByText("A stale sentence.", { exact: true })).toHaveCount(0);
  await expect(page.getByText(/Microphone live/)).toBeVisible();
  await expect.poll(() => page.evaluate(() => ((window as any).__listenerTestStreams as MediaStream[]).length)).toBe(2);

  await organizer.getByRole("button", { name: "Reset this room" }).click();
  await expect(page.getByText("Microphone and listener stopped by room reset.")).toBeVisible();
  await expect.poll(() => micTracksEnded(page)).toBe(true);
  await expect(page.getByRole("button", { name: "Enable microphone" })).toBeVisible();
  await organizerContext.close();
});

test("terminal microphone errors stop capture and keep their explanation visible", async ({ page }) => {
  const guest = await interceptedMicrophoneGuest(page);
  await page.getByRole("button", { name: "Enable microphone" }).click();
  await expect(page.getByText(/Microphone live/)).toBeVisible();
  await expect.poll(async () => {
    const message = await page.locator(".listener-panel [role=status]").innerText();
    if (message.includes("disabled")) return "disabled";
    if (message.includes("does not match")) return "mismatch";
    return message;
  }, { timeout: 8000 }).toBe("disabled");
  await expect(page.getByText("Microphone transcription is disabled. Use typed observation or configure paid transcription.")).toBeVisible({ timeout: 8000 });
  await expect.poll(() => micTracksEnded(page)).toBe(true);
  await expect(page.getByRole("button", { name: "Enable microphone" })).toBeVisible();
});

test("microphone permission denial leaves capture stopped and explains typed fallback", async ({ page }) => {
  const guest = await interceptedMicrophoneGuest(page, undefined, "denied");
  await page.getByRole("button", { name: "Enable microphone" }).click();
  await expect(page.locator(".listener-panel [role=status]")).toContainText("Microphone permission was unavailable");
  await expect(page.getByRole("button", { name: "Enable microphone" })).toBeVisible();
  expect(await page.evaluate(() => ((window as any).__listenerTestStreams as MediaStream[]).length)).toBe(0);
  const state = await page.request.get(`/api/rooms/${guest.roomId}/state`).then(response => response.json());
  expect(state.listener.usage.audio_seconds).toBe(0);
  expect(state.listener.usage.transcription_calls).toBe(0);
});

test("Stop during a pending permission prompt releases the stream granted afterward", async ({ page }) => {
  const guest = await interceptedMicrophoneGuest(page, undefined, "pending");
  await page.getByRole("button", { name: "Enable microphone" }).click();
  await page.getByRole("button", { name: "Stop", exact: true }).click();
  await expect(page.getByRole("button", { name: "Enable microphone" })).toBeVisible();
  await page.evaluate(async () => await (window as any).__resolveListenerPermission());
  await expect.poll(() => page.evaluate(() => ((window as any).__listenerTestStreams as MediaStream[]).length)).toBe(1);
  await expect.poll(() => micTracksEnded(page)).toBe(true);
  const state = await page.request.get(`/api/rooms/${guest.roomId}/state`).then(response => response.json());
  expect(state.listener.usage.audio_seconds).toBe(0);
  expect(state.listener.usage.transcription_calls).toBe(0);
});

test("host pause invalidates an open guest permission prompt", async ({ browser, page }) => {
  const created = await page.request.post("/api/rooms", { data: {} }).then(response => response.json());
  const organizerContext = await browser.newContext();
  const organizer = await organizerContext.newPage();
  await organizer.addInitScript(({ room, token }) => localStorage.setItem(`organizer:${room}`, token),
    { room: created.room_id, token: created.organizer_token });
  organizer.on("dialog", dialog => dialog.accept());
  await organizer.goto(`/?view=organizer&room=${created.room_id}`);
  await expect(organizer.getByRole("button", { name: "Pause evening" })).toBeVisible();

  const guest = await interceptedMicrophoneGuest(page, { room_id: created.room_id, organizer_token: created.organizer_token }, "pending");
  await page.getByRole("button", { name: "Enable microphone" }).click();
  await organizer.getByRole("button", { name: "Pause evening" }).click();
  await expect(organizer.getByRole("button", { name: "Resume evening" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Resume listening" })).toBeVisible();
  await page.evaluate(async () => await (window as any).__resolveListenerPermission());
  await expect.poll(() => page.evaluate(() => ((window as any).__listenerTestStreams as MediaStream[]).length)).toBe(1);
  await expect.poll(() => micTracksEnded(page)).toBe(true);
  const state = await page.request.get(`/api/rooms/${guest.roomId}/state`).then(response => response.json());
  expect(state.listener.usage.audio_seconds).toBe(0);
  expect(state.listener.usage.transcription_calls).toBe(0);
  await organizerContext.close();
});

test("authorized Lewis speaking state suppresses and resumes guest microphone capture", async ({ page }) => {
  const guest = await interceptedMicrophoneGuest(page);
  await page.getByRole("button", { name: "Enable microphone" }).click();
  await expect(page.getByText(/Microphone live/)).toBeVisible();
  await expect.poll(() => micTracksEnabled(page)).toBe(true);
  await publishScholarSpeaking(page, guest.roomId, guest.organizerToken!, true);
  await expect.poll(() => micTracksEnabled(page)).toBe(false);
  await expect(page.getByText("Microphone paused while the detective speaks.")).toBeVisible();
  await publishScholarSpeaking(page, guest.roomId, guest.organizerToken!, false);
  await expect.poll(() => micTracksEnabled(page)).toBe(true);
  await expect(page.getByText(/Microphone live/)).toBeVisible();
  await page.evaluate(() => (window as any).__scholarSignalSocket?.close());
  await page.getByRole("button", { name: "Stop", exact: true }).click();
  await expect.poll(() => micTracksEnded(page)).toBe(true);
});

test("guest device narration suppresses capture immediately and resumes with a fresh clip", async ({ page }) => {
  await holdDeviceNarration(page);
  const guest = await interceptedMicrophoneGuest(page);
  await page.getByRole("checkbox", { name: /Read dialogue aloud/ }).check();
  await page.getByRole("button", { name: "Enable microphone", exact: true }).click();
  await expect(page.getByText(/Microphone live/)).toBeVisible();
  await expect.poll(() => micTracksEnabled(page)).toBe(true);
  const starts = await page.evaluate(() => (window as any).__listenerRecorderStarts as number);
  await beginDeviceNarration(page, guest);
  await expect.poll(() => micTracksEnabled(page)).toBe(false);
  await expect(page.getByText("Microphone paused while the detective speaks.")).toBeVisible();
  // Longer than a recording interval: the interrupted segment must never be uploaded.
  await page.waitForTimeout(3250);
  expect(await page.evaluate(() => (window as any).__listenerAudioHeaders)).toBe(0);
  await endDeviceNarration(page); // no room update is sent to trigger recovery
  await expect.poll(() => micTracksEnabled(page)).toBe(true);
  await expect.poll(() => page.evaluate(() => (window as any).__listenerRecorderStarts)).toBeGreaterThan(starts);
  await expect(page.getByText(/Microphone live/)).toBeVisible();
  await page.getByRole("button", { name: "Stop", exact: true }).click();
  await expect.poll(() => micTracksEnded(page)).toBe(true);
  const state = await page.request.get(`/api/rooms/${guest.roomId}/state`).then(response => response.json());
  expect(state.listener.usage.transcription_calls).toBe(0);
  expect(state.listener.usage.audio_seconds).toBe(0);
});

test("permission granted during local narration starts suppressed and resumes without a room update", async ({ page }) => {
  await holdDeviceNarration(page);
  const guest = await interceptedMicrophoneGuest(page, undefined, "pending");
  await page.getByRole("checkbox", { name: /Read dialogue aloud/ }).check();
  await page.getByRole("button", { name: "Enable microphone", exact: true }).click();
  await expect.poll(() => page.evaluate(() => typeof (window as any).__resolveListenerPermission)).toBe("function");
  await beginDeviceNarration(page, guest);
  await page.evaluate(() => (window as any).__resolveListenerPermission());
  await expect.poll(() => page.evaluate(() => ((window as any).__listenerTestStreams as MediaStream[]).length)).toBe(1);
  await expect.poll(() => micTracksEnabled(page)).toBe(false);
  await expect(page.getByText("Microphone paused while the detective speaks.")).toBeVisible();
  const starts = await page.evaluate(() => (window as any).__listenerRecorderStarts as number);
  await endDeviceNarration(page);
  await expect.poll(() => micTracksEnabled(page)).toBe(true);
  await expect.poll(() => page.evaluate(() => (window as any).__listenerRecorderStarts)).toBeGreaterThan(starts);
  await page.getByRole("button", { name: "Stop", exact: true }).click();
  await expect.poll(() => micTracksEnded(page)).toBe(true);
  expect(await page.evaluate(() => (window as any).__listenerAudioHeaders)).toBe(0);
  const state = await page.request.get(`/api/rooms/${guest.roomId}/state`).then(response => response.json());
  expect(state.listener.usage.transcription_calls).toBe(0);
  expect(state.listener.usage.audio_seconds).toBe(0);
});
