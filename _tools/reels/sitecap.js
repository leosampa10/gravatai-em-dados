// node sitecap.js '{"goto":"camara:c-dos","anchor":"#ficha","pan":900,"off":80}' out.png
// print alto do site (tema claro, celular 390 px) a partir da âncora, para o reel "rolar" a tela
const {chromium}=require('playwright');(async()=>{const S=JSON.parse(process.argv[2]);const out=process.argv[3];
const b=await chromium.launch();const p=await b.newPage({viewport:{width:390,height:844},deviceScaleFactor:3});
await p.addInitScript(()=>{localStorage.setItem('gv-wl','skip');localStorage.setItem('gv-rv','off');localStorage.setItem('gv-dock-hint','1')});
await p.goto('file://'+require('path').resolve(__dirname,'../../index.html'));await p.waitForTimeout(1500);
if(S.goto)await p.evaluate(g=>goto(g),S.goto);await p.waitForTimeout(800);
await p.addStyleTag({content:'.gv-pel,.gv-top,.gv-tip,.gv-dock{display:none!important}mark.gr .w{transition:none!important;background-size:100% 78%!important}'});
for(const c of (S.clicks||[])){const el=p.locator(c).first();if(await el.count()){await el.click();await p.waitForTimeout(500);}}
await p.evaluate(()=>{document.querySelectorAll('body *').forEach(e=>{const ps=getComputedStyle(e).position;if(ps==='sticky'||ps==='fixed')e.style.setProperty('position','relative','important')})});
let y=0;if(S.anchor&&S.anchor!=='top'){y=await p.locator(S.anchor).first().evaluate((e,o)=>Math.max(0,e.getBoundingClientRect().top+scrollY-o),S.off||80);}
const H=await p.evaluate(()=>document.documentElement.scrollHeight);const h=Math.min(844+(S.pan||0),H-y);
await p.screenshot({path:out,fullPage:true,clip:{x:0,y,width:390,height:h}});await b.close();console.log(h)})();
