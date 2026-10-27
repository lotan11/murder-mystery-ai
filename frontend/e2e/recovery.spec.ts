import { test, expect } from '@playwright/test';
test('TV keeps captions after a lost WebGL context', async ({ page }) => {
 const room = await (await page.request.post('/api/rooms')).json();
 await page.emulateMedia({ reducedMotion: 'reduce' });
 await page.goto(`/?view=tv&room=${room.room_id}`);
 const canvas = page.locator('.detective-view canvas');
 await expect(canvas).toBeVisible();
 await canvas.evaluate(element => element.dispatchEvent(new Event('webglcontextlost', { cancelable: true })));
 await expect(page.getByLabel('Detective portrait fallback')).toBeVisible();
 await expect(page.locator('.stage-subtitles')).toContainText('Good evening');
 await expect(page.getByLabel('Latest evidence')).toContainText('A rather inconvenient death.');
});
