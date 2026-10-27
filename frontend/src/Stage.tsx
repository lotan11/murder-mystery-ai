import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import "./stage.css";

type Props = {
  evidence: Array<{
    id: string;
    title: string;
    description: string;
    act: number;
  }>;
  dialogue: string;
  act: number;
  paused: boolean;
};

/** Procedural stand-in for a future licensed, rigged character. No audio or visemes. */
export default function Stage({ evidence, dialogue, act, paused }: Props) {
  const mount = useRef<HTMLDivElement>(null);
  const pausedRef = useRef(paused);
  const [fallback, setFallback] = useState(false);
  useEffect(() => {
    pausedRef.current = paused;
  }, [paused]);
  useEffect(() => {
    const host = mount.current;
    if (!host) return;
    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch {
      setFallback(true);
      return;
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    host.appendChild(renderer.domElement);
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 50);
    camera.position.set(0, 1.65, 6.7);
    camera.lookAt(0, 1.6, 0);
    scene.add(new THREE.HemisphereLight(0xb8d8d7, 0x17131a, 2));
    const key = new THREE.DirectionalLight(0xffddb0, 4);
    key.position.set(-3, 5, 4);
    key.castShadow = true;
    scene.add(key);
    const rim = new THREE.DirectionalLight(0x69c1c5, 4);
    rim.position.set(3, 3, -2);
    scene.add(rim);
    const character = new THREE.Group();
    scene.add(character);
    const material = (color: number, roughness = 0.7, metalness = 0) =>
      new THREE.MeshStandardMaterial({ color, roughness, metalness });
    const skin = material(0xc99b79, 0.84),
      dark = material(0x152a2d),
      lapel = material(0x263d3c),
      hair = material(0x44372f),
      brass = material(0xb99a5e, 0.3, 0.65),
      shirt = material(0xddd6bf),
      black = material(0x161b1a);
    function mesh(
      geometry: THREE.BufferGeometry,
      mat: THREE.Material,
      pos: number[],
      scale?: number[],
      parent: THREE.Object3D = character,
    ) {
      const obj = new THREE.Mesh(geometry, mat);
      obj.position.set(pos[0], pos[1], pos[2]);
      if (scale) obj.scale.set(scale[0], scale[1], scale[2]);
      obj.castShadow = true;
      obj.receiveShadow = true;
      parent.add(obj);
      return obj;
    }
    const sphere = () => new THREE.SphereGeometry(1, 40, 32);
    mesh(sphere(), dark, [0, 0.65, 0], [0.88, 1.05, 0.43]);
    mesh(sphere(), shirt, [0, 1.05, 0.36], [0.31, 0.65, 0.08]);
    [-1, 1].forEach((side) => {
      const shoulder = mesh(
        sphere(),
        dark,
        [side * 0.76, 0.68, 0],
        [0.32, 0.74, 0.35],
      );
      shoulder.rotation.z = side * 0.17;
      const panel = mesh(new THREE.BoxGeometry(0.29, 0.94, 0.07), lapel, [
        side * 0.3,
        1.08,
        0.4,
      ]);
      panel.rotation.z = side * -0.29;
      mesh(sphere(), skin, [side * 0.485, 2.2, 0], [0.115, 0.18, 0.13]);
    });
    mesh(new THREE.CylinderGeometry(0.18, 0.22, 0.45, 32), skin, [0, 1.63, 0]);
    const head = new THREE.Group();
    head.position.set(0, 2.19, 0);
    character.add(head);
    mesh(sphere(), skin, [0, 0, 0], [0.46, 0.57, 0.36], head);
    mesh(sphere(), skin, [0, -0.26, 0.16], [0.32, 0.24, 0.27], head);
    mesh(sphere(), skin, [0, -0.015, 0.365], [0.105, 0.17, 0.145], head);
    [-1, 1].forEach((side) => {
      mesh(
        sphere(),
        shirt,
        [side * 0.18, 0.11, 0.321],
        [0.1, 0.065, 0.039],
        head,
      );
      mesh(
        sphere(),
        black,
        [side * 0.175, 0.11, 0.359],
        [0.035, 0.04, 0.015],
        head,
      );
      const brow = mesh(
        sphere(),
        hair,
        [side * 0.18, 0.23, 0.31],
        [0.14, 0.034, 0.048],
        head,
      );
      brow.rotation.z = side * -0.12;
      const moustache = mesh(
        sphere(),
        hair,
        [side * 0.12, -0.17, 0.37],
        [0.165, 0.068, 0.065],
        head,
      );
      moustache.rotation.z = side * 0.2;
      mesh(
        sphere(),
        hair,
        [side * 0.42, 0.16, -0.02],
        [0.065, 0.25, 0.2],
        head,
      );
      const bow = mesh(new THREE.ConeGeometry(0.12, 0.24, 3), black, [
        side * 0.105,
        1.48,
        0.43,
      ]);
      bow.rotation.z = (side * Math.PI) / 2;
    });
    mesh(sphere(), black, [0, 1.48, 0.45], [0.055, 0.055, 0.045]);
    mesh(
      new THREE.CylinderGeometry(0.63, 0.65, 0.075, 64),
      hair,
      [0, 0.48, 0],
      undefined,
      head,
    );
    mesh(
      new THREE.CylinderGeometry(0.39, 0.45, 0.38, 64),
      hair,
      [0, 0.69, 0],
      undefined,
      head,
    );
    mesh(
      new THREE.CylinderGeometry(0.446, 0.449, 0.065, 64),
      black,
      [0, 0.535, 0],
      undefined,
      head,
    );
    mesh(
      new THREE.TorusGeometry(0.115, 0.013, 10, 40),
      brass,
      [0.18, 0.11, 0.38],
      undefined,
      head,
    );
    const chain = mesh(
      new THREE.TorusGeometry(0.17, 0.009, 8, 32, Math.PI),
      brass,
      [0.36, -0.04, 0.29],
      undefined,
      head,
    );
    chain.rotation.z = -Math.PI / 2;
    [1.03, 0.71, 0.39].forEach((y) =>
      mesh(sphere(), brass, [0, y, 0.443], [0.027, 0.027, 0.02]),
    );
    const floor = mesh(
      new THREE.CylinderGeometry(1.22, 1.3, 0.09, 64),
      material(0x1c3133, 0.4, 0.3),
      [0, -0.38, 0],
    );
    floor.receiveShadow = true;
    const resize = () => {
      const width = host.clientWidth,
        height = host.clientHeight;
      renderer.setSize(width, height);
      camera.aspect = width / Math.max(height, 1);
      camera.updateProjectionMatrix();
    };
    const observer = new ResizeObserver(resize);
    observer.observe(host);
    resize();
    const reduce = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;
    let frame = 0,
      elapsed = 0,
      previous = performance.now();
    const draw = (now: number) => {
      const dt = Math.min((now - previous) / 1000, 0.05);
      previous = now;
      if (!pausedRef.current && !reduce) elapsed += dt;
      character.position.y = Math.sin(elapsed * 1.3) * 0.014;
      head.rotation.y = Math.sin(elapsed * 0.45) * 0.055;
      head.rotation.z = Math.sin(elapsed * 0.7) * 0.014;
      renderer.render(scene, camera);
      frame = requestAnimationFrame(draw);
    };
    frame = requestAnimationFrame(draw);
    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      scene.traverse((obj) => {
        if (obj instanceof THREE.Mesh) {
          obj.geometry.dispose();
          const materials = Array.isArray(obj.material)
            ? obj.material
            : [obj.material];
          materials.forEach((mat) => mat.dispose());
        }
      });
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, []);

  const latest = evidence[evidence.length - 1];
  return (
    <section className="cinema-stage" aria-label="Detective and evidence stage">
      <div className="stage-grain" />
      <div className="stage-location">
        <span className="live-dot" /> BLACKWOOD MANOR <span> / </span> THE
        LIBRARY
      </div>
      <div className="manor-backdrop">
        <i />
        <i />
        <i />
        <i />
        <i />
      </div>
      <div
        className="detective-view"
        ref={mount}
        role="img"
        aria-label="Procedural 3D detective wearing a tailored coat, hat and monocle"
      />
      {fallback && (
        <div
          className="detective-fallback"
          aria-label="Detective portrait fallback"
        >
          <div className="fallback-hat" />
          <div className="fallback-face">
            ◉<span>⌁</span>
          </div>
          <div className="fallback-coat" />
        </div>
      )}
      <div className="detective-caption">
        <span>YOUR HOST</span>
        <h2>
          Reginald P.
          <br />
          <em>Wobblebottom</em>
        </h2>
        <p>PROCEDURAL AVATAR · NO LIP SYNC</p>
      </div>
      <aside
        className={`evidence-spotlight ${latest ? "has-evidence" : ""}`}
        aria-label="Latest evidence"
      >
        <div className="dossier-top">
          <span>CASE FILE / 001</span>
          <span>{latest ? `ACT ${latest.act}` : "SEALED"}</span>
        </div>
        <div className="dossier-symbol" aria-hidden="true">
          {latest ? "⌕" : "W"}
        </div>
        <span className="dossier-kicker">
          {latest ? "EVIDENCE ENTERED" : "AWAITING DISCOVERY"}
        </span>
        <h3>{latest?.title || "A rather inconvenient death."}</h3>
        <p>
          {latest?.description ||
            "A manor full of secrets. One impeccably dressed detective. Let the evening unfold."}
        </p>
        <div className="dossier-footer">
          BLACKWOOD CONSTABULARY <span>CONFIDENTIAL</span>
        </div>
      </aside>
      <div className="stage-subtitles" aria-live="polite">
        <span>
          {paused
            ? "INTERMISSION"
            : act === 0
              ? "THE EVENING AWAITS"
              : act >= 4
                ? "THE REVEAL"
                : `ACT ${act} · THE INVESTIGATION`}
        </span>
        <p>“{dialogue}”</p>
      </div>
    </section>
  );
}
