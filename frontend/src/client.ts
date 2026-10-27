export type Evidence = {
  id: string;
  title: string;
  description: string;
  act: number;
};
export type RoomState = {
  room_id: string;
  title: string;
  act: number;
  paused: boolean;
  revision: number;
  guests: { id: string; name: string }[];
  evidence: Evidence[];
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
      return { error: typeof msg.message === "string" && msg.message ? msg.message : "The room rejected that request." };
    if (msg.type === "state") {
      const data = msg.data;
      const record = (value: unknown): value is Record<string, unknown> =>
        typeof value === "object" && value !== null && !Array.isArray(value);
      const strings = (value: unknown, keys: string[]) =>
        record(value) && keys.every((key) => typeof value[key] === "string");
      if (record(data) && strings(data, ["room_id", "title", "dialogue"]) &&
        Number.isInteger(data.act) && Number(data.act) >= 0 && Number(data.act) <= 4 &&
        Number.isInteger(data.revision) && Number(data.revision) >= 0 &&
        typeof data.paused === "boolean" &&
        Array.isArray(data.guests) && data.guests.every((guest) => strings(guest, ["id", "name"])) &&
        Array.isArray(data.suspects) && data.suspects.every((suspect) => strings(suspect, ["id", "name", "description"])) &&
        Array.isArray(data.evidence) && data.evidence.every((clue) => strings(clue, ["id", "title", "description"]) && Number.isInteger(clue.act)) &&
        record(data.votes) && Object.values(data.votes).every((count) => Number.isInteger(count) && Number(count) >= 0) &&
        (data.solution === null || typeof data.solution === "string"))
        return { state: data as RoomState };
      return { error: "An incomplete room update arrived. Reconnect to recover." };
    }
    return {};
  } catch {
    return {
      error: "An unreadable room update arrived. Reconnect to recover.",
    };
  }
}
