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


test("guest local device narration suppresses its own microphone",async({page})=>{
 await page.addInitScript(()=>{
  (window as any).__reviewSpoken=false;
  Object.defineProperty(speechSynthesis,'cancel',{configurable:true,value:()=>{}});
  Object.defineProperty(speechSynthesis,'speak',{configurable:true,value:(utterance:SpeechSynthesisUtterance)=>{
   (window as any).__reviewSpoken=true;utterance.onstart?.(new Event('start') as any);
  }});
 });
 const guest=await interceptedMicrophoneGuest(page);
 await page.getByRole('checkbox',{name:/Read dialogue aloud/}).check();
 await page.getByRole('button',{name:'Enable microphone',exact:true}).click();
 await expect(page.getByText(/Microphone live/)).toBeVisible();
 const state=await page.request.get(`/api/rooms/${guest.roomId}/state`).then(r=>r.json());
 state.dialogue='Local review narration is active.';state.scholar_speaking=false;state.listener.usage.enabled=true;
 guest.socket()?.send(JSON.stringify({type:'state',data:state}));
 await expect.poll(()=>page.evaluate(()=>(window as any).__reviewSpoken)).toBe(true);
 await page.waitForTimeout(100);
 const flags=await page.evaluate(()=>({spoken:(window as any).__reviewSpoken,enabled:((window as any).__listenerTestStreams as MediaStream[]).flatMap(s=>s.getAudioTracks()).map(t=>({enabled:t.enabled,state:t.readyState}))}));
 console.log('LOCAL_NARRATION_REVIEW',JSON.stringify(flags));
 expect(flags.enabled.length).toBeGreaterThan(0);
 expect(flags.enabled.every(track=>!track.enabled)).toBe(true);
});
