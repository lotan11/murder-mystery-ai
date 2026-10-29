import React, { Suspense, lazy } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./style.css";
const VoiceAudition = lazy(() => import("./VoiceAudition"));
const Casting = lazy(() => import("./Casting"));
const CharacterLab = lazy(() => import("./CharacterLab"));
const audition =
  new URLSearchParams(location.search).get("view") === "audition";
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {new URLSearchParams(location.search).get("view") === "character-lab" ? (
      <Suspense
        fallback={<p role="status">Preparing the character workbench…</p>}
      >
        <CharacterLab />
      </Suspense>
    ) : new URLSearchParams(location.search).get("view") === "casting" ? (
      <Suspense fallback={<p role="status">Preparing the casting studio…</p>}>
        <Casting />
      </Suspense>
    ) : audition ? (
      <Suspense
        fallback={
          <p className="audition-loading" role="status">
            Preparing the voice audition…
          </p>
        }
      >
        <VoiceAudition />
      </Suspense>
    ) : (
      <App />
    )}
  </React.StrictMode>,
);
