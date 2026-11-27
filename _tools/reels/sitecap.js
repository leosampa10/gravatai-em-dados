// node sitecap.js '{"goto":"camara:c-dos","anchor":"#ficha","pan":900,"off":80}' out.png
// print alto do site (tema claro, celular 390 px) a partir da âncora, para o reel "rolar" a tela
// opções extras:
//   q: "?peleia=g0-6"       query string na abertura
//   tela: true              print só da tela (844 px), com botões fixos (Peleia, dock) visíveis
//   hl: ".gv-pel"           contorno ocre em volta de um elemento (com tela:true)
//   pel: "v" | "g"          abre a Peleia (vereadores / gestões) e fotografa a janela inteira
//   story: ["v","a","b"]    gera o post de story da Peleia (1080x1920) em vez de print
const {chromium}=require('playwright');(async()=>{const S=JSON.parse(process.argv[2]);const out=process.argv[3];
const b=await chromium.launch();const p=await b.newPage({viewport:{width:390,height:844},deviceScaleFactor:3});
await p.addInitScript(()=>{localStorage.setItem('gv-wl','skip');localStorage.setItem('gv-rv','off');localStorage.setItem('gv-dock-hint','1')});
await p.goto('file://'+require('path').resolve(__dirname,'../../index.html')+(S.q||''));await p.waitForTimeout(1500);
if(S.goto)await p.evaluate(g=>goto(g),S.goto);await p.waitForTimeout(800);
await p.addStyleTag({content:'.gv-top,.gv-tip{display:none!important}mark.gr .w{transition:none!important;background-size:100% 78%!important}'+(S.tela||S.pel?'':'.gv-pel,.gv-dock{display:none!important}')});
for(const c of (S.clicks||[])){const el=p.locator(c).first();if(await el.count()){await el.click();await p.waitForTimeout(500);}}
if(S.story){const u=await p.evaluate(a=>gvPeleiaImg(a[0],a[1],a[2],'st',.92),S.story);require('fs').writeFileSync(out,Buffer.from(u.split(',')[1],'base64'));await b.close();console.log(Math.round(390*1920/1080));return}
if(S.pel){await p.evaluate(m=>{if(!document.querySelector('.pel'))gvPeleia(m)},S.pel);await p.waitForTimeout(900);
 await p.evaluate(()=>{const v=document.querySelector('.pel-veil'),e=document.querySelector('.pel');v.style.cssText+=';position:absolute!important;inset:0 auto auto 0!important;width:390px!important;height:auto!important;background:transparent!important;display:block!important;padding:0!important';e.style.cssText+=';max-height:none!important;overflow:visible!important;position:relative!important;transform:none!important;margin:0!important;border-radius:0!important;width:390px!important;box-shadow:none!important;animation:none!important';document.body.style.overflow=''});
 await p.waitForTimeout(400);const bx=await p.locator('.pel').first().boundingBox();const h=Math.round(bx.height);
 await p.setViewportSize({width:390,height:Math.max(844,h+20)});await p.waitForTimeout(300);
 await p.locator('.pel').first().screenshot({path:out});await b.close();console.log(h);return}
if(S.tela){if(S.hl)await p.addStyleTag({content:`${S.hl}{outline:5px solid #F2CE6E!important;outline-offset:5px}`});
 if(S.anchor&&S.anchor!=='top')await p.evaluate(([a,o])=>{const e=document.querySelector(a);if(e)scrollTo(0,e.getBoundingClientRect().top+scrollY-o)},[S.anchor,S.off||80]);
 await p.waitForTimeout(500);await p.screenshot({path:out});await b.close();console.log(844);return}
await p.evaluate(()=>{document.querySelectorAll('body *').forEach(e=>{const ps=getComputedStyle(e).position;if(ps==='sticky'||ps==='fixed')e.style.setProperty('position','relative','important')})});
let y=0;if(S.anchor&&S.anchor!=='top'){y=await p.locator(S.anchor).first().evaluate((e,o)=>Math.max(0,e.getBoundingClientRect().top+scrollY-o),S.off||80);}
const H=await p.evaluate(()=>document.documentElement.scrollHeight);const h=Math.min(844+(S.pan||0),H-y);
await p.screenshot({path:out,fullPage:true,clip:{x:0,y,width:390,height:h}});await b.close();console.log(h)})();
