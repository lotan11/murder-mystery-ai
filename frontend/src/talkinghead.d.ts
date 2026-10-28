declare module "@met4citizen/talkinghead" {
  export type AvatarOptions = {
    url: string;
    body: "M" | "F";
    lipsyncLang: string;
    avatarMood: string;
  };
  export class TalkingHead {
    constructor(node: HTMLElement, options?: Record<string, unknown>);
    audioCtx: AudioContext;
    lipsync: Record<string, unknown>;
    isSpeaking: boolean;
    isAudioPlaying: boolean;
    mtAvatar: Record<string, { applied: number; ms: number[][]; is: number[] }>;
    showAvatar(
      avatar: AvatarOptions,
      progress?: (event: ProgressEvent) => void,
    ): Promise<void>;
    speakAudio(
      audio: {
        audio: AudioBuffer;
        words: string[];
        wtimes: number[];
        wdurations: number[];
      },
      options?: { lipsyncLang: string; isRaw?: boolean },
      onSubtitles?: (word: string) => void,
    ): void;
    stopSpeaking(): void;
    stop(): void;
    dispose(): void;
  }
}
declare module "@met4citizen/talkinghead/modules/lipsync-en.mjs" {
  export class LipsyncEn {}
}
