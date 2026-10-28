import { test, expect } from '@playwright/test';

test('local TalkingHead plays timed mouth shapes and stops on voice change', async ({ page }) => {
  test.setTimeout(120000);
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/?view=audition');
  const avatar = page.getByLabel('TalkingHead audition avatar');
  await expect(avatar).toHaveAttribute('data-model-state', 'ready', { timeout: 60000 });
  await expect(avatar.locator('canvas')).toBeVisible();
  await page.getByRole('button', { name: 'Play audition', exact: true }).click();
  await expect(avatar).toHaveAttribute('data-speaking', 'true');
  await expect.poll(async () => Number(await avatar.getAttribute('data-viseme-motion-count'))).toBeGreaterThan(2);
  await page.getByLabel('Existing voice').selectOption('david');
  await expect(avatar).toHaveAttribute('data-speaking', 'false');
  await expect.poll(async () => Number(await avatar.getAttribute('data-viseme-max'))).toBeLessThan(0.02);
  await page.getByRole('button', { name: 'Play audition', exact: true }).click();
  await expect(avatar).toHaveAttribute('data-speaking', 'true');
  await page.getByRole('button', { name: 'Stop audition', exact: true }).click();
  await expect(avatar).toHaveAttribute('data-speaking', 'false');
  expect(errors).toEqual([]);
});

test('missing recordings explain preparation without offering playback', async ({ page }) => {
  await page.route('**/api/audition', route => route.fulfill({ json: {available: false, voices: []} }));
  await page.goto('/?view=audition');
  await expect(page.getByRole('alert')).toContainText('not prepared');
  await expect(page.getByRole('button', {name: 'Play audition', exact: true})).toBeDisabled();
});
