import { useEffect, useRef, useState } from "react";
import "./casting.css";

type CharacterId = "ashford" | "mercer" | "vale";
type VoiceId = "bm_george" | "bm_daniel" | "bm_lewis";
type SceneId = "arrival" | "evidence" | "reassurance";
type Sample = {
  id: SceneId;
  title: string;
  text: string;
  duration_ms: number;
  audio_url: string;
};
type Voice = {
  id: VoiceId;
  name: string;
  locale: "en-GB";
  gender: "Male";
  samples: Sample[];
};
type Manifest = {
  available: boolean;
  version: number;
  provider: "kokoro-onnx";
  voices: Voice[];
  message?: string;
};
const characters: {
  id: CharacterId;
  title: string;
  brief: string;
  direction: string;
}[] = [
  {
    id: "ashford",
    title: "A · The Classic",
    brief: "Silver hair. Charcoal tailoring. An exacting eye.",
    direction: "Distinguished and understated, with a knowing expression.",
  },
  {
    id: "mercer",
    title: "B · The Modern",
    brief: "Salt-and-pepper beard. Navy suit. Worldly composure.",
    direction: "Warm authority with a quietly skeptical edge.",
  },
  {
    id: "vale",
    title: "C · The Scholar",
    brief: "Round spectacles. Tweed waistcoat. Careful attention.",
    direction: "Intellectual, observant, and gently theatrical.",
  },
];
const voices: { id: VoiceId; name: string; brief: string }[] = [
  {
    id: "bm_george",
    name: "George",
    brief:
      "Listen for measured delivery, space between thoughts, and dry restraint.",
  },
  {
    id: "bm_daniel",
    name: "Daniel",
    brief:
      "Listen for clear articulation and a composed, conversational rhythm.",
  },
  {
    id: "bm_lewis",
    name: "Lewis",
    brief: "Listen for deliberate phrasing and a lightly theatrical cadence.",
  },
];
const scenes: { id: SceneId; title: string }[] = [
  { id: "arrival", title: "Arrival at the manor" },
  { id: "evidence", title: "An observation about evidence" },
  { id: "reassurance", title: "Reassuring the guests" },
];
const sceneDirections: Record<SceneId, string> = {
  arrival: "Direction to judge: a warm introduction, a small pause after the name, then an understated final thought. No grin or comic flourish.",
  evidence: "Direction to judge: a slight skeptical lift on the theory, then a calm return to the evidence. Amusement should never sound dismissive.",
  reassurance: "Direction to judge: softer reassurance, room to breathe between thoughts, and a settled finish. Keep the warmth subtle.",
};
const shortlistKey = "wobblebottom-casting-shortlist-v1";
const allowedCombinations = new Set(
  characters.flatMap((character) =>
    voices.map((voice) => `${character.id}:${voice.id}`),
  ),
);
function readShortlist(): string[] {
  try {
    const value: unknown = JSON.parse(
      localStorage.getItem(shortlistKey) || "[]",
    );
    return Array.isArray(value)
      ? [
          ...new Set(
            value.filter(
              (entry): entry is string =>
                typeof entry === "string" && allowedCombinations.has(entry),
            ),
          ),
        ]
      : [];
  } catch {
    return [];
  }
}
function validManifest(value: unknown): value is Manifest {
  if (!value || typeof value !== "object") return false;
  const data = value as Manifest;
  return (
    typeof data.available === "boolean" &&
    data.provider === "kokoro-onnx" &&
    data.version === 1 &&
    Array.isArray(data.voices) &&
    data.voices.every(
      (voice) =>
        voice &&
        voices.some((candidate) => candidate.id === voice.id) &&
        typeof voice.name === "string" &&
        voice.locale === "en-GB" &&
        voice.gender === "Male" &&
        Array.isArray(voice.samples) &&
        voice.samples.every(
          (sample) =>
            sample &&
            scenes.some((scene) => scene.id === sample.id) &&
            typeof sample.title === "string" &&
            typeof sample.text === "string" &&
            typeof sample.duration_ms === "number" &&
            sample.duration_ms > 0 &&
            typeof sample.audio_url === "string" &&
            sample.audio_url.startsWith("/api/casting/audio/"),
        ),
    )
  );
}

export default function Casting() {
  const [characterId, setCharacterId] = useState<CharacterId>("ashford"),
    [voiceId, setVoiceId] = useState<VoiceId>("bm_george"),
    [sceneId, setSceneId] = useState<SceneId>("arrival");
  const [manifest, setManifest] = useState<Manifest | null>(null),
    [loading, setLoading] = useState(true),
    [error, setError] = useState("");
  const [playing, setPlaying] = useState(false),
    [status, setStatus] = useState(
      "Choose a look and voice, then play a scene.",
    ),
    [shortlist, setShortlist] = useState(readShortlist),
    [saving, setSaving] = useState(true);
  const [portraitState, setPortraitState] = useState<
    Record<string, "ready" | "failed">
  >({});
  const audio = useRef<HTMLAudioElement>(null),
    generation = useRef(0),
    mounted = useRef(false);
  const character = characters.find(
    (candidate) => candidate.id === characterId,
  )!;
  const voice = voices.find((candidate) => candidate.id === voiceId)!;
  const clip = manifest?.voices
    .find((candidate) => candidate.id === voiceId)
    ?.samples.find((sample) => sample.id === sceneId);
  const script =
    clip?.text ||
    manifest?.voices
      .flatMap((candidate) => candidate.samples)
      .find((sample) => sample.id === sceneId)?.text;
  const currentCombination = `${characterId}:${voiceId}`,
    shortlisted = shortlist.includes(currentCombination);
  function stop(message = "Playback stopped.") {
    generation.current += 1;
    if (audio.current) {
      audio.current.pause();
      audio.current.currentTime = 0;
    }
    setPlaying(false);
    setStatus(message);
  }
  useEffect(() => {
    mounted.current = true;
    const abort = new AbortController();
    fetch("/api/casting", { signal: abort.signal })
      .then((response) => {
        if (!response.ok) throw Error("manifest");
        return response.json();
      })
      .then((value) => {
        if (abort.signal.aborted) return;
        if (!validManifest(value)) throw Error("manifest");
        setManifest(value);
        if (!value.available)
          setStatus("British voice clips are not prepared on this server yet.");
      })
      .catch(() => {
        if (!abort.signal.aborted)
          setError(
            "The British voice library could not be loaded. The working game and local Windows audition are still available.",
          );
      })
      .finally(() => {
        if (!abort.signal.aborted) setLoading(false);
      });
    return () => {
      mounted.current = false;
      abort.abort();
      generation.current += 1;
      if (audio.current) {
        audio.current.pause();
        audio.current.removeAttribute("src");
        audio.current.load();
      }
    };
  }, []);
  useEffect(() => {
    try {
      localStorage.setItem(shortlistKey, JSON.stringify(shortlist));
      setSaving(true);
    } catch {
      setSaving(false);
    }
  }, [shortlist]);
  function choose(character: CharacterId, voice: VoiceId) {
    stop("Selection changed. Press Play scene when ready.");
    setCharacterId(character);
    setVoiceId(voice);
    setError("");
  }
  function toggleShortlist(combination: string) {
    setShortlist((current) =>
      current.includes(combination)
        ? current.filter((entry) => entry !== combination)
        : [...current, combination],
    );
  }
  async function play() {
    if (!clip || !manifest?.available || !audio.current) return;
    stop("Loading the selected British voice clip…");
    setError("");
    const ownGeneration = generation.current;
    try {
      audio.current.src = clip.audio_url;
      await audio.current.play();
      if (!mounted.current || ownGeneration !== generation.current) return;
      setPlaying(true);
      setStatus(`Playing ${voice.name} · ${clip.title}.`);
    } catch {
      if (mounted.current && ownGeneration === generation.current)
        setError(
          "This British voice clip could not play. Check the cached recordings, then try Play scene again.",
        );
    }
  }

  return (
    <div className="casting-page">
      <header className="casting-header">
        <a className="brand" href="/">
          <span className="seal">W</span>
          <span>
            WOBBLEBOTTOM
            <span className="brand-sub">CHARACTER & VOICE CASTING</span>
          </span>
        </a>
        <a href="/">Return to the working game ↗</a>
      </header>
      <main className="casting-main">
        <div className="eyebrow">
          AN APPROVAL SANDBOX · THE GAME STAYS UNCHANGED
        </div>
        <h1>Cast the detective.</h1>
        <p className="casting-intro">
          Three looks. Three British voices. One Reginald P. Wobblebottom.
          <br />
          Compare each pairing with the same three scenes, then keep a local
          shortlist.
        </p>
        <div className="casting-layout">
          <section className="casting-look-panel">
            <fieldset className="casting-character-options">
              <legend>Character concept</legend>
              {characters.map((candidate) => (
                <label
                  key={candidate.id}
                  className={candidate.id === characterId ? "selected" : ""}
                >
                  <input
                    type="radio"
                    name="casting-character"
                    checked={candidate.id === characterId}
                    onChange={() => choose(candidate.id, voiceId)}
                  />
                  <strong>{candidate.title}</strong>
                  <span>{candidate.brief}</span>
                </label>
              ))}
            </fieldset>
            <div
              className="casting-portrait"
              aria-label="Selected character concept"
            >
              <img
                src={`/casting/${character.id}.png`}
                alt={`${character.title}: ${character.direction}`}
                className={
                  portraitState[character.id] === "ready" ? "ready" : ""
                }
                onLoad={() =>
                  setPortraitState((current) => ({
                    ...current,
                    [character.id]: "ready",
                  }))
                }
                onError={() =>
                  setPortraitState((current) => ({
                    ...current,
                    [character.id]: "failed",
                  }))
                }
              />
              {portraitState[character.id] !== "ready" && (
                <div className="casting-portrait-pending">
                  {portraitState[character.id] === "failed"
                    ? "This concept portrait is still being prepared."
                    : "Loading concept portrait…"}
                </div>
              )}
              <div className="casting-portrait-label">
                <strong>{character.title}</strong>
                <span>Concept portrait — not a rigged 3D avatar</span>
              </div>
            </div>
            <p className="casting-direction">
              {character.direction} Every concept is an interpretation of
              Wobblebottom, not a separate suspect.
            </p>
          </section>
          <aside className="casting-desk">
            <section className="panel">
              <div className="eyebrow">THE VOICE CANDIDATES</div>
              <h2>British voices. Real clips.</h2>
              <p className="casting-note">
                Offline Kokoro neural voices · British English · male. Listen
                for character and maturity; these names do not guarantee an age
                or a particular emotional performance.
              </p>
              <fieldset className="casting-voice-options">
                <legend>Voice candidate</legend>
                {voices.map((candidate) => (
                  <label
                    key={candidate.id}
                    className={voiceId === candidate.id ? "selected" : ""}
                  >
                    <input
                      type="radio"
                      name="casting-voice"
                      checked={voiceId === candidate.id}
                      onChange={() => choose(characterId, candidate.id)}
                    />
                    <strong>{candidate.name}</strong>
                    <span>{candidate.brief}</span>
                  </label>
                ))}
              </fieldset>
              <label htmlFor="casting-scene">Audition scene</label>
              <select
                id="casting-scene"
                value={sceneId}
                onChange={(event) => {
                  stop("Scene changed. Press Play scene when ready.");
                  setSceneId(event.target.value as SceneId);
                  setError("");
                }}
              >
                {scenes.map((scene) => (
                  <option value={scene.id} key={scene.id}>
                    {manifest?.voices
                      .flatMap((candidate) => candidate.samples)
                      .find((sample) => sample.id === scene.id)?.title ||
                      scene.title}
                  </option>
                ))}
              </select>
              <div className="casting-actions">
                <button
                  className="primary"
                  onClick={play}
                  disabled={loading || !manifest?.available || !clip}
                >
                  Play scene
                </button>
                <button onClick={() => stop()} disabled={!playing}>
                  Stop playback
                </button>
              </div>
              <p className="casting-status" role="status">
                {loading ? "Checking the local British voice library…" : status}
              </p>
              {!loading && (!manifest?.available || !clip) && (
                <p className="casting-unavailable">
                  This voice or scene is unavailable until its Kokoro recording
                  is prepared. No Windows US voice is substituted.
                </p>
              )}
              {error && (
                <p className="casting-error" role="alert">
                  {error}
                </p>
              )}
            </section>
            <section className="panel">
              <div className="eyebrow">YOUR CURRENT PAIRING</div>
              <h3>
                {character.title} + {voice.name}
              </h3>
              <button
                onClick={() => toggleShortlist(currentCombination)}
                aria-pressed={shortlisted}
              >
                {shortlisted ? "Remove from shortlist" : "Add to shortlist"}
              </button>
              <p className="casting-note">
                {saving
                  ? "Shortlist saved only on this device."
                  : "Browser storage is unavailable; this shortlist lasts until you leave."}{" "}
                Saving is not approval and does not activate a new character or
                voice in the game.
              </p>
            </section>
          </aside>
        </div>
        <section className="casting-script" aria-label="Current casting script">
          <span className="eyebrow">IDENTICAL SCENE TEXT FOR EVERY VOICE</span>
          <p>
            {script ||
              "The scene text will appear here when the British voice clips are available."}
          </p>
          <p className="casting-note">{sceneDirections[sceneId]}</p>
          <span className="casting-caption-note">
            A still concept portrait accompanies real audio. No mouth animation
            or 3D rig is being demonstrated here.
          </span>
        </section>
        <section
          className="casting-overview panel"
          aria-label="Nine character and voice combinations"
        >
          <div className="eyebrow">THE COMPARISON BOARD</div>
          <h2>Nine possible pairings</h2>
          <p className="casting-note">
            Select a pairing below, then press Play scene. Selection never
            starts audio automatically.
          </p>
          <div className="casting-table-wrap">
            <table>
              <thead>
                <tr>
                  <th scope="col">Character concept</th>
                  {voices.map((candidate) => (
                    <th key={candidate.id} scope="col">
                      {candidate.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {characters.map((candidate) => (
                  <tr key={candidate.id}>
                    <th scope="row">{candidate.title}</th>
                    {voices.map((voiceCandidate) => {
                      const key = `${candidate.id}:${voiceCandidate.id}`;
                      return (
                        <td key={key}>
                          <button
                            className={
                              currentCombination === key ? "selected" : ""
                            }
                            aria-label={`Select ${candidate.title} with ${voiceCandidate.name}`}
                            onClick={() =>
                              choose(candidate.id, voiceCandidate.id)
                            }
                          >
                            {currentCombination === key
                              ? "Selected"
                              : "Compare"}
                            {shortlist.includes(key) && (
                              <span className="casting-star"> ★</span>
                            )}
                          </button>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="casting-note">
            Neural delivery responds to the authored wording, punctuation, and
            pace. It is not a precise control for emotion, inflection, or
            acting; the final voice and rig still need approval.
          </p>
        </section>
        <section
          className="casting-shortlist panel"
          aria-label="Local casting shortlist"
        >
          <div className="eyebrow">KEPT FOR YOUR NEXT REVIEW</div>
          <h2>Your shortlist</h2>
          {shortlist.length ? (
            <div>
              {shortlist.map((combination) => {
                const [character, voice] = combination.split(":");
                const title = `${characters.find((candidate) => candidate.id === character)?.title} + ${voices.find((candidate) => candidate.id === voice)?.name}`;
                return (
                  <span key={combination}>
                    {title}
                    <button
                      aria-label={`Remove ${title} from shortlist`}
                      onClick={() => toggleShortlist(combination)}
                    >
                      ×
                    </button>
                  </span>
                );
              })}
            </div>
          ) : (
            <p className="casting-note">
              No pairings saved yet. Add a pairing after listening; your working
              game remains unchanged.
            </p>
          )}
        </section>
      </main>
      <audio
        ref={audio}
        preload="none"
        onEnded={() => {
          setPlaying(false);
          setStatus(
            "Scene complete. Compare another pairing or keep it on your shortlist.",
          );
        }}
      />
    </div>
  );
}
