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
      return { error: msg.message || "The room rejected that request." };
    if (msg.type === "state" && msg.data && Array.isArray(msg.data.evidence))
      return { state: msg.data };
    return {};
  } catch {
    return {
      error: "An unreadable room update arrived. Reconnect to recover.",
    };
  }
}
