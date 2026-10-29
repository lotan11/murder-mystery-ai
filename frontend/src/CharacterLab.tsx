import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import "./character-lab.css";
import { validateStudy, validateStudyAudio, studyPoseAt } from "./scholar-timing.mjs";

type Preset = "front" | "profile" | "three-quarter";
type DevelopmentModel = "blockout" | "face-study" | "rig-study";
type FacialControl =
  | "jawOpen"
  | "eyeBlinkLeft"
  | "eyeBlinkRight"
  | "browInnerUp"
  | "browOuterUpLeft"
  | "browOuterUpRight"
  | "browDownLeft"
  | "browDownRight"
  | "mouthPucker"
  | "lipPress"
  | "mouthSmile";
const facialControls: { name: FacialControl; label: string; max: number }[] = [
  { name: "jawOpen", label: "Jaw opening", max: 0.38 },
  { name: "eyeBlinkLeft", label: "Left blink", max: 1 },
  { name: "eyeBlinkRight", label: "Right blink", max: 1 },
  { name: "browInnerUp", label: "Inner brow lift", max: 0.35 },
  { name: "browOuterUpLeft", label: "Left brow lift", max: 0.35 },
  { name: "browOuterUpRight", label: "Right brow lift", max: 0.35 },
  { name: "browDownLeft", label: "Left brow lower", max: 0.25 },
  { name: "browDownRight", label: "Right brow lower", max: 0.25 },
  { name: "mouthPucker", label: "Lip rounding", max: 0.25 },
  { name: "lipPress", label: "Lip compression", max: 0.25 },
  { name: "mouthSmile", label: "Subtle smile", max: 0.2 },
];
const modelFiles: Record<DevelopmentModel, string> = {
  blockout: "scholar-blockout.glb",
  "face-study": "scholar-face-study.glb",
  "rig-study": "scholar-rig-study.glb",
};
const neutralFace = Object.fromEntries(
  facialControls.map((control) => [control.name, 0]),
) as Record<FacialControl, number>;
const speechMouthControls: FacialControl[] = ["jawOpen", "mouthPucker", "lipPress", "mouthSmile"];
type SpeechState = "idle" | "loading" | "playing" | "ended" | "error";
type MorphBinding = { influences: number[]; index: number };
type Inventory = {
  meshes: number;
  joints: number;
  skinnedMeshes: number;
  morphs: string[];
  meshNames: string[];
  bytes: number;
};
function releaseModel(root: THREE.Object3D) {
  const geometries = new Set<THREE.BufferGeometry>(),
    materials = new Set<THREE.Material>(),
    textures = new Set<THREE.Texture>(),
    skeletons = new Set<THREE.Skeleton>();
  root.traverse((object) => {
    if (!(object instanceof THREE.Mesh)) return;
    geometries.add(object.geometry);
    if (object instanceof THREE.SkinnedMesh) skeletons.add(object.skeleton);
    for (const material of Array.isArray(object.material)
      ? object.material
      : [object.material]) {
      materials.add(material);
      for (const value of Object.values(material))
        if (value instanceof THREE.Texture) textures.add(value);
    }
  });
  geometries.forEach((geometry) => geometry.dispose());
  materials.forEach((material) => material.dispose());
  textures.forEach((texture) => texture.dispose());
  skeletons.forEach((skeleton) => skeleton.dispose());
}

export default function CharacterLab() {
  const mount = useRef<HTMLDivElement>(null),
    viewer = useRef<HTMLDivElement>(null),
    morphBindings = useRef<Partial<Record<FacialControl, MorphBinding[]>>>({}),
    headBinding = useRef<{ bone: THREE.Bone; rest: THREE.Quaternion } | null>(null),
    headVertex = useRef<{ mesh: THREE.SkinnedMesh; rest: THREE.Vector3 } | null>(null),
    cameraPreset = useRef<(preset: Preset) => void>(() => {}),
    requestRender = useRef<() => void>(() => {});
  const speechAudio = useRef<HTMLAudioElement | null>(null),
    speechAbort = useRef<AbortController | null>(null),
    speechFrame = useRef(0), speechSession = useRef(0),
    speechURL = useRef<string | null>(null);
  const [speechState, setSpeechState] = useState<SpeechState>("idle"),
    [speechMessage, setSpeechMessage] = useState("");
  const [model, setModel] = useState<DevelopmentModel>("blockout"),
    [discoveredControls, setDiscoveredControls] = useState<FacialControl[]>([]),
    [hasHead, setHasHead] = useState(false),
    [headTurn, setHeadTurn] = useState(0),
    [faceValues, setFaceValues] = useState<Record<FacialControl, number>>({
      ...neutralFace,
    });
  const [state, setState] = useState<"loading" | "ready" | "failed">("loading"),
    [preset, setPreset] = useState<Preset>("front");
  const [inventory, setInventory] = useState<Inventory | null>(null),
    [error, setError] = useState("");
  function setSpeechMouth(values: Partial<Record<FacialControl, number>>) {
    let changed = false;
    for (const name of speechMouthControls) {
      const value = Math.max(0, Math.min(facialControls.find(c => c.name === name)?.max || 0, values[name] || 0));
      for (const binding of morphBindings.current[name] || []) {
        if (Math.abs(binding.influences[binding.index] - value) > .0001) changed = true;
        binding.influences[binding.index] = value;
      }
    }
    if (changed) requestRender.current();
  }
  function stopSpeech(next: SpeechState = "idle", message = "") {
    speechSession.current += 1;
    speechAbort.current?.abort(); speechAbort.current = null;
    cancelAnimationFrame(speechFrame.current); speechFrame.current = 0;
    const audio = speechAudio.current; speechAudio.current = null;
    if (audio) { audio.onended = null; audio.onerror = null; audio.pause(); audio.removeAttribute("src"); audio.load(); audio.remove(); }
    if (speechURL.current) URL.revokeObjectURL(speechURL.current);
    speechURL.current = null;
    setSpeechMouth({});
    setFaceValues(current => ({...current, jawOpen:0, mouthPucker:0, lipPress:0, mouthSmile:0}));
    if (viewer.current) {
      viewer.current.dataset.speechTime = "0";
      viewer.current.dataset.speechPhoneme = "";
      viewer.current.dataset.speechState = next;
    }
    setSpeechState(next); setSpeechMessage(message);
  }
  async function playSpeech() {
    if (model !== "rig-study" || state !== "ready" || document.hidden) return;
    stopSpeech("loading");
    const session = speechSession.current, abort = new AbortController();
    speechAbort.current = abort;
    async function boundedResponse(path: string, maximum: number) {
      const response = await fetch(path, {signal: abort.signal, cache: "no-store"});
      if (!response.ok || Number(response.headers.get("content-length") || 0) > maximum) throw Error("The fixed local study is unavailable.");
      const reader = response.body?.getReader();
      if (!reader) throw Error("The fixed local study could not be read.");
      const chunks: Uint8Array[] = []; let size = 0;
      while (true) {
        const {value, done} = await reader.read(); if (done) break;
        size += value.byteLength;
        if (size > maximum) { await reader.cancel(); throw Error("The fixed local study exceeds its size limit."); }
        chunks.push(value);
      }
      const bytes = new Uint8Array(size); let offset = 0;
      for (const chunk of chunks) {bytes.set(chunk, offset); offset += chunk.byteLength;}
      return bytes;
    }
    try {
      const metadata = await boundedResponse("/character-lab/lewis-study.json", 512*1024);
      const study = validateStudy(JSON.parse(new TextDecoder().decode(metadata)));
      const bytes = await boundedResponse("/character-lab/lewis-study.wav", 8*1024*1024);
      validateStudyAudio(bytes, study.duration_seconds);
      if (!globalThis.crypto?.subtle) throw Error("This browser cannot verify the fixed recording. Open the lab on localhost or a secure connection.");
      const digest = await crypto.subtle.digest("SHA-256", bytes);
      const hash = [...new Uint8Array(digest)].map(v => v.toString(16).padStart(2,"0")).join("");
      if (hash !== study.audio_sha256) throw Error("The fixed audio does not match its phoneme timing.");
      if (session !== speechSession.current || abort.signal.aborted || document.hidden) return;
      const url = URL.createObjectURL(new Blob([bytes], {type:"audio/wav"}));
      speechURL.current = url;
      const audio = new Audio(url); speechAudio.current = audio;
      audio.hidden = true; audio.dataset.labSpeech = "true";
      audio.playbackRate = 1.05; audio.preservesPitch = true;
      viewer.current?.appendChild(audio);
      audio.onended = () => {if (session === speechSession.current) stopSpeech("ended", "The fixed Lewis study finished.");};
      audio.onerror = () => {if (session === speechSession.current) stopSpeech("error", "The fixed local study audio could not be played. Manual controls remain available.");};
      await audio.play();
      if (session !== speechSession.current || abort.signal.aborted) return;
      setSpeechState("playing");
      if (viewer.current) viewer.current.dataset.speechState = "playing";
      const animate = () => {
        if (session !== speechSession.current || speechAudio.current !== audio || audio.paused || audio.ended) return;
        const pose = studyPoseAt(study.phonemes, audio.currentTime);
        setSpeechMouth(pose);
        if (viewer.current) {
          viewer.current.dataset.speechTime = audio.currentTime.toFixed(3);
          viewer.current.dataset.speechPhoneme = pose.phoneme;
        }
        speechFrame.current = requestAnimationFrame(animate);
      };
      speechFrame.current = requestAnimationFrame(animate);
    } catch (error) {
      if (session !== speechSession.current || abort.signal.aborted) return;
      stopSpeech("error", error instanceof Error ? error.message : "The fixed local study is unavailable.");
    }
  }
  useEffect(() => {
    const hidden = () => {if (document.hidden && (speechAudio.current || speechAbort.current)) stopSpeech();};
    document.addEventListener("visibilitychange", hidden);
    return () => {document.removeEventListener("visibilitychange", hidden); stopSpeech();};
  }, []);
  useEffect(() => {
    setState("loading");
    setInventory(null);
    setError("");
    setPreset("front");
    setDiscoveredControls([]);
    setFaceValues({ ...neutralFace });
    morphBindings.current = {};
    headBinding.current = null;
    headVertex.current = null;
    setHasHead(false);
    setHeadTurn(0);
    let disposed = false,
      frame = 0,
      previous = 0,
      cleaned = false,
      dirty = true,
      renderCount = 0;
    requestRender.current = () => { dirty = true; };
    const abort = new AbortController();
    let renderer: THREE.WebGLRenderer | null = null,
      controls: OrbitControls | null = null,
      observer: ResizeObserver | null = null;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x233733);
    function cleanup() {
      if (cleaned) return;
      cleaned = true;
      stopSpeech();
      cancelAnimationFrame(frame);
      observer?.disconnect();
      controls?.dispose();
      releaseModel(scene);
      if (renderer) {
        renderer.domElement.removeEventListener(
          "webglcontextlost",
          contextLost,
        );
        renderer.dispose();
        renderer.forceContextLoss();
        renderer.domElement.remove();
      }
      cameraPreset.current = () => {};
      requestRender.current = () => {};
      morphBindings.current = {};
      headBinding.current = null;
      headVertex.current = null;
      if (viewer.current) {
        viewer.current.dataset.morphActive = "0";
        viewer.current.dataset.morphMax = "0";
        viewer.current.dataset.headTurn = "0";
        viewer.current.dataset.headDisplacement = "0";
        viewer.current.dataset.renderCount = "0";
      }
    }
    function contextLost(event: Event) {
      event.preventDefault();
      if (disposed) return;
      cleanup();
      setState("failed");
      setError(
        "The 3D view lost its graphics context. The portrait reference and measured inventory remain available; reload to reopen the model.",
      );
    }
    queueMicrotask(async () => {
      if (disposed || !mount.current) return;
      try {
        const host = mount.current;
        renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1;
        renderer.domElement.setAttribute("aria-hidden", "true");
        renderer.domElement.addEventListener("webglcontextlost", contextLost);
        host.appendChild(renderer.domElement);
        const camera = new THREE.PerspectiveCamera(30, 1, 0.01, 1000);
        camera.position.set(0, 1.3, 4);
        controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.12;
        controls.addEventListener("change", () => { dirty = true; });
        controls.target.set(0, 1.3, 0);
        scene.add(new THREE.HemisphereLight(0xffffff, 0x969d98, 2.2));
        const key = new THREE.DirectionalLight(0xffffff, 3);
        key.position.set(-3, 5, 4);
        scene.add(key);
        const fill = new THREE.DirectionalLight(0xe2e9ed, 1.5);
        fill.position.set(4, 2, 3);
        scene.add(fill);
        const resize = () => {
          if (!renderer) return;
          const width = Math.max(host.clientWidth, 1),
            height = Math.max(host.clientHeight, 1);
          renderer.setSize(width, height);
          camera.aspect = width / height;
          camera.updateProjectionMatrix();
          dirty = true;
        };
        observer = new ResizeObserver(resize);
        observer.observe(host);
        resize();
        const draw = (now: number) => {
          if (disposed || cleaned) return;
          frame = requestAnimationFrame(draw);
          if (now - previous < 1000 / 30) return;
          previous = now;
          controls?.update();
          // Speech study invalidates changed poses; idle models skip GPU work. Keep damping responsive,
          // but avoid reskinning and redrawing unchanged geometry while idle.
          if (!dirty) return;
          dirty = false;
          const influenceGroups = Object.values(morphBindings.current).map(
            (bindings) =>
              Math.max(
                0,
                ...bindings.map((binding) =>
                  Math.abs(binding.influences[binding.index] || 0),
                ),
              ),
          );
          if (viewer.current) {
            scene.updateMatrixWorld(true);
            const sample = headVertex.current;
            let displacement = 0;
            if (sample) {
              sample.mesh.skeleton.update();
              const posed = sample.mesh.getVertexPosition(0, new THREE.Vector3());
              posed.applyMatrix4(sample.mesh.matrixWorld);
              displacement = posed.distanceTo(sample.rest);
            }
            viewer.current.dataset.headDisplacement = displacement.toFixed(6);
            const head = headBinding.current;
            const rotation = head
              ? head.rest.clone().invert().multiply(head.bone.quaternion)
              : new THREE.Quaternion();
            viewer.current.dataset.headTurn = THREE.MathUtils.radToDeg(
              2 * Math.atan2(rotation.y, rotation.w),
            ).toFixed(3);
            viewer.current.dataset.morphActive = String(
              influenceGroups.filter((value) => value > 0.001).length,
            );
            viewer.current.dataset.morphMax = Math.max(
              0,
              ...influenceGroups,
            ).toFixed(3);
          }
          if (renderer) {
            renderer.render(scene, camera);
            renderCount += 1;
            if (viewer.current) viewer.current.dataset.renderCount = String(renderCount);
          }
        };
        frame = requestAnimationFrame(draw);
        const response = await fetch(`/character-lab/${modelFiles[model]}`, {
          signal: abort.signal,
        });
        if (!response.ok) throw Error("missing");
        const bytes = await response.arrayBuffer();
        if (
          bytes.byteLength < 20 ||
          new DataView(bytes).getUint32(0, true) !== 0x46546c67
        )
          throw Error("missing");
        const gltf = await new GLTFLoader().parseAsync(
          bytes,
          "/character-lab/",
        );
        if (disposed || cleaned) {
          releaseModel(gltf.scene);
          return;
        }
        let meshes = 0,
          joints = 0,
          skinnedMeshes = 0;
        const morphs = new Set<string>(),
          meshNames: string[] = [];
        gltf.scene.traverse((object) => {
          if (object instanceof THREE.Mesh) {
            meshes += 1;
            meshNames.push(object.name || `Mesh ${meshes}`);
            Object.keys(object.morphTargetDictionary || {}).forEach((name) =>
              morphs.add(name),
            );
            if (object.morphTargetDictionary && object.morphTargetInfluences) {
              for (const control of facialControls) {
                const index = object.morphTargetDictionary[control.name];
                if (
                  Number.isInteger(index) &&
                  index >= 0 &&
                  index < object.morphTargetInfluences.length
                ) {
                  const binding = {
                    influences: object.morphTargetInfluences,
                    index,
                  };
                  (morphBindings.current[control.name] ||= []).push(binding);
                  binding.influences[index] = 0;
                }
              }
            }
          }
          if (object instanceof THREE.SkinnedMesh) {
            skinnedMeshes += 1;
            if (object.name.toLowerCase().includes("spectacle") &&
                object.geometry.getAttribute("position")?.count) {
              headVertex.current = { mesh: object, rest: new THREE.Vector3() };
            }
          }
          if (object instanceof THREE.Bone) {
            joints += 1;
            if (object.name.replace(/^mixamorig:?/, "") === "Head") {
              headBinding.current = {
                bone: object,
                rest: object.quaternion.clone(),
              };
            }
          }
        });
        if (!meshes) {
          releaseModel(gltf.scene);
          throw Error("empty");
        }
        scene.add(gltf.scene);
        gltf.scene.updateMatrixWorld(true);
        if (headVertex.current) {
          const sample = headVertex.current;
          sample.mesh.skeleton.update();
          sample.mesh.getVertexPosition(0, sample.rest);
          sample.rest.applyMatrix4(sample.mesh.matrixWorld);
        }
        const bounds = new THREE.Box3().setFromObject(gltf.scene),
          size = bounds.getSize(new THREE.Vector3()),
          center = bounds.getCenter(new THREE.Vector3());
        const height = Math.max(size.y, 0.1);
        const fullBody = height > Math.max(size.x, size.z) * 1.8;
        const target = new THREE.Vector3(
          center.x,
          fullBody ? bounds.min.y + height * 0.76 : center.y,
          center.z,
        );
        // Bust exports need the whole head and shoulder silhouette, not full-body head framing.
        const distance = fullBody
          ? height * 1.17
          : Math.max(
              height / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2))),
              size.x /
                (2 *
                  Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) *
                  camera.aspect),
            ) * 1.12;
        camera.near = Math.max(height / 1000, 0.001);
        camera.far = height * 100;
        camera.updateProjectionMatrix();
        controls.minDistance = height * 0.38;
        controls.maxDistance = height * 4;
        cameraPreset.current = (view) => {
          if (!controls) return;
          const direction =
            view === "profile"
              ? new THREE.Vector3(1, 0, 0)
              : view === "three-quarter"
                ? new THREE.Vector3(0.68, 0, 0.74)
                : new THREE.Vector3(0, 0, 1);
          camera.position.copy(target).addScaledVector(direction, distance);
          controls.target.copy(target);
          controls.update();
          dirty = true;
        };
        cameraPreset.current("front");
        setInventory({
          meshes,
          joints,
          skinnedMeshes,
          morphs: [...morphs].sort(),
          meshNames,
          bytes: bytes.byteLength,
        });
        setDiscoveredControls(
          facialControls
            .filter((control) => !!morphBindings.current[control.name]?.length)
            .map((control) => control.name),
        );
        setHasHead(headBinding.current !== null);
        requestRender.current();
        setState("ready");
      } catch {
        if (disposed || cleaned) return;
        cleanup();
        setState("failed");
        setError(
          "The selected local Scholar model could not be opened. It may still be preparing, or this browser may not support the 3D view. No other avatar has been substituted.",
        );
      }
    });
    return () => {
      disposed = true;
      abort.abort();
      cleanup();
    };
  }, [model]);
  function applyFace(name: FacialControl, value: number) {
    const safe = Math.max(
      0,
      Math.min(
        facialControls.find((control) => control.name === name)?.max || 0,
        Number.isFinite(value) ? value : 0,
      ),
    );
    const bindings = morphBindings.current[name];
    if (!bindings?.length) return;
    bindings.forEach((binding) => {
      binding.influences[binding.index] = safe;
    });
    requestRender.current();
    setFaceValues((current) => ({ ...current, [name]: safe }));
  }
  function applyHead(value: number) {
    const binding = headBinding.current;
    if (!binding) return;
    const safe = Math.max(-10, Math.min(10, Number.isFinite(value) ? value : 0));
    binding.bone.quaternion.copy(binding.rest).multiply(
      new THREE.Quaternion().setFromAxisAngle(
        new THREE.Vector3(0, 1, 0),
        THREE.MathUtils.degToRad(safe),
      ),
    );
    binding.bone.updateMatrixWorld(true);
    requestRender.current();
    setHeadTurn(safe);
  }
  function resetFace() {
    Object.values(morphBindings.current).forEach((bindings) =>
      bindings.forEach((binding) => {
        binding.influences[binding.index] = 0;
      }),
    );
    requestRender.current();
    setFaceValues({ ...neutralFace });
  }
  function changeModel(next: DevelopmentModel) {
    if (next === model) return;
    stopSpeech();
    resetFace();
    applyHead(0);
    setHasHead(false);
    setState("loading");
    setInventory(null);
    setDiscoveredControls([]);
    setError("");
    setPreset("front");
    setModel(next);
  }
  function view(next: Preset) {
    setPreset(next);
    cameraPreset.current(next);
  }
  return (
    <div className="character-lab-page">
      <header className="character-lab-header">
        <a className="brand" href="/">
          <span className="seal">W</span>
          <span>
            WOBBLEBOTTOM<span className="brand-sub">CHARACTER DEVELOPMENT</span>
          </span>
        </a>
        <a href="/">Return to the working game ↗</a>
      </header>
      <main className="character-lab-main">
        <div className="eyebrow">
          A SEPARATE WORKBENCH · THE LIVE GAME IS UNCHANGED
        </div>
        <h1>Shape the Scholar.</h1>
        <p className="character-lab-intro">
          An approved portrait is the visual reference. The actual local 3D
          blockout beside it is a work in progress, with likeness, clothing, and
          animation rig still in development.
        </p>
        <div className="character-lab-model-choice">
          <label htmlFor="development-model">Development model</label>
          <select
            id="development-model"
            value={model}
            onChange={(event) =>
              changeModel(
                event.target.value === "rig-study"
                  ? "rig-study"
                  : event.target.value === "face-study"
                    ? "face-study"
                    : "blockout",
              )
            }
          >
            <option value="blockout">Original Scholar blockout</option>
            <option value="face-study">
              Face study · three-control experiment
            </option>
            <option value="rig-study">Rig study · experimental binding</option>
          </select>
          <p>
            {model === "rig-study"
              ? "An experimental weighted bust with manual head and face controls. Likeness, materials and full visemes remain unfinished. A fixed local Lewis timing study is available below; live game speech is not connected."
              : model === "face-study"
              ? "A static face experiment with three manually controlled morphs. No skeleton or speech-driven lip sync is connected."
              : "The original unapproved blockout remains available for comparison."}
          </p>
        </div>
        <div className="character-lab-comparison">
          <section className="character-lab-reference">
            <div className="character-lab-panel-title">
              <h2>Approved concept</h2>
              <span>PORTRAIT REFERENCE</span>
            </div>
            <img
              src="/casting/vale.png"
              alt="Approved Scholar portrait reference: an older British detective with round spectacles and a tweed waistcoat"
            />
            <p>
              The selected look for Reginald P. Wobblebottom. This image is not
              a 3D model or an animation demonstration.
            </p>
          </section>
          <section className="character-lab-model">
            <div className="character-lab-panel-title">
              <h2>3D development</h2>
              <span>WORK IN PROGRESS</span>
            </div>
            <div
              className="character-lab-viewer"
              ref={viewer}
              role="img"
              aria-label="Scholar 3D workbench"
              data-model-state={state}
              data-development-model={model}
              data-speech-state={speechState}
              data-speech-time="0"
              data-speech-phoneme=""
              data-render-count="0"
              data-head-turn="0"
              data-head-displacement="0"
              data-morph-active="0"
              data-morph-max="0"
              data-mesh-count={inventory?.meshes || 0}
              data-joint-count={inventory?.joints || 0}
              data-morph-count={inventory?.morphs.length || 0}
            >
              <div ref={mount} className="character-lab-canvas" />
              {state === "loading" && (
                <div className="character-lab-overlay" role="status">
                  {model === "blockout"
                    ? "Opening the local Scholar blockout…"
                    : model === "rig-study"
                      ? "Opening the local Scholar rig study…"
                      : "Opening the local Scholar face study…"}
                </div>
              )}
              {state === "failed" && (
                <div className="character-lab-overlay">
                  {model === "blockout"
                    ? "3D blockout unavailable"
                    : model === "rig-study"
                      ? "3D rig study unavailable"
                      : "3D face study unavailable"}
                </div>
              )}
              <span className="character-lab-watermark">
                {model === "rig-study"
                  ? "RIG STUDY · EXPERIMENTAL BINDING"
                  : model === "face-study"
                  ? "FACE STUDY · THREE-CONTROL EXPERIMENT"
                  : "BLOCKOUT · NOT ACTIVE IN THE GAME"}
              </span>
            </div>
            <div
              className="character-lab-controls"
              aria-label="Model view controls"
            >
              <button
                disabled={state !== "ready"}
                aria-pressed={preset === "front"}
                onClick={() => view("front")}
              >
                Front
              </button>
              <button
                disabled={state !== "ready"}
                aria-pressed={preset === "profile"}
                onClick={() => view("profile")}
              >
                Profile
              </button>
              <button
                disabled={state !== "ready"}
                aria-pressed={preset === "three-quarter"}
                onClick={() => view("three-quarter")}
              >
                Three-quarter
              </button>
              <button
                disabled={state !== "ready"}
                onClick={() => view("front")}
              >
                Reset camera
              </button>
            </div>
            {model !== "blockout" && (
              <section
                className="character-lab-face-controls"
                aria-label="Face study controls"
              >
                <h3>Manual facial experiment</h3>
                <p>
                  These controls drive real morph targets found in the selected
                  file. Jaw opening is capped at 0.38; blinks can close fully.
                  {model === "rig-study" &&
                    " Brow lifts are limited to 0.35 and lowering to 0.25. Manual lip rounding and compression are limited to 0.25; smile to 0.20. Full visemes and mouth interior remain unfinished."}
                  {" "}This does not establish a usable speech rig.
                </p>
                {state === "ready" && discoveredControls.length > 0 ? (
                  <>
                    {facialControls
                      .filter((control) =>
                        discoveredControls.includes(control.name),
                      )
                      .map((control) => (
                        <div
                          className="character-lab-face-slider"
                          key={control.name}
                        >
                          <label htmlFor={`face-${control.name}`}>
                            {control.label}
                            <output htmlFor={`face-${control.name}`}>
                              {faceValues[control.name].toFixed(2)}
                            </output>
                          </label>
                          <input
                            id={`face-${control.name}`}
                            type="range"
                            disabled={(speechState === "playing" || speechState === "loading") && speechMouthControls.includes(control.name)}
                            min="0"
                            max={control.max}
                            step="0.01"
                            value={faceValues[control.name]}
                            onChange={(event) =>
                              applyFace(
                                control.name,
                                Number(event.target.value),
                              )
                            }
                          />
                        </div>
                      ))}
                    <button disabled={speechState === "playing" || speechState === "loading"} onClick={resetFace}>Reset facial controls</button>
                    {discoveredControls.length < (model === "rig-study" ? 11 : 3) && (
                      <p>
                        Only the controls actually present in this file are
                        shown.
                      </p>
                    )}
                  </>
                ) : (
                  <p>
                    {state === "loading"
                      ? "Discovering the model’s actual morph targets…"
                      : "No supported facial controls are available in the loaded model."}
                  </p>
                )}
              </section>
            )}
            {model === "rig-study" && (
              <section className="character-lab-face-controls character-lab-speech" aria-label="Fixed Lewis timing study">
                <h3>Fixed Lewis timing study</h3>
                <p>A short local Lewis recording at the approved +5% pace drives a simplified mouth-shape approximation from model-predicted phoneme timings. This is not finished natural lip-sync or a full viseme set. Mouth interior and final likeness remain unfinished.</p>
                <p className="character-lab-study-line">“Good evening. I am Detective Wobblebottom. Let us examine the evidence.”</p>
                <div className="character-lab-study-buttons">
                  <button disabled={state !== "ready" || speechState === "loading" || speechState === "playing" || !speechMouthControls.every(name => discoveredControls.includes(name))} onClick={() => void playSpeech()}>Play Lewis timing study</button>
                  <button disabled={speechState !== "loading" && speechState !== "playing"} onClick={() => stopSpeech()}>Stop timing study</button>
                </div>
                <p role="status">{speechMessage || (speechState === "playing" ? "Playing the fixed local study. Stop returns the mouth to neutral." : speechState === "loading" ? "Checking the fixed recording and its timing…" : "Silent until you choose Play. This study does not use room dialogue or a microphone.")}</p>
              </section>
            )}
            {model === "rig-study" && state === "ready" && hasHead && (
              <section
                className="character-lab-face-controls"
                aria-label="Rig study controls"
              >
                <h3>Manual head experiment</h3>
                <p>
                  Turns the actual head bone up to ten degrees from its loaded
                  rest pose. This is a binding study, with unfinished likeness,
                  materials and speech controls.
                </p>
                <div className="character-lab-face-slider">
                  <label htmlFor="rig-head-turn">
                    Head turn
                    <output htmlFor="rig-head-turn">{headTurn.toFixed(1)}°</output>
                  </label>
                  <input
                    id="rig-head-turn"
                    type="range"
                    min="-10"
                    max="10"
                    step="0.5"
                    value={headTurn}
                    onChange={(event) => applyHead(Number(event.target.value))}
                  />
                </div>
                <button onClick={() => applyHead(0)}>Reset head pose</button>
              </section>
            )}
            <p className="character-lab-note">
              Drag to orbit. Scroll to zoom. Neutral studio lighting; the head
              and upper body are framed for inspection.
            </p>
          </section>
        </div>
        <section
          className="character-lab-inventory panel"
          aria-label="Loaded model inventory"
        >
          <div className="eyebrow">MEASURED FROM THE LOADED GLB</div>
          <h2>Geometry and rig inventory</h2>
          <div className="character-lab-counts">
            <div>
              <strong>{inventory?.meshes ?? "—"}</strong>
              <span>Meshes</span>
            </div>
            <div>
              <strong>{inventory?.joints ?? "—"}</strong>
              <span>Bone joints</span>
            </div>
            <div>
              <strong>{inventory?.skinnedMeshes ?? "—"}</strong>
              <span>Skinned meshes</span>
            </div>
            <div>
              <strong>{inventory?.morphs.length ?? "—"}</strong>
              <span>Named morphs</span>
            </div>
            <div>
              <strong>
                {inventory
                  ? `${(inventory.bytes / 1024 / 1024).toFixed(1)} MB`
                  : "—"}
              </strong>
              <span>Local asset</span>
            </div>
          </div>
          <p role="status">
            {state === "loading"
              ? "Loading the local asset; inventory has not been measured yet."
              : state === "ready"
                ? "The actual local model is loaded. Counts describe its contents, not an approved likeness or a production-ready animation rig."
                : error}
          </p>
          {inventory && (
            <details>
              <summary>Inspect mesh and morph names</summary>
              <p>
                <strong>Meshes:</strong> {inventory.meshNames.join(", ")}
              </p>
              <p>
                <strong>Morphs:</strong>{" "}
                {inventory.morphs.length
                  ? inventory.morphs.join(", ")
                  : "No named morph targets were found."}
              </p>
            </details>
          )}
          <p className="character-lab-note">
            Only the weighted rig offers a fixed local speech-timing experiment.
            Manual face-study sliders remain separate from voice. The approved
            portrait + Lewis presentation and the existing animated sample
            remain available in the working game.
          </p>
        </section>
      </main>
    </div>
  );
}
