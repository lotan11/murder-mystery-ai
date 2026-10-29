import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import "./character-lab.css";

type Preset = "front" | "profile" | "three-quarter";
type DevelopmentModel = "blockout" | "face-study";
type FacialControl = "jawOpen" | "eyeBlinkLeft" | "eyeBlinkRight";
const facialControls: { name: FacialControl; label: string; max: number }[] = [
  { name: "jawOpen", label: "Jaw opening", max: 0.38 },
  { name: "eyeBlinkLeft", label: "Left blink", max: 1 },
  { name: "eyeBlinkRight", label: "Right blink", max: 1 },
];
const modelFiles: Record<DevelopmentModel, string> = {
  blockout: "scholar-blockout.glb",
  "face-study": "scholar-face-study.glb",
};
const neutralFace = { jawOpen: 0, eyeBlinkLeft: 0, eyeBlinkRight: 0 };
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
    textures = new Set<THREE.Texture>();
  root.traverse((object) => {
    if (!(object instanceof THREE.Mesh)) return;
    geometries.add(object.geometry);
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
}

export default function CharacterLab() {
  const mount = useRef<HTMLDivElement>(null),
    viewer = useRef<HTMLDivElement>(null),
    morphBindings = useRef<Partial<Record<FacialControl, MorphBinding[]>>>({}),
    cameraPreset = useRef<(preset: Preset) => void>(() => {});
  const [model, setModel] = useState<DevelopmentModel>("blockout"),
    [discoveredControls, setDiscoveredControls] = useState<FacialControl[]>([]),
    [faceValues, setFaceValues] = useState<Record<FacialControl, number>>({
      ...neutralFace,
    });
  const [state, setState] = useState<"loading" | "ready" | "failed">("loading"),
    [preset, setPreset] = useState<Preset>("front");
  const [inventory, setInventory] = useState<Inventory | null>(null),
    [error, setError] = useState("");
  useEffect(() => {
    setState("loading");
    setInventory(null);
    setError("");
    setPreset("front");
    setDiscoveredControls([]);
    setFaceValues({ ...neutralFace });
    morphBindings.current = {};
    let disposed = false,
      frame = 0,
      previous = 0,
      cleaned = false;
    const abort = new AbortController();
    let renderer: THREE.WebGLRenderer | null = null,
      controls: OrbitControls | null = null,
      observer: ResizeObserver | null = null;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x233733);
    function cleanup() {
      if (cleaned) return;
      cleaned = true;
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
      morphBindings.current = {};
      if (viewer.current) {
        viewer.current.dataset.morphActive = "0";
        viewer.current.dataset.morphMax = "0";
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
            viewer.current.dataset.morphActive = String(
              influenceGroups.filter((value) => value > 0.001).length,
            );
            viewer.current.dataset.morphMax = Math.max(
              0,
              ...influenceGroups,
            ).toFixed(3);
          }
          renderer?.render(scene, camera);
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
          if (object instanceof THREE.SkinnedMesh) skinnedMeshes += 1;
          if (object instanceof THREE.Bone) joints += 1;
        });
        if (!meshes) {
          releaseModel(gltf.scene);
          throw Error("empty");
        }
        scene.add(gltf.scene);
        gltf.scene.updateMatrixWorld(true);
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
    setFaceValues((current) => ({ ...current, [name]: safe }));
  }
  function resetFace() {
    Object.values(morphBindings.current).forEach((bindings) =>
      bindings.forEach((binding) => {
        binding.influences[binding.index] = 0;
      }),
    );
    setFaceValues({ ...neutralFace });
  }
  function changeModel(next: DevelopmentModel) {
    if (next === model) return;
    resetFace();
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
                event.target.value === "face-study" ? "face-study" : "blockout",
              )
            }
          >
            <option value="blockout">Original Scholar blockout</option>
            <option value="face-study">
              Face study · three-control experiment
            </option>
          </select>
          <p>
            {model === "face-study"
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
                    : "Opening the local Scholar face study…"}
                </div>
              )}
              {state === "failed" && (
                <div className="character-lab-overlay">
                  {model === "blockout"
                    ? "3D blockout unavailable"
                    : "3D face study unavailable"}
                </div>
              )}
              <span className="character-lab-watermark">
                {model === "face-study"
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
            {model === "face-study" && (
              <section
                className="character-lab-face-controls"
                aria-label="Face study controls"
              >
                <h3>Manual facial experiment</h3>
                <p>
                  These controls drive real morph targets found in the selected
                  file. Influence is capped at 0.38. This does not establish a
                  usable speech rig.
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
                    <button onClick={resetFace}>Reset facial controls</button>
                    {discoveredControls.length < 3 && (
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
            No speech-driven mouth animation is connected in this workbench.
            Manual face-study sliders do not connect to a voice. The approved
            portrait + Lewis presentation and the existing animated sample
            remain available in the working game.
          </p>
        </section>
      </main>
    </div>
  );
}
