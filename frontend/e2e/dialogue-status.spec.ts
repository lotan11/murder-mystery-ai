import { test, expect } from "@playwright/test";

test("default rehearsal clearly remains scripted and works without paid AI", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: /Create an evening/ }).click();
  await expect(page).toHaveURL(/room=/);
  const status = page.getByRole("region", {
    name: "Detective integration status",
  });
  await expect(
    status.getByRole("heading", { name: "Scripted detective" }),
  ).toBeVisible();
  await expect(status).toContainText("No paid AI requests are made.");
  await expect(status).toContainText(
    "Resetting the case does not reset its AI allowance.",
  );
  const health = await (await page.request.get("/health")).json();
  expect(health.ai_enabled).toBe(false);
  expect(JSON.stringify(health)).not.toContain("api_key");
  await page.getByRole("button", { name: "Begin case" }).click();
  await page.getByRole("button", { name: "Reveal next clue" }).click();
  await page
    .getByLabel("Simulated microphone · typed input")
    .fill("Explain the untouched port.");
  await page.getByRole("button", { name: /Send observation/ }).click();
  const room = new URL(page.url()).searchParams.get("room");
  await expect
    .poll(
      async () =>
        (await (await page.request.get(`/api/rooms/${room}/state`)).json())
          .dialogue_meta.reason,
    )
    .toBe("scripted_default");
  const snapshot = await (
    await page.request.get(`/api/rooms/${room}/state`)
  ).json();
  expect(snapshot.dialogue_meta).toMatchObject({
    provider: "scripted",
    source: "scripted",
    calls_used: 0,
    available: false,
    busy: false,
  });
  await expect(
    status.getByRole("heading", { name: "Scripted detective" }),
  ).toBeVisible();
});
