// node render.js in.html out.png
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});
for(let i=2;i<process.argv.length;i+=2){await p.goto('file://'+process.argv[i]);await p.waitForTimeout(700);await p.screenshot({path:process.argv[i+1]});}await b.close();})();
