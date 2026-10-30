export type AudioChunk = { blob: Blob; mimeType: string; durationSeconds: number };

/**
 * Captures standalone, independently decodable WebM/Ogg/MP4 clips. A MediaRecorder
 * timeslice is a sequence of container fragments, so every interval gets its own
 * recorder and a finalized file before the next interval begins.
 */
export async function openListenerCapture(options: {
  isCurrent: () => boolean;
  onChunk: (chunk: AudioChunk) => void;
  onError: (message: string) => void;
  onStatus: (echoCancellation: boolean) => void;
  segmentMilliseconds?: number;
}): Promise<() => void> {
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: {
      echoCancellation: { ideal: true },
      noiseSuppression: { ideal: true },
      autoGainControl: { ideal: true },
    },
  });
  let stopped = false;
  let recorder: MediaRecorder | null = null;
  let timer: ReturnType<typeof setTimeout> | null = null;
  let delivery: Promise<void> = Promise.resolve();
  const stop = () => {
    if (stopped) return;
    stopped = true;
    if (timer) clearTimeout(timer);
    timer = null;
    const active = recorder;
    recorder = null;
    if (active?.state === "recording") active.stop();
    stream.getTracks().forEach((track) => track.stop());
  };
  if (!options.isCurrent()) {
    stop();
    return stop;
  }
  if (typeof MediaRecorder === "undefined") {
    stop();
    throw new Error("This browser does not support microphone recording.");
  }
  const preferred = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/ogg;codecs=opus",
    "audio/mp4",
  ];
  const mimeType = typeof MediaRecorder.isTypeSupported === "function"
    ? preferred.find((candidate) => MediaRecorder.isTypeSupported(candidate)) || ""
    : "";
  options.onStatus(Boolean(stream.getAudioTracks()[0]?.getSettings().echoCancellation));
  const segmentMilliseconds = Math.min(5000, Math.max(1000, options.segmentMilliseconds ?? 3000));

  const recordSegment = () => {
    if (stopped || !options.isCurrent()) {
      stop();
      return;
    }
    try {
      const active = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      recorder = active;
      const segmentStarted = performance.now();
      active.ondataavailable = (event) => {
        if (stopped || !options.isCurrent() || !event.data.size) return;
        const seconds = Math.max(1, Math.ceil((performance.now() - segmentStarted) / 1000));
        const chunk = {
          blob: event.data,
          mimeType: active.mimeType.trim().toLowerCase(),
          durationSeconds: Math.min(5, seconds),
        };
        delivery = delivery.then(async () => {
          if (!stopped && options.isCurrent()) await options.onChunk(chunk);
        }).catch(() => {
          if (!stopped && options.isCurrent()) options.onError("An audio clip could not be prepared for delivery.");
        });
      };
      active.onerror = () => {
        stop();
        options.onError("Microphone capture failed. Check browser permission and retry.");
      };
      active.onstop = () => {
        if (recorder === active) recorder = null;
        if (!stopped && options.isCurrent()) timer = setTimeout(recordSegment, 0);
        else stop();
      };
      active.start();
      timer = setTimeout(() => {
        if (active.state === "recording") active.stop();
      }, segmentMilliseconds);
    } catch {
      stop();
      options.onError("This browser could not create a supported audio clip.");
    }
  };
  recordSegment();
  return stop;
}
