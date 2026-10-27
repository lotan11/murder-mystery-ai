import { test, expect } from "@playwright/test";

test("organizer, TV and guest complete a synchronized case", async ({
  browser,
}) => {
  const organizerContext = await browser.newContext();
  const guestContext = await browser.newContext({
    viewport: { width: 390, height: 844 },
  });
  const tvContext = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
  });
  const organizer = await organizerContext.newPage();
  const guest = await guestContext.newPage();
  const tv = await tvContext.newPage();
  const errors: string[] = [];
  for (const page of [organizer, guest, tv])
    page.on("pageerror", (error) => errors.push(error.message));
  await organizer.goto("/", { waitUntil: "domcontentloaded" });
  await organizer.getByRole("button", { name: /Create an evening/ }).click();
  await expect(organizer).toHaveURL(/room=/);
  const room = new URL(organizer.url()).searchParams.get("room");
  await tv.goto(`/?view=tv&room=${room}`, { waitUntil: "domcontentloaded" });
  await guest.goto(`/?view=guest&room=${room}`, { waitUntil: "domcontentloaded" });
  await expect(guest.locator("canvas")).toHaveCount(0);
  await guest.getByLabel("Your name", { exact: true }).fill("Inspector Guest");
  await guest.getByRole("button", { name: "Join the investigation" }).click();
  await expect(
    organizer.getByText("Inspector Guest", { exact: true }),
  ).toBeVisible();
  await organizer.getByRole("button", { name: "Begin case" }).click();
  await expect(tv.getByText("ACT 1", { exact: true })).toBeVisible();
  await expect(organizer.getByRole("button", { name: /Next act/ })).toBeDisabled();
  await organizer.getByRole("button", { name: "Reveal next clue" }).click();
  await expect(
    tv.getByRole("heading", { name: "The untouched port", exact: true }),
  ).toBeVisible();
  await tv.screenshot({ path: "test-results/tv-stage.png", fullPage: true });
  await guest.screenshot({
    path: "test-results/guest-notebook.png",
    fullPage: true,
  });
  expect(
    await guest.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await guest
    .getByLabel("Simulated microphone · typed input")
    .fill("What do we know about the tea?");
  await guest.getByRole("button", { name: /Send observation/ }).click();
  await expect
    .poll(async () =>
      (await guest.request.get(`/api/rooms/${room}/state`))
        .json()
        .then((s) => s.dialogue),
    )
    .not.toContain("Do resist");
  await organizer.getByRole("button", { name: "Pause evening" }).click();
  await expect(
    guest.getByRole("button", { name: /Send observation/ }),
  ).toBeDisabled();
  await organizer.getByRole("button", { name: "Resume evening" }).click();
  await organizer.getByRole("button", { name: "Reveal next clue" }).click();
  await expect(
    tv.getByRole("heading", { name: "The stopped clock", exact: true }),
  ).toBeVisible();
  await expect(organizer.getByRole("button", { name: "Reveal next clue" })).toBeDisabled();
  await expect(organizer.getByRole("button", { name: /Next act/ })).toBeEnabled();
  await organizer.getByRole("button", { name: /Next act/ }).click();
  await expect(tv.getByText("ACT 2", { exact: true })).toBeVisible();
  await organizer.getByRole("button", { name: "Reveal next clue" }).click();
  await expect(
    tv.getByRole("heading", { name: "A physician's ledger", exact: true }),
  ).toBeVisible();
  await organizer.getByRole("button", { name: "Reveal next clue" }).click();
  await expect(
    tv.getByRole("heading", { name: "The music-room recording", exact: true }),
  ).toBeVisible();
  await organizer.getByRole("button", { name: /Next act/ }).click();
  await expect(tv.getByText("ACT 3", { exact: true })).toBeVisible();
  await guest.reload({ waitUntil: "domcontentloaded" });
  await expect(guest.getByText(/You are at the table/)).toBeVisible();
  await guest.getByRole("button", { name: "Accuse Dr." }).click();
  await expect
    .poll(async () =>
      (await guest.request.get(`/api/rooms/${room}/state`))
        .json()
        .then((s) => s.votes.margot),
    )
    .toBe(1);
  await organizer.getByRole("button", { name: "Reveal next clue" }).click();
  await expect(
    tv.getByRole("heading", { name: "The dismissal letter", exact: true }),
  ).toBeVisible();
  await organizer.getByRole("button", { name: "Resolve the case" }).click();
  await expect(
    tv.getByRole("heading", { name: "Every toast leaves a trace." }),
  ).toBeVisible();
  await tv.screenshot({ path: "test-results/tv-solution.png", fullPage: true });
  await tv.reload({ waitUntil: "domcontentloaded" });
  await expect(
    tv.getByRole("heading", { name: "Every toast leaves a trace." }),
  ).toBeVisible();
  expect(errors).toEqual([]);
  await organizerContext.close();
  await guestContext.close();
  await tvContext.close();
});
