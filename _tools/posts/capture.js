// usage: node capture.js spec.json outdir
const {chromium}=require('playwright');const fs=require('fs');
const [,,specf,out]=process.argv;const S=JSON.parse(fs.readFileSync(specf));fs.mkdirSync(out,{recursive:true});
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:3});
const p=await ctx.newPage();await p.addInitScript(()=>{localStorage.setItem('gv-wl','skip');});
await p.goto('file://'+require('path').resolve(__dirname,'../../index.html'));await p.waitForTimeout(1200);
if(!S.light){await p.click('#tt');await p.waitForTimeout(300);}
await p.evaluate(g=>goto(g),S.goto);await p.waitForTimeout(700);
await p.addStyleTag({content:'.chart svg{min-width:0!important;width:100%!important}'+(S.view?'':'*{transition-duration:0s!important;animation-duration:0s!important}html,body{scroll-behavior:auto!important}')});
await p.waitForTimeout(200);
if(S.light&&!S.view)await p.evaluate(()=>{document.querySelectorAll('body *').forEach(e=>{const ps=getComputedStyle(e).position;if(ps==='sticky'||ps==='fixed')e.style.setProperty('position','static','important')});document.querySelectorAll('.gv-pel,.gv-dock,.gv-top').forEach(e=>e.style.display='none')});
if(S.view){const meta={frames:[]};let n=0;const VH=S.vh||560;
 const vshot=async(touch,hold=1)=>{const f=`${out}/f${String(n).padStart(4,'0')}.png`;await p.screenshot({path:f,clip:{x:0,y:0,width:390,height:VH}});meta.frames.push({f,hold,crop:null,touch:touch?{x:touch.x,y:touch.y}:null});n++;};
 const a=p.locator(S.anchor).first();await a.evaluate((e,off)=>{window.scrollTo({top:e.getBoundingClientRect().top+scrollY-off,behavior:'instant'})},S.off||70);await p.waitForTimeout(400);
 await vshot(null,16);
 for(const st of S.steps){const el=p.locator(st.sel).first();if(st.inline)await el.evaluate(e=>e.scrollIntoView({block:'nearest',inline:'center',behavior:'instant'}));await p.waitForTimeout(150);const bb=await el.boundingBox();const t={x:bb.x+bb.width/2,y:bb.y+bb.height/2};
  await vshot(t,9);await el.click();
  for(let i=0;i<(st.burst||6);i++){await p.waitForTimeout(70);await vshot(i<2?t:null,2);}
  await p.waitForTimeout(300);await vshot(null,st.hold||30);}
 await vshot(null,30);
 fs.writeFileSync(`${out}/meta.json`,JSON.stringify(meta));await b.close();return;}

let card=null;if(S.cardId){card=await p.$('#'+S.cardId);}
const cards=card?[]:await p.$$(S.cardSel||'.card');
for(const c of cards){const t=await c.evaluate(e=>(e.querySelector('h2,h3')||{}).textContent||'');if(new RegExp(S.title,'i').test(t)&&await c.isVisible()){card=c;break;}}
if(!card)throw new Error('card not found '+S.title);
for(const a of (S.prep||[])){const el=await card.$(a);if(el){await el.click();await p.waitForTimeout(350);}}
await card.evaluate(e=>e.scrollIntoView({block:'start'}));await p.evaluate(()=>scrollBy(0,-12));await p.waitForTimeout(300);
const clipOf=async()=>{const r=await card.evaluate((e,sel)=>{const a=e.getBoundingClientRect();let b=a.bottom;if(sel){const q=e.querySelector(sel);if(q)b=Math.min(a.bottom,q.getBoundingClientRect().bottom+6);}return {x:a.left,y:a.top,width:a.width,height:b-a.top}},S.clipTo||null);r.height=Math.min(r.height,S.maxH||700);return r};
let clip=await clipOf();const meta={frames:[]};let n=0;
const shot=async(touch,hold=1)=>{const cr=await card.boundingBox();clip=await clipOf();const f=`${out}/f${String(n).padStart(4,'0')}.png`;await card.screenshot({path:f});meta.frames.push({f,hold,crop:clip.height,touch:touch?{x:(touch.x-cr.x),y:(touch.y-cr.y)}:null,w:clip.width,h:clip.height});n++;};
const A=S.anim||{type:'none'};
if(A.type==='slider'){const inp=await card.$('input[type=range]');const bb=await inp.boundingBox();const mn=+await inp.getAttribute('min'),mx=+await inp.getAttribute('max');if(A.from==null)A.from=mx;if(A.to==null)A.to=mn;
  const pos=async v=>{const bb=await (await card.$('input[type=range]')).boundingBox();return {x:bb.x+8+(bb.width-16)*(v-mn)/(mx-mn),y:bb.y+bb.height/2}};
  await (await card.$('input[type=range]')).evaluate((e,v)=>{e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))},A.from);await p.waitForTimeout(150);
  await shot(null,12);await shot(await pos(A.from),8);
  const step=A.from>A.to?-1:1;for(let v=A.from+step;step>0?v<=A.to:v>=A.to;v+=step){await (await card.$('input[type=range]')).evaluate((e,v)=>{e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))},v);await p.waitForTimeout(80);await shot(await pos(v),A.hold||4);}
  await shot(null,45);}
else if(A.type==='scrub'){const r=await (await card.$('svg rect[style]')).boundingBox();await shot(null,12);
  const N=A.steps||18;for(let i=0;i<=N;i++){const x=r.x+r.width*((A.from??0)+((A.to??1)-(A.from??0))*i/N);const y=r.y+r.height*0.5;await p.mouse.move(x,y);await p.waitForTimeout(60);await shot({x,y:r.y+r.height+4},A.hold||4);}
  await shot({x:r.x+r.width*(A.to??1),y:r.y+r.height+4},40);}
else if(A.type==='toggle'){const btn=await card.$(A.btn);const bb=await btn.boundingBox();const t={x:bb.x+bb.width/2,y:bb.y+bb.height/2};
  await shot(null,20);await shot(t,10);await btn.click();await p.waitForTimeout(300);if(A.after){for(const c of await p.$$('.card')){const t=await c.evaluate(e=>(e.querySelector('h2,h3')||{}).textContent||'');if(new RegExp(A.after,'i').test(t)&&await c.isVisible()){card=c;break;}}await card.evaluate(e=>e.scrollIntoView({block:'start'}));await p.waitForTimeout(200);}clip=await clipOf();const nb=await card.$(A.btn);if(nb){const q=await nb.boundingBox();t.x=q.x+q.width/2;t.y=q.y+q.height/2;}await shot(t,10);await shot(null,55);}
else if(A.type==='clicks'){await shot(null,16);
  for(const st of A.steps){const el=await card.$(st.sel);if(!el)throw new Error('no el '+st.sel);await el.scrollIntoViewIfNeeded();const bb=await el.boundingBox();const t={x:bb.x+bb.width/2,y:bb.y+bb.height/2};
   await shot(t,9);await el.click();await p.waitForTimeout(st.wait||350);
   if(st.after){for(const c of await p.$$('.card')){const tt=await c.evaluate(e=>(e.querySelector('h2,h3')||{}).textContent||'');if(new RegExp(st.after,'i').test(tt)&&await c.isVisible()){card=c;break;}}}
   if(st.top!==false){await card.evaluate(e=>e.scrollIntoView({block:'start'}));await p.waitForTimeout(150);}
   await shot(null,st.hold||30);}
  await shot(null,30);}
else {await shot(null,90);}
fs.writeFileSync(`${out}/meta.json`,JSON.stringify(meta));await b.close();})().catch(e=>{console.error(e);process.exit(1)});
