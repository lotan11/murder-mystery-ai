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
  performance?: { emotion: string; gesture: string };
  votes: unknown;
  solution: string | null;
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
