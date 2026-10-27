import { useEffect, useRef, useState } from "react";
import Stage from "./Stage";
import { decodeState, socketURL, type RoomState } from "./client";
type View = "tv" | "guest" | "organizer";
const params = new URLSearchParams(location.search);
const initialView = (
  ["tv", "guest", "organizer"].includes(params.get("view") || "")
    ? params.get("view")
    : "organizer"
) as View;
const actNames = [
  "The gathering",
  "A fatal toast",
  "Threads unravel",
  "The final deduction",
  "Case closed",
];
const actInstructions = [
  "Gather the table, share the guest link, then begin the case when everyone is ready.",
  "Establish what happened. Reveal the first clues and compare the clock with the victim’s last confirmed sighting.",
  "Test the alibis. Review the released evidence before deciding whose story still holds together.",
  "Make your deduction. Review motive, means and opportunity, then record an accusation before the host resolves the case.",
  "The case is closed. Compare your deduction with Wobblebottom’s reconstruction.",
];
export default function App() {
  const [view] = useState<View>(initialView),
    [room, setRoom] = useState((params.get("room") || "").toUpperCase()),
    [roomInput, setRoomInput] = useState(
      (params.get("room") || "").toUpperCase(),
    ),
    [state, setState] = useState<RoomState | null>(null),
    [status, setStatus] = useState("Offline"),
    [error, setError] = useState(""),
    [requestNotice, setRequestNotice] = useState(""),
    [name, setName] = useState(""),
    [text, setText] = useState(""),
    [busy, setBusy] = useState(false),
    [voice, setVoice] = useState(false),
    [joined, setJoined] = useState(false);
  const socket = useRef<WebSocket | null>(null),
    voiceRef = useRef(false),
    lastSpoken = useRef("");
  useEffect(() => {
    voiceRef.current = voice;
    if (!voice) window.speechSynthesis?.cancel();
  }, [voice]);
  useEffect(() => {
    if (!room) return;
    let closed = false,
      timer: ReturnType<typeof setTimeout>,
      attempt = 0;
    const token =
      view === "organizer"
        ? localStorage.getItem(`organizer:${room}`) || ""
        : "";
    const connect = () => {
      if (closed) return;
      setJoined(false);
      setStatus("Connecting");
      const url = new URL(socketURL(room, view, token));
      const guest = localStorage.getItem(`guest:${room}`);
      if (view === "guest" && guest) url.searchParams.set("guest_token", guest);
      const ws = new WebSocket(url);
      socket.current = ws;
      ws.onopen = () => {
        attempt = 0;
        setStatus("Live");
      };
      ws.onmessage = (e) => {
        let message;
        try {
          message = JSON.parse(e.data);
        } catch {}
        if (message?.type === "joined") {
          localStorage.setItem(`guest:${room}`, message.guest_token);
          setJoined(true);
          return;
        }
        const result = decodeState(e.data);
        if (result.error) {
          setError(result.error);
          setRequestNotice("");
        }
        if (result.state) {
          setState(result.state);
          setRequestNotice("");
          if (
            voiceRef.current &&
            result.state.dialogue !== lastSpoken.current &&
            "speechSynthesis" in window
          ) {
            speechSynthesis.cancel();
            const speech = new SpeechSynthesisUtterance(result.state.dialogue);
            speech.rate = 0.93;
            speechSynthesis.speak(speech);
          }
          lastSpoken.current = result.state.dialogue;
        }
      };
      ws.onerror = () =>
        setError("Cannot connect to the room. Check the server and room code.");
      ws.onclose = (e) => {
        setStatus("Offline");
        setRequestNotice("");
        if (!closed && e.code !== 1008)
          timer = setTimeout(connect, Math.min(1000 * 2 ** attempt++, 10000));
        else if (e.code === 1008)
          setError(
            "Room access denied. Check your room code or organizer key.",
          );
      };
    };
    connect();
    return () => {
      closed = true;
      clearTimeout(timer);
      socket.current?.close();
      window.speechSynthesis?.cancel();
    };
  }, [room, view]);
  function send(message: object) {
    if (socket.current?.readyState !== WebSocket.OPEN) {
      setError("You are offline. Reconnect before sending.");
      return false;
    }
    setError("");
    socket.current.send(JSON.stringify(message));
    setRequestNotice("Request sent. Waiting for the room to update.");
    return true;
  }
  async function create() {
    setBusy(true);
    setError("");
    try {
      const response = await fetch("/api/rooms", { method: "POST" });
      if (!response.ok)
        throw Error("Room creation failed. Is the server running?");
      const result = await response.json();
      localStorage.setItem(
        `organizer:${result.room_id}`,
        result.organizer_token,
      );
      location.href = `?view=organizer&room=${encodeURIComponent(result.room_id)}`;
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  function enter() {
    const code = roomInput.trim().toUpperCase();
    if (!code) return;
    location.href = `?view=guest&room=${encodeURIComponent(code)}`;
  }
  const online = status === "Live";
  const currentClues = state?.available_evidence;
  const canProgress =
    !!state && state.act >= 1 && state.act <= 3 && !state.paused && online;
  const canContribute =
    online && !!state && !state.paused && (view === "organizer" || joined);
  const control = (action: string) => send({ type: "control", action });
  function link(role: View) {
    return `${location.origin}/?view=${role}&room=${encodeURIComponent(room)}`;
  }
  return (
    <div className={`app view-${view}`}>
      <header className="masthead">
        <a className="brand" href="/">
          <span className="seal">W</span>
          <span>
            WOBBLEBOTTOM<span className="brand-sub">MYSTERY SOCIETY</span>
          </span>
        </a>
        <div className="edition">AN EVENING OF EXCELLENT SUSPICIONS</div>
        <div className={`connection ${online ? "live" : ""}`}>
          <span />
          {status}
        </div>
      </header>
      {!room ? (
        <main className="welcome">
          <div className="eyebrow">
            BLACKTHORN MANOR · INTERACTIVE DINNER MYSTERY
          </div>
          <h1>The Last Toast</h1>
          <p className="intro">
            One extraordinary evening. Three questionable alibis.
            <br />A detective with an entirely unreasonable name.
          </p>
          <div className="welcome-card">
            <h2>Gather your suspects</h2>
            <p>
              Create a room, open the stage on your TV, and invite guests to
              join on their phones.
            </p>
            <button className="primary" onClick={create} disabled={busy}>
              {busy ? "Preparing the manor…" : "Create an evening"}{" "}
              <span>↗</span>
            </button>
            <div className="divider">or join an existing room</div>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                enter();
              }}
            >
              <label htmlFor="room">Room code</label>
              <div className="input-row">
                <input
                  id="room"
                  value={roomInput}
                  onChange={(e) => setRoomInput(e.target.value)}
                  placeholder="Enter room code"
                  required
                />
                <button type="submit">Enter</button>
              </div>
            </form>
          </div>
          <p className="footnote">
            LOCAL PROTOTYPE · SCRIPTED DETECTIVE · NO MICROPHONE CAPTURE
          </p>
        </main>
      ) : (
        <>
          <div className="room-bar">
            <div>
              <span className="eyebrow">TONIGHT’S CASE</span>
              <h1>{state?.title || "The Last Toast"}</h1>
            </div>
            <div className="room-code">
              ROOM <strong>{room}</strong>
              <span>{state?.guests.length || 0} guests at the table</span>
            </div>
            <nav aria-label="Room views">
              {(["tv", "guest", "organizer"] as View[]).map((v) => (
                <a
                  key={v}
                  className={view === v ? "active" : ""}
                  href={link(v)}
                >
                  {v === "tv"
                    ? "TV stage"
                    : v === "guest"
                      ? "Guest notebook"
                      : "Organizer"}
                </a>
              ))}
            </nav>
          </div>
          <main className="room-layout">
            <section className="main-column">
              <div className="chapter">
                <span>
                  ACT {state?.act === 4 ? "FINALE" : state?.act || "—"}
                </span>
                <h2>{actNames[state?.act || 0]}</h2>
                <div className="chapter-line" />
                {state?.paused && (
                  <span className="paused">Evening paused</span>
                )}
              </div>
              {view !== "guest" && state && (
                <Stage
                  evidence={state.evidence}
                  dialogue={state.dialogue}
                  act={state.act}
                  paused={state.paused}
                />
              )}
              {!state && (
                <p className="room-instructions" role="status">
                  Connecting to the manor. The server will restore this room’s
                  latest saved progress.
                </p>
              )}
              {view !== "tv" && state && (
                <p className="room-instructions">
                  {state.paused
                    ? "The evening is paused. The host can resume when the table is ready."
                    : actInstructions[state.act]}
                </p>
              )}
              <section className="transcript" aria-live="polite">
                <div className="eyebrow">
                  DETECTIVE REGINALD P. WOBBLEBOTTOM{" "}
                  <span>· SCRIPTED DIALOGUE</span>
                </div>
                <p>“{state?.dialogue || "Connecting to the manor…"}”</p>
                <label className="voice">
                  <input
                    type="checkbox"
                    checked={voice}
                    onChange={(e) => setVoice(e.target.checked)}
                  />{" "}
                  Read dialogue aloud <span>Device voice · optional</span>
                </label>
              </section>
              {view !== "tv" && (
                <section className="evidence-archive">
                  <div className="eyebrow">
                    THE CASE FILE · {state?.evidence.length || 0} CLUES
                  </div>
                  <h2>Your evidence notebook</h2>
                  {state?.evidence.length ? (
                    state.evidence.map((clue) => (
                      <article key={clue.id}>
                        <h3>{clue.title}</h3>
                        <p>{clue.description}</p>
                      </article>
                    ))
                  ) : (
                    <p className="muted">
                      Evidence will appear here as the organizer reveals it.
                    </p>
                  )}
                </section>
              )}
              {state?.solution && (
                <section className="solution">
                  <span className="eyebrow">THE RECONSTRUCTION</span>
                  <h2>Every toast leaves a trace.</h2>
                  <p>
                    {typeof state.solution === "string"
                      ? state.solution
                      : JSON.stringify(state.solution)}
                  </p>
                </section>
              )}
            </section>
            {view !== "tv" && (
              <aside className="sidebar">
                {view === "organizer" ? (
                  <>
                    <section className="panel">
                      <div className="eyebrow">THE EVENING IS YOURS</div>
                      <h2>Director’s desk</h2>
                      <p className="muted">
                        Reveal each clue, let the table investigate, then move
                        the story forward.
                      </p>
                      <p className="tiny host-progress" aria-live="polite">
                        {state?.paused
                          ? "Paused — resume to reveal clues or advance."
                          : state?.act === 0
                            ? "Ready when your guests are."
                            : state?.act === 4
                              ? "Case closed. Reset to rehearse again."
                              : currentClues === undefined
                                ? "Waiting for the host’s clue list…"
                                : currentClues.length
                                  ? `${currentClues.length} clue${currentClues.length === 1 ? "" : "s"} left in this act. Reveal them before moving on.`
                                  : "All clues in this act are released. Give the table time to discuss, then advance."}
                      </p>
                      <div className="control-grid">
                        <button
                          disabled={!online || state?.act !== 0 || state.paused}
                          onClick={() => control("start")}
                          className="primary"
                        >
                          Begin case
                        </button>
                        <button
                          disabled={!canProgress || !currentClues?.length}
                          onClick={() => control("reveal")}
                        >
                          Reveal next clue
                        </button>
                        <button
                          disabled={
                            !canProgress ||
                            !currentClues ||
                            currentClues.length > 0
                          }
                          onClick={() => control("advance")}
                        >
                          {state?.act === 3 ? "Resolve the case" : "Next act →"}
                        </button>
                        <button
                          disabled={!online}
                          onClick={() =>
                            control(state?.paused ? "resume" : "pause")
                          }
                        >
                          {state?.paused ? "Resume evening" : "Pause evening"}
                        </button>
                      </div>
                      <button
                        className="text-button"
                        disabled={!online}
                        onClick={() => {
                          if (
                            confirm("Reset this room and clear its progress?")
                          )
                            control("reset");
                        }}
                      >
                        Reset this room
                      </button>
                    </section>
                    <section className="panel">
                      <div className="eyebrow">INVITE THE TABLE</div>
                      <h3>One room. Every screen.</h3>
                      <a
                        className="share-link"
                        href={link("tv")}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open TV stage ↗
                      </a>
                      <a
                        className="share-link"
                        href={link("guest")}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open guest notebook ↗
                      </a>
                      <label htmlFor="guestlink">
                        Guest link · copy to share
                      </label>
                      <input
                        id="guestlink"
                        readOnly
                        value={link("guest")}
                        onFocus={(e) => e.target.select()}
                      />
                      <p className="tiny">
                        On phones, use your computer’s network address instead
                        of localhost. Keep the organizer link and browser
                        private.
                      </p>
                    </section>
                  </>
                ) : (
                  <section className="panel">
                    <div className="eyebrow">YOUR PLACE AT THE TABLE</div>
                    <h2>Guest notebook</h2>
                    {!joined ? (
                      <form
                        onSubmit={(e) => {
                          e.preventDefault();
                          send({ type: "join", name: name.trim() });
                        }}
                      >
                        <label htmlFor="name">Your name</label>
                        <input
                          id="name"
                          maxLength={40}
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          placeholder="An impeccably innocent guest"
                          required
                        />
                        <button
                          className="primary"
                          disabled={!online || !name.trim()}
                        >
                          Join the investigation
                        </button>
                      </form>
                    ) : (
                      <p className="joined">
                        ✓ You are at the table. Your questions and accusation
                        sync with the room.
                      </p>
                    )}
                  </section>
                )}
                <section className="panel">
                  <div className="eyebrow">ASK THE DETECTIVE</div>
                  <h3>A question of character</h3>
                  {view === "guest" && state && (
                    <blockquote className="guest-response" aria-live="polite">
                      <span>WOBBLEBOTTOM · SCRIPTED DETECTIVE</span>
                      <p>“{state.dialogue}”</p>
                    </blockquote>
                  )}
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      send({ type: "dialogue", text: text.trim() });
                    }}
                  >
                    <label htmlFor="question">
                      Simulated microphone · typed input
                    </label>
                    <textarea
                      id="question"
                      value={text}
                      onChange={(e) => setText(e.target.value)}
                      maxLength={500}
                      placeholder="What do we know about the glass?"
                      required
                    />
                    <button disabled={!canContribute || !text.trim()}>
                      Send observation ↗
                    </button>
                  </form>
                  <div className="quick-prompts" aria-label="Detective prompts">
                    <button
                      disabled={!canContribute}
                      onClick={() =>
                        send({
                          type: "dialogue",
                          text: "Recap the evidence so far.",
                        })
                      }
                    >
                      Recap evidence
                    </button>
                    <button
                      disabled={!canContribute}
                      onClick={() =>
                        send({
                          type: "dialogue",
                          text: "Give us a spoiler-free hint.",
                        })
                      }
                    >
                      Ask for a hint
                    </button>
                  </div>
                  <p className="tiny">
                    No audio is recorded. Responses use a deterministic dialogue
                    adapter.
                  </p>
                </section>
                {view === "guest" && (
                  <section className="panel">
                    <div className="eyebrow">YOUR DEDUCTION</div>
                    <h3>Who raised the last toast?</h3>
                    <p className="tiny">
                      Accusations open in Act 3. You may change your vote until
                      the case resolves.
                    </p>
                    <p className="tiny" aria-live="polite">
                      Votes recorded:{" "}
                      {state?.votes
                        ? Object.entries(state.votes as Record<string, number>)
                            .map(
                              ([id, count]) =>
                                `${state.suspects.find((s) => s.id === id)?.name || id}: ${count}`,
                            )
                            .join(" · ") || "None yet"
                        : "None yet"}
                    </p>
                    {state?.suspects.map((s) => (
                      <div className="suspect" key={s.id}>
                        <strong>{s.name}</strong>
                        <p>{s.description}</p>
                        <button
                          disabled={
                            !online ||
                            !joined ||
                            state.paused ||
                            state.act !== 3
                          }
                          onClick={() =>
                            send({ type: "accuse", suspect: s.id })
                          }
                        >
                          Accuse {s.name.split(" ")[0]}
                        </button>
                      </div>
                    ))}
                  </section>
                )}
                <section className="panel guest-list">
                  <div className="eyebrow">
                    AT THE TABLE · {state?.guests.length || 0}
                  </div>
                  {state?.guests.length ? (
                    state.guests.map((g) => <span key={g.id}>{g.name}</span>)
                  ) : (
                    <p className="muted">The suspects are arriving.</p>
                  )}
                </section>
              </aside>
            )}
          </main>
        </>
      )}
      {requestNotice && (
        <div className="request-notice" role="status">
          {requestNotice}
        </div>
      )}
      {error && (
        <div className="error" role="alert">
          {error}
          <button onClick={() => setError("")} aria-label="Dismiss error">
            ×
          </button>
        </div>
      )}
      <footer>
        <span>W / MYSTERY SOCIETY</span>
        <p>
          Prototype integrations: procedural avatar · scripted AI · typed
          microphone simulation · no lip-sync
        </p>
        <span>BLACKTHORN MANOR / 01</span>
      </footer>
    </div>
  );
}
