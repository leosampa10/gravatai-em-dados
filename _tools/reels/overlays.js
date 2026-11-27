// node overlays.js jobs.json  -> renders transparent PNGs (1080x1920) from HTML snippets
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const J=JSON.parse(fs.readFileSync(process.argv[2]));const b=await chromium.launch();
const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.setContent(`<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,400;0,600;0,700;0,800;0,900;1,800&display=swap" rel="stylesheet"><style>${J.css}</style></head><body><div id="r"></div></body></html>`);
await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
for(const [html,out] of J.items){await p.evaluate(h=>{document.getElementById('r').innerHTML=h},html);await p.waitForTimeout(60);await p.screenshot({path:out,omitBackground:true});}
await b.close()})();
