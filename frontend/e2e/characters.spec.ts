import { test, expect, type Page } from "@playwright/test";

type Packet = { type: string; data?: any };
function observe(page: Page): Packet[] {
  const packets: Packet[] = [];
  page.on("websocket", (socket) =>
    socket.on("framereceived", (frame) => {
      try {
        packets.push(JSON.parse(String(frame.payload)));
      } catch {
        /* Ignore non-JSON frames. */
      }
    }),
  );
  return packets;
}
function latestPrivate(packets: Packet[]) {
  return packets.filter((packet) => packet.type === "private").at(-1)?.data;
}

test("four dinner guests receive isolated roles, introduce themselves and explain accusations", async ({
  browser,
}) => {
  const contexts = await Promise.all(
    Array.from({ length: 6 }, (_, index) =>
      browser.newContext({
        viewport:
          index < 2
            ? { width: 1600, height: 1000 }
            : { width: 390, height: 844 },
      }),
    ),
  );
  try {
    const pages = await Promise.all(
      contexts.map((context) => context.newPage()),
    );
    const [host, tv, ...guests] = pages;
    const packets = pages.map(observe);
    const errors: string[] = [];
    pages.forEach((page) =>
      page.on("pageerror", (error) => errors.push(error.message)),
    );
    await host.goto("/", { waitUntil: "domcontentloaded" });
    await host.getByRole("button", { name: /Create an evening/ }).click();
    await expect(host).toHaveURL(/room=/);
    const room = new URL(host.url()).searchParams.get("room");
    const state = async () =>
      (await host.request.get(`/api/rooms/${room}/state`)).json();
    await tv.goto(`/?view=tv&room=${room}`, { waitUntil: "domcontentloaded" });
    const names = [
      "Dinner Ada",
      "Dinner Felix",
      "Dinner Vale",
      "Dinner Sleuth",
    ];
    const roles = ["ada", "felix", "margot", "investigator"];
    for (const [index, guest] of guests.entries()) {
      await guest.goto(`/?view=guest&room=${room}`, {
        waitUntil: "domcontentloaded",
      });
      await guest.getByLabel("Your name", { exact: true }).fill(names[index]);
      await guest
        .getByRole("button", { name: "Join the investigation" })
        .click();
      await expect
        .poll(() => latestPrivate(packets[index + 2])?.character.id)
        .toBe(roles[index]);
      await expect(
        guest.getByRole("region", { name: "Your private character" }),
      ).toBeVisible();
      await expect(
        guest.getByRole("button", { name: "Reveal private brief" }),
      ).toBeVisible();
      await expect(guest.locator("canvas")).toHaveCount(0);
      expect(
        await guest.evaluate(
          () => document.documentElement.scrollWidth <= window.innerWidth,
        ),
      ).toBe(true);
    }
    await guests[3].screenshot({
      path: "test-results/character-notebook.png",
      fullPage: true,
    });
    const publicState = JSON.stringify(await state());
    for (const [index] of guests.entries()) {
      const own = latestPrivate(packets[index + 2]);
      expect(publicState).not.toContain(own.character.private_brief);
      expect(publicState).not.toContain("private_brief");
      for (const packet of packets[index + 2].filter(
        (packet) => packet.type === "private",
      )) {
        expect(packet.data.guest_id).toBe(own.guest_id);
      }
    }
    expect(packets[0].some((packet) => packet.type === "private")).toBe(false);
    expect(packets[1].some((packet) => packet.type === "private")).toBe(false);
    const adaBrief = latestPrivate(packets[2]).character.private_brief;
    await guests[0]
      .getByRole("button", { name: "Reveal private brief" })
      .click();
    await expect(guests[0].getByText(adaBrief, { exact: true })).toBeVisible();
    for (const page of [host, tv, guests[1], guests[2], guests[3]]) {
      expect(await page.locator("body").textContent()).not.toContain(adaBrief);
    }
    // Reassignment is a host action, and a changed role conceals the new brief.
    await host
      .getByLabel("Character for Dinner Ada", { exact: true })
      .selectOption("investigator");
    await host
      .getByRole("button", {
        name: "Assign character to Dinner Ada",
        exact: true,
      })
      .click();
    await expect
      .poll(() => latestPrivate(packets[2])?.character.id)
      .toBe("investigator");
    await expect(
      guests[0].getByRole("button", { name: "Reveal private brief" }),
    ).toBeVisible();
    await host
      .getByLabel("Character for Dinner Sleuth", { exact: true })
      .selectOption("ada");
    await host
      .getByRole("button", {
        name: "Assign character to Dinner Sleuth",
        exact: true,
      })
      .click();
    await expect
      .poll(() => latestPrivate(packets[5])?.character.id)
      .toBe("ada");
    await guests[0]
      .getByLabel("Your public introduction", { exact: true })
      .fill("I am ready to examine the evidence.");
    await guests[0]
      .getByRole("button", { name: "Submit introduction" })
      .click();
    await expect(
      host.getByRole("region", { name: "Public introductions" }),
    ).toContainText("I am ready to examine the evidence.");
    await guests[2].reload({ waitUntil: "domcontentloaded" });
    await expect(
      guests[2].getByRole("region", { name: "Your private character" }),
    ).toContainText("Dr. Margot Vale");
    await expect(
      guests[2].getByRole("button", { name: "Reveal private brief" }),
    ).toBeVisible();
    await host.getByRole("button", { name: "Begin case" }).click();
    await expect(
      host.getByLabel("Character for Dinner Ada", { exact: true }),
    ).toBeDisabled();
    let count = 0;
    for (const act of [1, 2, 3]) {
      for (let clue = 0; clue < (act === 3 ? 1 : 2); clue++) {
        await host.getByRole("button", { name: "Reveal next clue" }).click();
        count++;
        await expect
          .poll(async () => (await state()).evidence.length)
          .toBe(count);
      }
      if (act < 3) {
        await host.getByRole("button", { name: /Next act/ }).click();
        await expect.poll(async () => (await state()).act).toBe(act + 1);
      }
    }
    const rationale = "The tray links access and opportunity.";
    await guests[1]
      .getByLabel("Reason for your accusation", { exact: true })
      .fill(rationale);
    await guests[1].getByRole("button", { name: "Accuse Dr." }).click();
    await expect
      .poll(() => latestPrivate(packets[3])?.own_vote?.rationale)
      .toBe(rationale);
    expect((await state()).accusations).toEqual([]);
    expect(JSON.stringify(await state())).not.toContain(rationale);
    await host.getByRole("button", { name: "Resolve the case" }).click();
    await expect
      .poll(async () =>
        (await state()).accusations.some(
          (item: any) => item.rationale === rationale,
        ),
      )
      .toBe(true);
    await expect(guests[3].getByText(rationale, { exact: true })).toBeVisible();
    expect(errors).toEqual([]);
  } finally {
    await Promise.all(contexts.map((context) => context.close()));
  }
});
