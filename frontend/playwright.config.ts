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
const auditionTestDirectory = fileURLToPath(new URL("../data/audition-test", import.meta.url));

export default defineConfig({
  testDir: "./e2e",
  timeout: 90000,
  workers: 1,
  expect: { timeout: 10000 },
  use: {
    baseURL: "http://127.0.0.1:8001",
    headless: true,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  reporter: "list",
  webServer: {
    command: `"${python}" scripts/prepare-audition-test.py --output "${auditionTestDirectory}" && "${python}" -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --ws-max-size 16384 --no-access-log --log-level warning`,
    cwd: root,
    url: "http://127.0.0.1:8001/health",
    reuseExistingServer: false,
    timeout: 30000,
    env: {
      MYSTERY_DIALOGUE_PROVIDER: "scripted",
      MYSTERY_ALLOW_PAID_AI: "false",
      OPENAI_API_KEY: "",
      MYSTERY_OPENAI_MODEL: "",
      MYSTERY_AUDITION_DIR: auditionTestDirectory,
      MYSTERY_DB_PATH: fileURLToPath(
        new URL(
          `./.e2e-data/${Date.now()}-${process.pid}.sqlite3`,
          import.meta.url,
        ),
      ),
    },
  },
});
