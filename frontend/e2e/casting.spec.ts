import { test, expect } from '@playwright/test';
import {readFileSync} from 'node:fs';
const sceneText = {
 arrival: 'Good evening. I am Detective Reginald P. Wobblebottom. A pleasure to meet you. I trust your evening has been less eventful than mine.',
 evidence: 'An interesting theory. Let us see whether the evidence is prepared to support it.',
 reassurance: 'Take your time. A careful answer is far more useful than a confident guess.'
};
const voices = ['George','Daniel','Lewis'];
const characters = ['A · The Classic','B · The Modern','C · The Scholar'];
const ids = ['bm_george','bm_daniel','bm_lewis'];

test('casting compares all nine pairings without autoplay or activating game assets',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/api/casting',r=>r.fulfill({json:{available:true,version:1,provider:'kokoro-onnx',test_fixture:true,
 voices:ids.map((id,i)=>({id,name:voices[i],locale:'en-GB',gender:'Male',samples:Object.entries(sceneText).map(([scene,text])=>({id:scene,title:scene,text,duration_ms:8000,audio_url:`/api/casting/audio/${id}/${scene}`}))}))}}));
 const requested:string[]=[];
 await page.route('**/api/casting/audio/**',r=>{requested.push(r.request().url());return r.fulfill({contentType:'audio/wav',body:readFileSync(new URL('../../data/audition-test/zira-greeting.wav',import.meta.url))});});
 await page.goto('/?view=casting');
 await expect(page.getByRole('heading',{name:'Cast the detective.'})).toBeVisible();
 await expect(page.getByText('Concept portrait — not a rigged 3D avatar',{exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'Play scene',exact:true})).toBeEnabled();
 expect(requested).toEqual([]);
 for(let c=0;c<3;c++)for(let v=0;v<3;v++){
  await page.getByRole('button',{name:`Select ${characters[c]} with ${voices[v]}`,exact:true}).click();
  await expect.poll(()=>page.locator('audio').evaluate((a:HTMLAudioElement)=>a.paused)).toBe(true);
  const portrait=page.getByLabel('Selected character concept').locator('img');
  await expect.poll(()=>portrait.evaluate((img:HTMLImageElement)=>img.complete&&img.naturalWidth>0)).toBe(true);
  await page.getByRole('button',{name:'Play scene',exact:true}).click();
  await expect.poll(()=>page.locator('audio').evaluate((a:HTMLAudioElement)=>!a.paused)).toBe(true);
  await expect(page.locator('audio')).toHaveAttribute('src',`/api/casting/audio/${ids[v]}/arrival`);
  expect(await page.locator('audio').evaluate((a:HTMLAudioElement)=>a.playbackRate)).toBe(v===2?1.05:1);
  expect(await page.locator('audio').evaluate((a:HTMLAudioElement)=>a.preservesPitch)).toBe(true);
  await expect(page.getByLabel('Current casting script')).toContainText(sceneText.arrival);
 }
 await page.getByLabel('Lewis pace').selectOption('1');
 await expect.poll(()=>page.locator('audio').evaluate((a:HTMLAudioElement)=>a.paused)).toBe(true);
 await page.getByRole('button',{name:'Play scene',exact:true}).click();
 await expect.poll(()=>page.locator('audio').evaluate((a:HTMLAudioElement)=>a.playbackRate)).toBe(1);
 await page.getByLabel('Audition scene').selectOption('evidence');
 await expect.poll(()=>page.locator('audio').evaluate((a:HTMLAudioElement)=>a.paused)).toBe(true);
 await expect(page.getByLabel('Current casting script')).toContainText(sceneText.evidence);
 await page.getByRole('button',{name:'Add to shortlist',exact:true}).click();
 await expect(page.getByLabel('Local casting shortlist')).toContainText('C · The Scholar + Lewis');
 await page.reload();
 await expect(page.getByLabel('Local casting shortlist')).toContainText('C · The Scholar + Lewis');
 expect(await page.locator('audio').evaluate((a:HTMLAudioElement)=>a.paused)).toBe(true);
 expect(errors).toEqual([]);
});

test('casting missing recordings preserves portraits and disables playback',async({page})=>{
 await page.route('**/api/casting',r=>r.fulfill({json:{available:false,version:1,provider:'kokoro-onnx',voices:[]}}));
 await page.goto('/?view=casting');
 await expect(page.getByRole('button',{name:'Play scene',exact:true})).toBeDisabled();
 await expect(page.getByText(/No Windows US voice is substituted/)).toBeVisible();
 await expect(page.getByRole('button',{name:'Select B · The Modern with Daniel',exact:true})).toBeVisible();
});
