import {test,expect} from '@playwright/test';

test('Scholar workbench loads real development geometry without activating the game',async({page})=>{
 test.setTimeout(90000);const errors:string[]=[];const speech:string[]=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.url().includes('scholar-speech'))speech.push(r.url());});
 await page.goto('/?view=character-lab');
 const viewer=page.getByLabel('Scholar 3D workbench',{exact:true});
 await expect(viewer).toHaveAttribute('data-model-state','ready',{timeout:60000});
 await expect(viewer.locator('canvas')).toBeVisible();
 expect(Number(await viewer.getAttribute('data-mesh-count'))).toBeGreaterThan(0);
 await page.getByRole('button',{name:'Profile',exact:true}).click();
 await expect(page.getByRole('button',{name:'Profile',exact:true})).toHaveAttribute('aria-pressed','true');
 await page.getByRole('button',{name:'Three-quarter',exact:true}).click();
 await expect(page.getByRole('button',{name:'Three-quarter',exact:true})).toHaveAttribute('aria-pressed','true');
 await page.getByRole('button',{name:'Reset camera',exact:true}).click();
 await expect(page.getByRole('button',{name:'Front',exact:true})).toHaveAttribute('aria-pressed','true');
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
