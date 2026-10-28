import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

// Synthetic audio is a transport/animation fixture, never a speech-quality audition.
const audioBase64 = () => readFileSync(new URL('../../data/audition-test/zira-greeting.wav', import.meta.url)).toString('base64');

test('TV performance is opt-in, speaks public dialogue, and stops on pause', async ({page, context}) => {
  test.setTimeout(150000);
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await page.getByRole('button', {name: /Create an evening/}).click();
  await expect(page).toHaveURL(/room=/);
  const room = new URL(page.url()).searchParams.get('room')!;
  const host = page;
  const tv = await context.newPage();
  let calls = 0;
  await tv.route('**/api/speech/status', route => route.fulfill({json:{available:true,provider:'windows-sapi',voices:[{id:'david',name:'Microsoft David Desktop'},{id:'zira',name:'Microsoft Zira Desktop'}],message:'Synthetic test fixture'}}));
  await tv.route(`**/api/rooms/${room}/speech/config`, route => route.fulfill({json: {
    available: true, voices: [{id:'david',name:'Microsoft David Desktop'},{id:'zira',name:'Microsoft Zira Desktop'}], tv_token:'test-read-only-capability'
  }}));
  await tv.route(`**/api/rooms/${room}/speech`, async route => {
    calls++;
    const request = route.request();
    expect(request.postDataJSON()).toEqual({voice: expect.stringMatching(/^(david|zira)$/)});
    const state = await (await tv.request.get(`/api/rooms/${room}/state`)).json();
    const words = state.dialogue.split(/\s+/);
    await route.fulfill({json: {
      text:state.dialogue, revision:state.revision, voice:request.postDataJSON().voice, audio_base64:audioBase64(),
      words, wtimes:words.map((_:string,i:number)=>i*100), wdurations:words.map(()=>80), duration_ms:8000, content_type:'audio/wav', provider:'windows-sapi', timing_source:'Synthetic test waveform and timings; not recorded speech'
    }});
  });
  await tv.goto(`/?view=tv&room=${room}#speech=test-read-only-capability`);
  await tv.getByLabel('Animated detective', {exact:true}).check();
  const avatar = tv.getByLabel('TalkingHead detective', {exact:true});
  await expect(avatar).toHaveAttribute('data-model-state','ready',{timeout:60000});
  expect(calls).toBe(0);
  await tv.getByRole('button',{name:'Enable local voice',exact:true}).click();
  await expect(avatar).toHaveAttribute('data-speaking','true');
  await expect.poll(async()=>Number(await avatar.getAttribute('data-viseme-motion-count'))).toBeGreaterThan(2);
  await host.getByRole('button',{name:'Pause evening',exact:true}).click();
  await expect(avatar).toHaveAttribute('data-speaking','false');
  await host.getByRole('button',{name:'Resume evening',exact:true}).click();
  await tv.getByRole('button',{name:'Replay dialogue',exact:true}).click();
  await expect(avatar).toHaveAttribute('data-speaking','true');
  await tv.getByRole('button',{name:'Mute local voice',exact:true}).click();
  await expect(avatar).toHaveAttribute('data-speaking','false');
  const mutedCalls = calls;
  await host.getByRole('button',{name:'Begin case',exact:true}).click();
  await expect(tv.getByText('ACT 1',{exact:true})).toBeVisible();
  expect(calls).toBe(mutedCalls);
  await expect(tv.getByLabel('Latest evidence',{exact:true})).toBeVisible();
  expect(errors).toEqual([]);
});
