import { useEffect, useRef, useState } from "react";
import Stage from "./Stage";
import { useScholarPerformance } from "./ScholarPerformance";
import { useLocalDetectivePerformance } from "./TalkingDetective";
import {
  decodePrivate,
  decodeState,
  dialogueStatus,
  socketURL,
  type PrivateState,
  type RoomState,
} from "./client";
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
    [presentation, setPresentation] = useState<
      "scholar" | "animated" | "original"
    >("scholar"),
    [tvSpeechToken, setTvSpeechToken] = useState(
      () => new URLSearchParams(location.hash.slice(1)).get("speech") || "",
    ),
    [joined, setJoined] = useState(false),
    [privateState, setPrivateState] = useState<PrivateState | null>(null),
    [privateVisible, setPrivateVisible] = useState(false),
    [introduction, setIntroduction] = useState(""),
    [rationale, setRationale] = useState(""),
    [assignments, setAssignments] = useState<Record<string, string>>({});
  const animated = presentation === "animated";
  const privateRole = useRef(""),
    previousAct = useRef<number | null>(null);
  const localSpeechStop = useRef<() => void>(() => {}),
    lastSpeechRevision = useRef<number | null>(null),
    animatedRef = useRef(false);
  const socket = useRef<WebSocket | null>(null),
    voiceRef = useRef(false),
    lastSpoken = useRef("");
  animatedRef.current = view === "tv" && presentation !== "original";
  useEffect(() => {
    voiceRef.current = voice;
    if (!voice) window.speechSynthesis?.cancel();
  }, [voice]);
  useEffect(() => {
    if (!room || (view !== "organizer" && view !== "tv")) return;
    const organizerToken = localStorage.getItem(`organizer:${room}`);
    if (!organizerToken || (view === "tv" && tvSpeechToken)) return;
    const abort = new AbortController();
    fetch(`/api/rooms/${encodeURIComponent(room)}/speech/config`, {
      headers: { Authorization: `Bearer ${organizerToken}` },
      signal: abort.signal,
    })
      .then((response) => (response.ok ? response.json() : null))
      .then((config) => {
        if (!abort.signal.aborted && typeof config?.tv_token === "string")
          setTvSpeechToken(config.tv_token);
      })
      .catch(() => {});
    return () => abort.abort();
  }, [room, view]);
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
      setPrivateState(null);
      setPrivateVisible(false);
      privateRole.current = "";
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
        if (message?.type === "private") {
          if (view !== "guest") return;
          const result = decodePrivate(e.data);
          if (result.error) {
            setPrivateState(null);
            setPrivateVisible(false);
            setError(result.error);
            return;
          }
          if (result.privateState) {
            const next = result.privateState;
            if (privateRole.current !== next.character.id) {
              setPrivateVisible(false);
              setIntroduction("");
              setRationale("");
            }
            privateRole.current = next.character.id;
            setPrivateState(next);
          }
          return;
        }
        const result = decodeState(e.data);
        if (result.error) {
          setError(result.error);
          setRequestNotice("");
        }
        if (result.state) {
          if (
            lastSpeechRevision.current !== result.state.revision ||
            result.state.paused
          )
            localSpeechStop.current();
          lastSpeechRevision.current = result.state.revision;
          if (result.state.paused) window.speechSynthesis?.cancel();
          if (
            previousAct.current !== null &&
            previousAct.current !== 0 &&
            result.state.act === 0
          ) {
            setPrivateVisible(false);
            setIntroduction("");
            setRationale("");
          }
          previousAct.current = result.state.act;
          setState(result.state);
          setRequestNotice("");
          if (
            voiceRef.current &&
            !animatedRef.current &&
            !result.state.paused &&
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
        localSpeechStop.current();
        window.speechSynthesis?.cancel();
        setJoined(false);
        setPrivateState(null);
        setPrivateVisible(false);
        setIntroduction("");
        setRationale("");
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
      localSpeechStop.current();
      setPrivateState(null);
      setPrivateVisible(false);
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
  const detective = dialogueStatus(state?.dialogue_meta);
  const canQuestion = canContribute && !detective.busy;
  const detectiveLabel = detective.busy
    ? "Detective is considering…"
    : detective.label;
  const localPerformance = useLocalDetectivePerformance({
    room,
    dialogue: state?.dialogue || "",
    revision: state?.revision || 0,
    paused: state?.paused || false,
    online: online && !!state,
    token:
      view === "tv"
        ? tvSpeechToken || localStorage.getItem(`organizer:${room}`) || ""
        : "",
    animated: view === "tv" && animated,
    onAnimatedChange: (value) =>
      changePresentation(value ? "animated" : "scholar"),
  });
  const scholarPerformance = useScholarPerformance({
    room,
    dialogue: state?.dialogue || "",
    revision: state?.revision || 0,
    act: state?.act || 0,
    paused: state?.paused || false,
    online: online && !!state,
    token:
      view === "tv"
        ? tvSpeechToken || localStorage.getItem(`organizer:${room}`) || ""
        : "",
    active: view === "tv" && presentation === "scholar",
  });
  localSpeechStop.current = () => {
    localPerformance.stop();
    scholarPerformance.stop();
  };
  function changePresentation(value: "scholar" | "animated" | "original") {
    localSpeechStop.current();
    setPresentation(value);
    animatedRef.current = value !== "original";
    voiceRef.current = false;
    setVoice(false);
    window.speechSynthesis?.cancel();
  }
  const control = (action: string) => send({ type: "control", action });
  function link(role: View) {
    const base = `${location.origin}/?view=${role}&room=${encodeURIComponent(room)}`;
    return role === "tv" && tvSpeechToken
      ? `${base}#speech=${encodeURIComponent(tvSpeechToken)}`
      : base;
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
            <br />A careful investigation. A reasoned conclusion.
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
          <p>
            <a className="share-link" href="/?view=character-lab">
              Inspect the Scholar 3D workbench ↗
            </a>
            <a className="share-link" href="/?view=casting">
              Compare detective looks and British voices ↗
            </a>
            <a className="share-link" href="/?view=audition">
              Open the voice and avatar audition ↗
            </a>
          </p>
          <p className="footnote">
            LOCAL PROTOTYPE · OPTIONAL AI · NO MICROPHONE CAPTURE
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
              {view === "tv" && state && (
                <>
                  <div className="tv-presentation">
                    <label htmlFor="tv-presentation">TV presentation</label>
                    <select
                      id="tv-presentation"
                      value={presentation}
                      onChange={(event) =>
                        changePresentation(
                          event.target.value as
                            | "scholar"
                            | "animated"
                            | "original",
                        )
                      }
                    >
                      <option value="scholar">
                        Scholar · approved portrait + Lewis
                      </option>
                      <option value="animated">
                        Animated sample · Windows voice fallback
                      </option>
                      <option value="original">
                        Original procedural stage
                      </option>
                    </select>
                  </div>
                  {localPerformance.controls}
                  {presentation === "scholar" && scholarPerformance.controls}
                </>
              )}
              {view !== "guest" && state && (
                <Stage
                  avatar={
                    view === "tv"
                      ? presentation === "scholar"
                        ? scholarPerformance.avatar
                        : animated
                          ? localPerformance.avatar
                          : undefined
                      : undefined
                  }
                  avatarCaption={
                    view === "tv" && presentation === "scholar"
                      ? "APPROVED SCHOLAR CONCEPT · 3D RIG PENDING"
                      : undefined
                  }
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
                  <span>· {detectiveLabel}</span>
                </div>
                <p>“{state?.dialogue || "Connecting to the manor…"}”</p>
                <label className="voice">
                  <input
                    type="checkbox"
                    checked={voice}
                    disabled={view === "tv" && presentation !== "original"}
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
              {view !== "tv" && !!state?.introductions?.length && (
                <section
                  className="public-introductions panel"
                  aria-label="Public introductions"
                >
                  <div className="eyebrow">SHARED WITH THE TABLE</div>
                  <h2>The introductions</h2>
                  {state.introductions.map((entry) => (
                    <article key={entry.guest_id}>
                      <h3>
                        {entry.character_name}{" "}
                        <small>played by {entry.name}</small>
                      </h3>
                      <p>{entry.text}</p>
                    </article>
                  ))}
                </section>
              )}
              {state?.act === 4 && !!state.accusations?.length && (
                <section className="public-accusations panel">
                  <div className="eyebrow">THE TABLE’S DEDUCTIONS</div>
                  <h2>Reasons revealed</h2>
                  {state.accusations.map((entry) => (
                    <article key={entry.guest_id}>
                      <h3>
                        {entry.name} accused{" "}
                        {state.suspects.find(
                          (person) => person.id === entry.suspect,
                        )?.name || entry.suspect}
                      </h3>
                      <p>{entry.rationale || "No written reason submitted."}</p>
                    </article>
                  ))}
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
                    <section
                      className="panel dialogue-provider"
                      aria-label="Detective integration status"
                    >
                      <div className="eyebrow">DETECTIVE INTEGRATION</div>
                      <h3>{detectiveLabel}</h3>
                      <p className="muted">
                        {detective.provider === "openai"
                          ? detective.aiAvailable
                            ? "AI provider configured and available."
                            : "AI provider configured but unavailable."
                          : "Scripted provider selected. No paid AI requests are made."}
                      </p>
                      {detective.provider === "openai" && (
                        <p className="provider-usage">
                          AI request attempts: {detective.callsUsed}/
                          {detective.callsLimit}
                        </p>
                      )}
                      <p className="tiny">{detective.reason}</p>
                      <p className="tiny">
                        Resetting the case does not reset its AI allowance.
                        Model assistance selects released clues and approved
                        remarks; the facts remain authored.
                      </p>
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
                {view === "guest" && joined && privateState && (
                  <>
                    <section
                      className="panel private-character"
                      aria-label="Your private character"
                    >
                      <div className="eyebrow">FOR YOUR EYES ONLY</div>
                      <h2>Your character</h2>
                      <h3>{privateState.character.name}</h3>
                      <p className="muted">
                        Your private brief stays on this screen. Hide it before
                        sharing your phone.
                      </p>
                      <button
                        type="button"
                        aria-expanded={privateVisible}
                        aria-controls="private-brief"
                        onClick={() => setPrivateVisible(!privateVisible)}
                      >
                        {privateVisible
                          ? "Hide private brief"
                          : "Reveal private brief"}
                      </button>
                      {privateVisible && (
                        <div id="private-brief" className="private-brief">
                          <p>{privateState.character.private_brief}</p>
                          <h3>Your objectives</h3>
                          <ul>
                            {privateState.character.objectives.map(
                              (objective, index) => (
                                <li key={index}>{objective}</li>
                              ),
                            )}
                          </ul>
                          <p className="performance-notes">
                            {privateState.character.performance_notes}
                          </p>
                        </div>
                      )}
                    </section>
                    <section className="panel introduction-form">
                      <div className="eyebrow">INTRODUCE YOURSELF</div>
                      <h3>A place in the story</h3>
                      <p className="muted">
                        Suggested public introduction:{" "}
                        {privateState.character.public_intro}
                      </p>
                      <form
                        onSubmit={(event) => {
                          event.preventDefault();
                          send({
                            type: "introduce",
                            text: introduction.trim(),
                          });
                        }}
                      >
                        <button
                          type="button"
                          className="text-button"
                          disabled={!canContribute || !state || state.act > 1}
                          onClick={() =>
                            setIntroduction(privateState.character.public_intro)
                          }
                        >
                          Use suggested introduction
                        </button>
                        <label htmlFor="introduction">
                          Your public introduction
                        </label>
                        <textarea
                          id="introduction"
                          maxLength={240}
                          value={introduction}
                          onChange={(event) =>
                            setIntroduction(event.target.value)
                          }
                          placeholder={privateState.character.public_intro}
                        />
                        <button
                          disabled={
                            !canContribute ||
                            !state ||
                            state.act > 1 ||
                            !introduction.trim()
                          }
                        >
                          {privateState.introduction_submitted
                            ? "Update introduction"
                            : "Submit introduction"}
                        </button>
                      </form>
                      <p className="tiny">
                        Introductions are optional and public. Write only what
                        you want everyone to see. Available in the gathering and
                        Act 1.
                      </p>
                      {privateState.introduction_submitted && (
                        <p className="joined">
                          Your introduction is shared with the table.
                        </p>
                      )}
                    </section>
                  </>
                )}
                <section className="panel">
                  <div className="eyebrow">ASK THE DETECTIVE</div>
                  <h3>A question of character</h3>
                  {view === "guest" && state && (
                    <blockquote className="guest-response" aria-live="polite">
                      <span>WOBBLEBOTTOM · {detectiveLabel}</span>
                      <p>“{state.dialogue}”</p>
                    </blockquote>
                  )}
                  <p className="detective-status" role="status">
                    {detectiveLabel}
                  </p>
                  {detective.aiAvailable && (
                    <p className="ai-disclosure">
                      Questions are sent to the configured AI provider with
                      released evidence. Your private card is not included.
                      Include only what you want to send in your question.
                    </p>
                  )}
                  {state?.dialogue_meta?.source === "fallback" && (
                    <p className="tiny fallback-notice">{detective.reason}</p>
                  )}
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      if (canQuestion)
                        send({ type: "dialogue", text: text.trim() });
                    }}
                  >
                    <label htmlFor="question">
                      Simulated microphone · typed input
                    </label>
                    <textarea
                      disabled={!canQuestion}
                      id="question"
                      value={text}
                      onChange={(e) => setText(e.target.value)}
                      maxLength={500}
                      placeholder="What do we know about the glass?"
                      required
                    />
                    <button disabled={!canQuestion || !text.trim()}>
                      Send observation ↗
                    </button>
                  </form>
                  <div className="quick-prompts" aria-label="Detective prompts">
                    <button
                      disabled={!canQuestion}
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
                      disabled={!canQuestion}
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
                    No audio is recorded.{" "}
                    {detective.aiAvailable
                      ? "Optional AI assistance uses released evidence; scripted fallback remains available."
                      : "Scripted responses work without an AI service."}
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
                    <label htmlFor="rationale">
                      Reason for your accusation
                    </label>
                    <textarea
                      id="rationale"
                      maxLength={300}
                      value={rationale}
                      onChange={(event) => setRationale(event.target.value)}
                      placeholder="Which released clue supports your deduction?"
                      disabled={!canContribute || state?.act !== 3}
                    />
                    <p className="tiny">
                      Your reason is visible only to you until the finale.
                      Sending a new accusation replaces your previous vote and
                      reason.
                    </p>
                    {privateState?.own_vote && (
                      <p className="own-vote" aria-live="polite">
                        Recorded:{" "}
                        {state?.suspects.find(
                          (person) =>
                            person.id === privateState.own_vote?.suspect,
                        )?.name || privateState.own_vote.suspect}
                        .{" "}
                        {privateState.own_vote.rationale ||
                          "No written reason."}
                      </p>
                    )}
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
                            send({
                              type: "accuse",
                              suspect: s.id,
                              rationale: rationale.trim(),
                            })
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
                    state.guests.map((g) =>
                      view === "organizer" ? (
                        <div className="assignment-row" key={g.id}>
                          <strong>{g.name}</strong>
                          <p>
                            {g.character_name || "Role pending"}
                            {g.introduced
                              ? " · Introduced"
                              : " · Introduction optional"}
                          </p>
                          <label htmlFor={`character-${g.id}`}>
                            Character for {g.name}
                          </label>
                          <select
                            id={`character-${g.id}`}
                            value={
                              assignments[g.id] ||
                              g.character_id ||
                              "investigator"
                            }
                            onChange={(event) =>
                              setAssignments({
                                ...assignments,
                                [g.id]: event.target.value,
                              })
                            }
                            disabled={
                              !online || state.act !== 0 || state.paused
                            }
                          >
                            <option value="ada">Ada Blackthorn</option>
                            <option value="felix">Felix Finch</option>
                            <option value="margot">Dr. Margot Vale</option>
                            <option value="investigator">
                              Visiting investigator
                            </option>
                          </select>
                          <button
                            disabled={
                              !online ||
                              state.act !== 0 ||
                              state.paused ||
                              (assignments[g.id] || g.character_id) ===
                                g.character_id
                            }
                            aria-label={`Assign character to ${g.name}`}
                            onClick={() =>
                              send({
                                type: "control",
                                action: "assign",
                                guest_id: g.id,
                                character_id:
                                  assignments[g.id] ||
                                  g.character_id ||
                                  "investigator",
                              })
                            }
                          >
                            Assign character
                          </button>
                        </div>
                      ) : (
                        <span key={g.id}>
                          {g.name}
                          {g.character_name ? ` · ${g.character_name}` : ""}
                        </span>
                      ),
                    )
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
          Prototype integrations: procedural avatar · {detective.label} · typed
          microphone simulation · no lip-sync
        </p>
        <span>BLACKTHORN MANOR / 01</span>
      </footer>
    </div>
  );
}
