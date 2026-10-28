const characterIds = ["ada", "felix", "margot", "investigator"];
export type Evidence = {
  id: string;
  title: string;
  description: string;
  summary?: string;
  act: number;
};
export type CharacterId = "ada" | "felix" | "margot" | "investigator";
export type PrivateState = {
  guest_id: string;
  character: {
    id: CharacterId;
    name: string;
    public_intro: string;
    private_brief: string;
    objectives: string[];
    performance_notes: string;
  };
  introduction_submitted: boolean;
  own_vote: { suspect: string; rationale: string } | null;
};
export type DialogueMeta = {
  provider: "scripted" | "openai";
  source: "scripted" | "model" | "fallback";
  reason: string;
  calls_used: number;
  calls_limit: number;
  available: boolean;
  busy: boolean;
};
export type RoomState = {
  room_id: string;
  title: string;
  act: number;
  paused: boolean;
  revision: number;
  guests: {
    id: string;
    name: string;
    character_id?: CharacterId;
    character_name?: string;
    introduced?: boolean;
  }[];
  introductions?: {
    guest_id: string;
    name: string;
    character_name: string;
    text: string;
  }[];
  accusations?: {
    guest_id: string;
    name: string;
    suspect: string;
    rationale: string;
  }[];
  evidence: Evidence[];
  available_evidence?: Pick<Evidence, "id" | "title" | "act">[];
  suspects: { id: string; name: string; description: string }[];
  dialogue: string;
  dialogue_meta?: DialogueMeta;
  performance?: { emotion: string; gesture: string };
  votes: unknown;
  solution: string | null;
  listener?: {
    utterances: { id: string; sequence: number; guest_id: string; speaker: string; text: string; follow_up_answer: boolean }[];
    theories: Record<string, { status: string; supporting: string[]; challenging: string[] }>;
    follow_up: { target_guest_id: string; target_name: string; question: string; answer?: string; answered?: boolean } | null;
    interventions: { target_guest_id: string; target_name: string; question: string }[];
    usage: { enabled: boolean; reason: string; audio_seconds: number; audio_limit_seconds: number; transcription_calls: number; estimated_cost_usd: number; retained_audio: false };
  };
};
export function socketURL(
  room: string,
  role: string,
  token: string,
  origin = location.origin,
) {
  const url = new URL(`/ws/${encodeURIComponent(room)}`, origin);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.searchParams.set("role", role);
  if (token) url.searchParams.set("token", token);
  return url.toString();
}
export function decodeState(raw: string): {
  state?: RoomState;
  error?: string;
} {
  try {
    const msg = JSON.parse(raw);
    if (msg.type === "error")
      return {
        error:
          typeof msg.message === "string" && msg.message
            ? msg.message
            : "The room rejected that request.",
      };
    if (msg.type === "state") {
      const data = msg.data;
      const record = (value: unknown): value is Record<string, unknown> =>
        typeof value === "object" && value !== null && !Array.isArray(value);
      const strings = (value: unknown, keys: string[]) =>
        record(value) && keys.every((key) => typeof value[key] === "string");
      const validListener = (value: unknown) => {
        if (value === undefined) return true;
        if (!record(value) || !Array.isArray(value.utterances) || !record(value.theories) || !Array.isArray(value.interventions) ||
            !(value.follow_up === null || record(value.follow_up)) || !record(value.usage)) return false;
        if (!value.utterances.every((item) => record(item) && strings(item, ["id", "guest_id", "speaker", "text"]) &&
            Number.isInteger(item.sequence) && typeof item.follow_up_answer === "boolean")) return false;
        return value.usage.retained_audio === false && typeof value.usage.enabled === "boolean" &&
          typeof value.usage.reason === "string" && Number.isInteger(value.usage.audio_seconds) &&
          Number.isInteger(value.usage.audio_limit_seconds) && Number.isInteger(value.usage.transcription_calls) &&
          typeof value.usage.estimated_cost_usd === "number";
      };
      if (
        record(data) &&
        strings(data, ["room_id", "title", "dialogue"]) &&
        Number.isInteger(data.act) &&
        Number(data.act) >= 0 &&
        Number(data.act) <= 4 &&
        Number.isInteger(data.revision) &&
        Number(data.revision) >= 0 &&
        typeof data.paused === "boolean" &&
        Array.isArray(data.guests) &&
        data.guests.every(
          (guest) =>
            strings(guest, ["id", "name"]) &&
            (guest.character_id === undefined ||
              characterIds.includes(guest.character_id)) &&
            (guest.character_name === undefined ||
              typeof guest.character_name === "string") &&
            (guest.introduced === undefined ||
              typeof guest.introduced === "boolean"),
        ) &&
        (data.introductions === undefined ||
          (Array.isArray(data.introductions) &&
            data.introductions.every((entry) =>
              strings(entry, ["guest_id", "name", "character_name", "text"]),
            ))) &&
        (data.accusations === undefined ||
          (Array.isArray(data.accusations) &&
            data.accusations.every((entry) =>
              strings(entry, ["guest_id", "name", "suspect", "rationale"]),
            ) &&
            (data.act === 4 || data.accusations.length === 0))) &&
        Array.isArray(data.suspects) &&
        data.suspects.every((suspect) =>
          strings(suspect, ["id", "name", "description"]),
        ) &&
        Array.isArray(data.evidence) &&
        data.evidence.every(
          (clue) =>
            strings(clue, ["id", "title", "description"]) &&
            Number.isInteger(clue.act) &&
            (clue.summary === undefined || typeof clue.summary === "string"),
        ) &&
        (data.available_evidence === undefined ||
          (Array.isArray(data.available_evidence) &&
            data.available_evidence.every(
              (clue) =>
                strings(clue, ["id", "title"]) && Number.isInteger(clue.act),
            ))) &&
        record(data.votes) &&
        Object.values(data.votes).every(
          (count) => Number.isInteger(count) && Number(count) >= 0,
        ) &&
        (data.dialogue_meta === undefined ||
          validDialogueMeta(data.dialogue_meta)) &&
        validListener(data.listener) &&
        (data.solution === null || typeof data.solution === "string")
      )
        return { state: data as RoomState };
      return {
        error: "An incomplete room update arrived. Reconnect to recover.",
      };
    }
    return {};
  } catch {
    return {
      error: "An unreadable room update arrived. Reconnect to recover.",
    };
  }
}

/** Private data stays in memory and is never merged into a public room snapshot. */
export function decodePrivate(raw: string): {
  privateState?: PrivateState;
  error?: string;
} {
  try {
    const message = JSON.parse(raw);
    if (message?.type !== "private") return {};
    const data = message.data;
    const character = data?.character;
    const string = (value: unknown) => typeof value === "string";
    if (
      data &&
      typeof data.guest_id === "string" &&
      data.guest_id &&
      character &&
      characterIds.includes(character.id) &&
      [
        character.name,
        character.public_intro,
        character.private_brief,
        character.performance_notes,
      ].every(string) &&
      Array.isArray(character.objectives) &&
      character.objectives.length > 0 &&
      character.objectives.every(string) &&
      typeof data.introduction_submitted === "boolean" &&
      (data.own_vote === null ||
        (data.own_vote &&
          ["ada", "felix", "margot"].includes(data.own_vote.suspect) &&
          string(data.own_vote.rationale)))
    )
      return { privateState: data as PrivateState };
    return {
      error:
        "An incomplete private character update arrived. Reconnect to restore your card.",
    };
  } catch {
    return {
      error:
        "An unreadable private character update arrived. Reconnect to restore your card.",
    };
  }
}

function validDialogueMeta(value: unknown): value is DialogueMeta {
  if (typeof value !== "object" || value === null || Array.isArray(value))
    return false;
  const meta = value as Record<string, unknown>;
  return (
    typeof meta.provider === "string" &&
    ["scripted", "openai"].includes(meta.provider) &&
    typeof meta.source === "string" &&
    ["scripted", "model", "fallback"].includes(meta.source) &&
    typeof meta.reason === "string" &&
    Number.isInteger(meta.calls_used) &&
    Number(meta.calls_used) >= 0 &&
    Number.isInteger(meta.calls_limit) &&
    Number(meta.calls_limit) >= 0 &&
    typeof meta.available === "boolean" &&
    typeof meta.busy === "boolean"
  );
}

const dialogueReasons: Record<string, string> = {
  scripted_default:
    "Scripted responses are selected. No paid AI requests are made.",
  ready:
    "Optional AI assistance is ready. Case facts remain authored and clue-gated.",
  missing_paid_consent:
    "Paid AI requests have not been enabled. Scripted responses remain available.",
  missing_api_key:
    "The AI provider has no key configured. Scripted responses remain available.",
  scripted_policy:
    "This question uses the scripted detective to preserve the case’s clue gates.",
  busy: "The detective is already considering a question. Please wait for the room’s reply.",
  case_event: "This part of the story uses the authored case narration.",
  reset:
    "The case has reset. Earlier AI request attempts still count toward this room’s allowance.",
  missing_key:
    "The AI provider has no key configured. Scripted responses remain available.",
  missing_model:
    "The AI provider has no model configured. Scripted responses remain available.",
  paid_opt_in_required:
    "Paid AI requests have not been enabled. Scripted responses remain available.",
  invalid_configuration:
    "The AI configuration needs attention. Scripted responses remain available.",
  timeout:
    "The AI provider took too long. The scripted detective answered instead.",
  provider_error:
    "The AI provider could not answer. The scripted detective answered instead.",
  refused:
    "The AI provider declined this request. The scripted detective answered instead.",
  invalid_plan:
    "The AI response did not match the released evidence. The scripted detective answered instead.",
  budget_exhausted:
    "This room has reached its AI request allowance. Scripted responses remain available.",
  stale:
    "The case changed while the AI considered the question. Only current released facts are used.",
  scripted_guard:
    "This question is handled by the scripted detective to preserve the case’s clue gates.",
};

/** UI copy comes from known statuses, never raw provider diagnostics. */
export function dialogueStatus(meta?: DialogueMeta) {
  return {
    label:
      meta?.source === "model"
        ? "AI-assisted detective"
        : meta?.source === "fallback"
          ? "Scripted fallback"
          : "Scripted detective",
    busy: meta?.busy ?? false,
    aiAvailable: meta?.provider === "openai" && meta.available,
    reason: meta?.reason
      ? Object.hasOwn(dialogueReasons, meta.reason)
        ? dialogueReasons[meta.reason]
        : "The scripted detective remains available while the AI provider is unavailable."
      : "Dialogue uses authored case facts and approved detective remarks.",
    provider: meta?.provider ?? "scripted",
    callsUsed: meta?.calls_used ?? 0,
    callsLimit: meta?.calls_limit ?? 0,
  };
}
