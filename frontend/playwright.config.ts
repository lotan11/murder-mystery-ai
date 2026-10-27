import { defineConfig } from "@playwright/test";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const localPython = fileURLToPath(
  new URL(
    process.platform === "win32"
      ? "../.venv/Scripts/python.exe"
      : "../.venv/bin/python",
    import.meta.url,
  ),
);
const python = existsSync(localPython) ? localPython : "python";

export default defineConfig({
  testDir: "./e2e",
  timeout: 45000,
  use: { baseURL: "http://127.0.0.1:8001", headless: true },
  reporter: "list",
  webServer: {
    command: `"${python}" -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --ws-max-size 16384 --no-access-log --log-level warning`,
    cwd: root,
    url: "http://127.0.0.1:8001/health",
    reuseExistingServer: false,
    timeout: 30000,
  },
});
