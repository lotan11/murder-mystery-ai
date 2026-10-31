import {test,expect} from '@playwright/test';

test('Scholar workbench loads real development geometry without activating the game',async({page})=>{
 test.setTimeout(90000);const errors:string[]=[];const speech:string[]=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.url().includes('scholar-speech'))speech.push(r.url());});
 await page.goto('/?view=character-lab');
 const viewer=page.getByLabel('Scholar 3D workbench',{exact:true});
 await expect(viewer).toHaveAttribute('data-model-state','ready',{timeout:60000});
 await expect(viewer.locator('canvas')).toBeVisible();
 await expect(viewer).toHaveAttribute('data-skin-map-count','0');
 expect(Number(await viewer.getAttribute('data-mesh-count'))).toBeGreaterThan(0);
 await page.getByRole('button',{name:'Profile',exact:true}).click();
 await expect(page.getByRole('button',{name:'Profile',exact:true})).toHaveAttribute('aria-pressed','true');
 await page.getByRole('button',{name:'Three-quarter',exact:true}).click();
 await expect(page.getByRole('button',{name:'Three-quarter',exact:true})).toHaveAttribute('aria-pressed','true');
 await page.getByRole('button',{name:'Reset camera',exact:true}).click();
 await expect(page.getByRole('button',{name:'Front',exact:true})).toHaveAttribute('aria-pressed','true');
 const canvasBounds=await viewer.locator('canvas').boundingBox();
 if(!canvasBounds)throw new Error('The model canvas has no drag surface');
 const beforeOrbit=Number(await viewer.getAttribute('data-render-count'));
 await page.mouse.move(canvasBounds.x+canvasBounds.width/2,canvasBounds.y+canvasBounds.height/2);
 await page.mouse.down();await page.mouse.move(canvasBounds.x+canvasBounds.width/2+70,canvasBounds.y+canvasBounds.height/2,{steps:4});await page.mouse.up();
 await expect.poll(async()=>Number(await viewer.getAttribute('data-render-count'))).toBeGreaterThan(beforeOrbit);
 // Orbit damping must finish naturally, then leave the GPU idle again.
 await expect.poll(async()=>{
   const before=await viewer.getAttribute('data-render-count');
   await page.waitForTimeout(300);
   return await viewer.getAttribute('data-render-count')===before;
 }).toBe(true);
 await expect(page.getByLabel('Loaded model inventory')).toContainText('not an approved likeness');
 await page.setViewportSize({width:390,height:844});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
 await viewer.locator('canvas').evaluate(element=>element.dispatchEvent(new Event('webglcontextlost',{cancelable:true})));
 await expect(viewer).toHaveAttribute('data-model-state','failed');
 await expect(page.locator('img[src="/casting/vale.png"]')).toBeVisible();
 expect(speech).toEqual([]);expect(errors).toEqual([]);
});

test('missing Scholar development model leaves reference and working-game link available',async({page})=>{
 await page.route('**/character-lab/scholar-blockout.glb',r=>r.fulfill({status:404,body:'Missing model'}));
 await page.goto('/?view=character-lab');
 await expect(page.getByLabel('Scholar 3D workbench',{exact:true})).toHaveAttribute('data-model-state','failed');
 await expect(page.getByRole('button',{name:'Front',exact:true})).toBeDisabled();
 await expect(page.locator('img[src="/casting/vale.png"]')).toBeVisible();
});


test('face study moves actual morphs within restrained limits and resets',async({page})=>{
 test.setTimeout(90000);
 await page.goto('/?view=character-lab');
 const viewer=page.getByLabel('Scholar 3D workbench',{exact:true});
 await page.getByLabel('Development model',{exact:true}).selectOption('face-study');
 await expect(viewer).toHaveAttribute('data-model-state','ready',{timeout:60000});
 await expect(viewer).toHaveAttribute('data-morph-count','3');
 await expect(viewer).toHaveAttribute('data-skin-map-count','0');
 await expect(page.getByRole('slider',{name:/brow|Lip rounding|Lip compression|Subtle smile/})).toHaveCount(0);
 const jaw=page.getByRole('slider',{name:/Jaw opening/});
 await jaw.focus();await jaw.press('End');
 await expect(jaw).toHaveValue('0.38');
 await expect(viewer).toHaveAttribute('data-morph-max','0.380');
 const blink=page.getByRole('slider',{name:/Left blink/});
 await blink.focus();await blink.press('End');
 await expect(blink).toHaveValue('1');
 await expect(viewer).toHaveAttribute('data-morph-max','1.000');
 await page.getByRole('button',{name:'Reset facial controls'}).click();
 await expect(jaw).toHaveValue('0');
 await expect(viewer).toHaveAttribute('data-morph-max','0.000');
 await page.getByLabel('Development model',{exact:true}).selectOption('blockout');
 await expect(viewer).toHaveAttribute('data-model-state','ready');
 await expect(viewer).toHaveAttribute('data-morph-count','0');
});


test('rig study turns the actual head bone, resets and retains facial controls',async({page})=>{
 test.setTimeout(90000);const errors:string[]=[];const speech:string[]=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('request',r=>{if(r.url().includes('scholar-speech'))speech.push(r.url());});
 await page.goto('/?view=character-lab');
 const viewer=page.getByLabel('Scholar 3D workbench',{exact:true});
 await page.getByLabel('Development model',{exact:true}).selectOption('rig-study');
 await expect(viewer).toHaveAttribute('data-model-state','ready',{timeout:60000});
 expect(Number(await viewer.getAttribute('data-joint-count'))).toBeGreaterThan(0);
 await expect(viewer).toHaveAttribute('data-morph-count','11');
 await expect(viewer).toHaveAttribute('data-skin-map-count','3');
 await expect(viewer).toHaveAttribute('data-iris-map-info','512x512/uv1/srgb');
 await expect(viewer).toHaveAttribute('data-hair-map-count','2');
 await expect(viewer).toHaveAttribute('data-hair-alpha-mode','blend');
 // The manual lab should draw its loaded pose, then leave the GPU idle.
 await expect.poll(async()=>{
   const before=await viewer.getAttribute('data-render-count');
   await page.waitForTimeout(300);
   return Number(before)>0 && await viewer.getAttribute('data-render-count')===before;
 }).toBe(true);
 const idleRenders=Number(await viewer.getAttribute('data-render-count'));
 await page.waitForTimeout(300);
 await expect(viewer).toHaveAttribute('data-render-count',String(idleRenders));
 const head=page.getByRole('slider',{name:/Head turn/});
 await head.focus();await head.press('End');
 await expect(head).toHaveValue('10');
 await expect(viewer).toHaveAttribute('data-head-turn','10.000');
 await expect.poll(async()=>Number(await viewer.getAttribute('data-render-count'))).toBeGreaterThan(idleRenders);
 await expect.poll(async()=>Number(await viewer.getAttribute('data-head-displacement'))).toBeGreaterThan(0.001);
 await head.press('Home');
 await expect(viewer).toHaveAttribute('data-head-turn','-10.000');
 await page.getByRole('button',{name:'Reset head pose'}).click();
 await expect(head).toHaveValue('0');
 await expect(viewer).toHaveAttribute('data-head-turn','0.000');
 await expect(viewer).toHaveAttribute('data-head-displacement','0.000000');
 const jaw=page.getByRole('slider',{name:/Jaw opening/});
 await jaw.focus();await jaw.press('End');
 await expect(viewer).toHaveAttribute('data-morph-max','0.380');
 await page.getByRole('button',{name:'Reset facial controls'}).click();
 for(const [label,limit] of [
   ['Inner brow lift','0.35'],['Left brow lift','0.35'],['Right brow lift','0.35'],
   ['Left brow lower','0.25'],['Right brow lower','0.25'],
   ['Lip rounding','0.25'],['Lip compression','0.25'],['Subtle smile','0.2'],
 ]){
   const brow=page.getByRole('slider',{name:new RegExp('^'+label)});
   await brow.focus();await brow.press('End');
   await expect(brow).toHaveValue(limit);
   await expect(viewer).toHaveAttribute('data-morph-active','1');
   await expect(viewer).toHaveAttribute('data-morph-max',Number(limit).toFixed(3));
   await page.getByRole('button',{name:'Reset facial controls'}).click();
   await expect(brow).toHaveValue('0');
   await expect(viewer).toHaveAttribute('data-morph-active','0');
   await expect(viewer).toHaveAttribute('data-morph-max','0.000');
 }
 await page.getByLabel('Development model',{exact:true}).selectOption('blockout');
 await expect(viewer).toHaveAttribute('data-model-state','ready');
 await expect(viewer).toHaveAttribute('data-joint-count','0');
 await expect(viewer).toHaveAttribute('data-iris-map-info','');
 await expect(viewer).toHaveAttribute('data-hair-map-count','0');
 await expect(head).toHaveCount(0);
 expect(speech).toEqual([]);expect(errors).toEqual([]);
});


test('fixed Lewis study uses user-initiated source-clock speech and stops on model change',async({page})=>{
 test.setTimeout(90000);const errors:string[]=[];const gameSpeech:string[]=[];
 // This scenario verifies explicit Stop/model cancellation, not natural completion.
 // Keep the real short clip playing if a slow runner takes longer than its duration.
 await page.addInitScript(()=>{
  const play=HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play=function(){
   if(this.dataset.labSpeech==='true')this.loop=true;
   return play.call(this);
  };
 });
 page.on('pageerror',e=>errors.push(e.message));
 page.on('request',r=>{if(r.url().includes('/scholar-speech'))gameSpeech.push(r.url());});
 await page.goto('/?view=character-lab');
 const viewer=page.getByLabel('Scholar 3D workbench',{exact:true});
 await page.getByLabel('Development model',{exact:true}).selectOption('rig-study');
 await expect(viewer).toHaveAttribute('data-model-state','ready',{timeout:60000});
 await expect(viewer).toHaveAttribute('data-speech-state','idle');
 await expect(page.locator('audio[data-lab-speech]')).toHaveCount(0);
 // Capture genuine transient motion as it occurs; polling can miss every voiced
 // frame and sample only neutral gaps. Never synthesize or modify a morph value.
 await viewer.evaluate(element=>{
  const observation={peak:0};(window as any).__labObservedMorph=observation;
  new MutationObserver(()=>{
   const audio=document.querySelector<HTMLAudioElement>('audio[data-lab-speech]');
   if(element.getAttribute('data-speech-state')==='playing'&&audio&&!audio.paused&&!audio.ended)
    observation.peak=Math.max(observation.peak,Number(element.getAttribute('data-morph-max')));
  }).observe(element,{attributes:true,attributeFilter:['data-morph-max']});
 });
 const head=page.getByRole('slider',{name:/Head turn/});await head.focus();await head.press('End');
 await page.getByRole('button',{name:'Play Lewis timing study',exact:true}).click();
 await expect(viewer).toHaveAttribute('data-speech-state','playing');
 const audio=page.locator('audio[data-lab-speech]');
 expect(await audio.evaluate(element=>(element as HTMLAudioElement).playbackRate)).toBe(1.05);
 expect(await audio.evaluate(element=>(element as HTMLAudioElement).preservesPitch)).toBe(true);
 await expect.poll(async()=>Number(await viewer.getAttribute('data-speech-time'))).toBeGreaterThan(0);
 await expect.poll(()=>page.evaluate(()=>(window as any).__labObservedMorph.peak)).toBeGreaterThan(0);
 await expect(page.getByRole('slider',{name:/Jaw opening/})).toBeDisabled();
 await page.getByRole('button',{name:'Stop timing study',exact:true}).click();
 await expect(viewer).toHaveAttribute('data-speech-state','idle');
 await expect(viewer).toHaveAttribute('data-morph-max','0.000');
 await expect(viewer).toHaveAttribute('data-head-turn','10.000');
 await expect(audio).toHaveCount(0);
 await page.getByRole('button',{name:'Play Lewis timing study',exact:true}).click();
 await expect(viewer).toHaveAttribute('data-speech-state','playing');
 await page.getByLabel('Development model',{exact:true}).selectOption('blockout');
 await expect(viewer).toHaveAttribute('data-model-state','ready');
 await expect(viewer).toHaveAttribute('data-speech-state','idle');
 await expect(audio).toHaveCount(0);
 expect(errors).toEqual([]);expect(gameSpeech).toEqual([]);
});

test('missing fixed timing study leaves manual rig controls available',async({page})=>{
 await page.route('**/character-lab/lewis-study.json',route=>route.fulfill({status:404,body:'Missing study'}));
 await page.goto('/?view=character-lab');
 await page.getByLabel('Development model',{exact:true}).selectOption('rig-study');
 const viewer=page.getByLabel('Scholar 3D workbench',{exact:true});
 await expect(viewer).toHaveAttribute('data-model-state','ready',{timeout:60000});
 await page.getByRole('button',{name:'Play Lewis timing study',exact:true}).click();
 await expect(viewer).toHaveAttribute('data-speech-state','error');
 await expect(page.getByRole('slider',{name:/Jaw opening/})).toBeEnabled();
 await expect(page.locator('audio[data-lab-speech]')).toHaveCount(0);
 await expect(page.getByLabel('Fixed Lewis timing study')).toContainText('unavailable');
});

test('fixed Lewis study stops on graphics loss and rejects mismatched audio',async({page})=>{
 await page.goto('/?view=character-lab');
 await page.getByLabel('Development model',{exact:true}).selectOption('rig-study');
 const viewer=page.getByLabel('Scholar 3D workbench',{exact:true});
 await expect(viewer).toHaveAttribute('data-model-state','ready',{timeout:60000});
 await page.getByRole('button',{name:'Play Lewis timing study',exact:true}).click();
 await expect(viewer).toHaveAttribute('data-speech-state','playing');
 await viewer.locator('canvas').evaluate(element=>element.dispatchEvent(new Event('webglcontextlost',{cancelable:true})));
 await expect(viewer).toHaveAttribute('data-model-state','failed');
 await expect(viewer).toHaveAttribute('data-speech-state','idle');
 await expect(page.locator('audio[data-lab-speech]')).toHaveCount(0);
 await page.route('**/character-lab/lewis-study.json',async route=>{
   const response=await route.fetch();const data=await response.json();data.audio_sha256='0'.repeat(64);
   await route.fulfill({response,json:data});
 });
 await page.reload();await page.getByLabel('Development model',{exact:true}).selectOption('rig-study');
 await expect(viewer).toHaveAttribute('data-model-state','ready',{timeout:60000});
 await page.getByRole('button',{name:'Play Lewis timing study',exact:true}).click();
 await expect(viewer).toHaveAttribute('data-speech-state','error');
 await expect(page.getByLabel('Fixed Lewis timing study')).toContainText('does not match');
 await expect(page.locator('audio[data-lab-speech]')).toHaveCount(0);
});


test('pending fixed study can be cancelled and hidden page stops playback',async({page})=>{
 let release=()=>{};const gate=new Promise<void>(resolve=>{release=resolve;});
 let entered=false;let completed=()=>{};const finished=new Promise<void>(resolve=>{completed=resolve;});
 await page.route('**/character-lab/lewis-study.json',async route=>{
   const response=await route.fetch();entered=true;await gate;
   try{await route.fulfill({response});}finally{completed();}
 });
 await page.goto('/?view=character-lab');
 await page.getByLabel('Development model',{exact:true}).selectOption('rig-study');
 const viewer=page.getByLabel('Scholar 3D workbench',{exact:true});
 await expect(viewer).toHaveAttribute('data-model-state','ready',{timeout:60000});
 await page.getByRole('button',{name:'Play Lewis timing study',exact:true}).click();
 await expect.poll(()=>entered).toBe(true);
 await expect(viewer).toHaveAttribute('data-speech-state','loading');
 await page.getByRole('button',{name:'Stop timing study',exact:true}).click();
 release();await finished;
 await expect(viewer).toHaveAttribute('data-speech-state','idle');
 await expect(page.locator('audio[data-lab-speech]')).toHaveCount(0);
 await page.unroute('**/character-lab/lewis-study.json');
 await page.getByRole('button',{name:'Play Lewis timing study',exact:true}).click();
 await expect(viewer).toHaveAttribute('data-speech-state','playing');
 await page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'));});
 await expect(viewer).toHaveAttribute('data-speech-state','idle');
 await expect(viewer).toHaveAttribute('data-morph-max','0.000');
 await expect(page.locator('audio[data-lab-speech]')).toHaveCount(0);
});


test('face framing fits decoded crown and chin on desktop and phone while preserving the view',async({page})=>{
 test.setTimeout(90000);
 await page.goto('/?view=character-lab');
 const viewer=page.getByLabel('Scholar 3D workbench',{exact:true});
 await page.getByLabel('Development model',{exact:true}).selectOption('rig-study');
 await expect(viewer).toHaveAttribute('data-model-state','ready',{timeout:60000});
 await expect(viewer).toHaveAttribute('data-frame-mode','bust');
 await expect(viewer).toHaveAttribute('data-face-anchor','loaded-eye-geometry');
 expect(Number(await viewer.getAttribute('data-face-world-bottom'))).toBeLessThan(Number(await viewer.getAttribute('data-groom-world-bottom')));
 const bounds=async()=>JSON.parse((await viewer.getAttribute('data-face-ndc'))||'{}');
 const bust=await bounds();
 await page.getByRole('button',{name:'Face close-up',exact:true}).click();
 await expect(viewer).toHaveAttribute('data-frame-mode','face');
 const portraitCrop=page.getByRole('img',{name:'Portrait head crop · same approved image',exact:true});
 await expect(portraitCrop).toBeVisible();
 await expect(portraitCrop).toHaveAttribute('viewBox','230 -45 570 680');
 await expect(portraitCrop).toHaveAttribute('preserveAspectRatio','xMidYMid meet');
 await expect(portraitCrop.locator('image')).toHaveAttribute('href','/casting/vale.png');
 await expect(portraitCrop.locator('image')).toHaveAttribute('width','1145');
 await expect(portraitCrop.locator('image')).toHaveAttribute('height','1374');
 // Original source-pixel landmarks: crown (~y20), ears and beard/chin (~y520)
 // all remain inside this viewBox; meet letterboxes rather than cropping on phones.
 expect(await portraitCrop.evaluate(element=>{
  const box=(element as SVGSVGElement).viewBox.baseVal;
  return box.x<=300 && box.x+box.width>=730 && box.y<=20 && box.y+box.height>=535;
 })).toBe(true);
 await expect(page.getByRole('button',{name:'Face close-up',exact:true})).toHaveAttribute('aria-pressed','true');
 await expect.poll(async()=>{const b=await bounds();return b.top-b.bottom;}).toBeGreaterThan(bust.top-bust.bottom);
 const fits=async()=>{const b=await bounds();return b.top<.95&&b.bottom>-.95&&b.left>-.95&&b.right<.95&&b.top-b.bottom>.6;};
 await expect.poll(fits).toBe(true);
 await page.getByRole('button',{name:'Three-quarter',exact:true}).click();
 await expect.poll(fits).toBe(true);
 await expect.poll(async()=>JSON.parse((await viewer.getAttribute('data-camera-direction'))!)[0]).toBeGreaterThan(.5);
 const direction=JSON.parse((await viewer.getAttribute('data-camera-direction'))!);
 await page.getByRole('button',{name:'Full bust',exact:true}).click();
 await expect(viewer).toHaveAttribute('data-frame-mode','bust');
 await expect.poll(async()=>{
  const current=JSON.parse((await viewer.getAttribute('data-camera-direction'))!);
  return Math.max(...current.map((v:number,i:number)=>Math.abs(v-direction[i])));
 }).toBeLessThan(.001);
 await page.getByRole('button',{name:'Face close-up',exact:true}).click();
 await page.getByRole('button',{name:'Front',exact:true}).click();
 await expect.poll(async()=>Math.abs(JSON.parse((await viewer.getAttribute('data-camera-direction'))!)[0])).toBeLessThan(.001);
 await page.screenshot({path:test.info().outputPath('face-desktop.png'),fullPage:true});
 const beforeResize=Number(await viewer.getAttribute('data-render-count'));
 await page.setViewportSize({width:390,height:844});
 await expect.poll(async()=>Number(await viewer.getAttribute('data-render-count'))).toBeGreaterThan(beforeResize);
 await expect.poll(fits).toBe(true);
 await page.screenshot({path:test.info().outputPath('face-mobile.png'),fullPage:true});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)).toBe(false);
 await page.getByRole('button',{name:'Reset camera',exact:true}).click();
 await expect(viewer).toHaveAttribute('data-frame-mode','bust');
 await expect(page.getByRole('button',{name:'Front',exact:true})).toHaveAttribute('aria-pressed','true');
 await expect(page.locator('img[src="/casting/vale.png"]')).toBeVisible();
 await expect(portraitCrop).toHaveCount(0);
 await page.getByRole('button',{name:'Face close-up',exact:true}).click();
 await page.getByLabel('Development model',{exact:true}).selectOption('face-study');
 await expect(viewer).toHaveAttribute('data-model-state','ready',{timeout:60000});
 await expect(viewer).toHaveAttribute('data-frame-mode','bust');
 await expect(page.locator('img[src="/casting/vale.png"]')).toBeVisible();
 await expect(portraitCrop).toHaveCount(0);
});
