// Render the local site in an isolated headless Chrome profile.
// No packages, account cookies, or external site access are required.
import {spawn} from 'node:child_process';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const base=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const out=join(base,'_build');
const siteOrigin=process.env.SITE_ORIGIN;
const profile=join(out,'layout-browser');
await mkdir(profile,{recursive:true});
const candidates=[process.env.CHROME_PATH,
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome','/usr/bin/chromium','/usr/bin/chromium-browser'].filter(Boolean);
const chromePath=candidates.find(existsSync);
if(!chromePath)throw new Error('Set CHROME_PATH to a Chrome/Chromium executable for optional layout checks.');
const chrome=spawn(chromePath,[
  '--headless','--disable-gpu','--no-first-run','--no-default-browser-check',
  '--hide-scrollbars','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'
],{windowsHide:true,stdio:'ignore'});
const delay=ms=>new Promise(r=>setTimeout(r,ms));
let ws;
const pending=new Map();
let next=0;
async function call(method,params={}){
  const id=++next;
  return new Promise((res,rej)=>{
    const timer=setTimeout(()=>{pending.delete(id);rej(new Error('Timeout: '+method));},15000);
    pending.set(id,{res,rej,timer});
    ws.send(JSON.stringify({id,method,params}));
  });
}
try{
  let port,tabs;
  for(let i=0;i<80;i++){
    try{
      port=(await readFile(join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];
      if(port){
        tabs=await (await fetch('http://127.0.0.1:'+port+'/json/list')).json();
        if(tabs.some(t=>t.type==='page'))break;
      }
    }catch{}
    await delay(250);
  }
  if(!tabs?.some(t=>t.type==='page'))throw new Error('Chrome did not create its local debugging endpoint');
  ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
  await new Promise((res,rej)=>{ws.addEventListener('open',res,{once:true});ws.addEventListener('error',rej,{once:true});});
  ws.addEventListener('message',e=>{const m=JSON.parse(e.data);const p=pending.get(m.id);if(p){clearTimeout(p.timer);pending.delete(m.id);m.error?p.rej(new Error(JSON.stringify(m.error))):p.res(m.result);}});
  await call('Page.enable');
  const reports=[];
  for(const [name,width,height] of [['desktop',1440,1200],['mobile',390,844],['narrow',320,760],['research-desktop',1440,1200],['research-mobile',390,844],['research-narrow',320,760],['project-desktop',1440,1200],['project-wide',1920,1080],['project-laptop',1280,800],['project-tablet',768,1024],['project-mobile',390,844],['project-narrow',320,760]]){
    await call('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
    const localPage=name.startsWith('project-')?'research/myomimetic-exosuit/index.html':name.startsWith('research-')?'research/index.html':'index.html';
    await call('Page.navigate',{url:siteOrigin?new URL(localPage,siteOrigin).href:pathToFileURL(join(base,localPage)).href});
    for(let n=0;n<40;n++){
      const ready=await call('Runtime.evaluate',{expression:'document.readyState',returnByValue:true});
      if(ready.result.value==='complete')break;
      await delay(100);
    }
    await call('Runtime.evaluate',{expression:'document.fonts.ready.then(()=>true)',awaitPromise:true,returnByValue:true});
    await call('Runtime.evaluate',{expression:'Promise.all([...document.images].map(img=>img.decode())).then(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))))',awaitPromise:true,returnByValue:true});
    const inspection=await call('Runtime.evaluate',{expression:`JSON.stringify({width:innerWidth,clientWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth,brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),headings:[...document.querySelectorAll('h1,h2')].map(e=>e.textContent),overflow:[...document.querySelectorAll('main,aside,nav,article,p,h1,h2,h3')].filter(e=>e.getBoundingClientRect().right>innerWidth+1).map(e=>e.tagName+': '+e.textContent.slice(0,70))})`,returnByValue:true});
    const audit={name,...JSON.parse(inspection.result.value)};
    if(name.startsWith('project-')){
      const figures=await call('Runtime.evaluate',{expression:`JSON.stringify({images:[...document.querySelectorAll('.study-figure img')].map(img=>{const r=img.getBoundingClientRect(),p=img.closest('figure').getBoundingClientRect();return {file:img.src.split('/').pop(),width:r.width,left:r.left,right:r.right,fits:r.width>0&&r.left>=p.left-1&&r.right<=p.right+1&&r.right<=innerWidth&&r.left>=0,ratioPreserved:Math.abs(r.width/r.height-img.naturalWidth/img.naturalHeight)<0.01}}),pairs:[...document.querySelectorAll('.figure-pair')].map(pair=>{const [a,b]=[...pair.children].map(e=>e.getBoundingClientRect());return {sideBySide:Math.abs(a.top-b.top)<1&&a.right<=b.left+1,leftWidth:a.width,rightWidth:b.width}})})`,returnByValue:true});
      audit.figures=JSON.parse(figures.result.value);
    }
    const navigation=await call('Runtime.evaluate',{expression:`JSON.stringify({links:[...document.querySelectorAll('nav a')].map(a=>({text:a.textContent,href:a.getAttribute('href')})),active:document.querySelector('nav [aria-current="page"]')?.textContent,videos:document.querySelectorAll('video').length})`,returnByValue:true});
    audit.navigation=JSON.parse(navigation.result.value);
    const isHome=localPage==='index.html';
    if(audit.navigation.links.map(a=>a.text).join(',')!=='Home,Research'||audit.navigation.active!==(isHome?'Home':'Research')||audit.navigation.videos!==(isHome?0:1))throw new Error('Unexpected navigation/video structure: '+name);
    if(name==='research-desktop'||name==='research-mobile'||name==='project-desktop'){
      const playback=await call('Runtime.evaluate',{expression:`(async()=>{const v=document.querySelector('video'); if(!v)return {error:'Video element missing'}; if(v.readyState<1)await Promise.race([new Promise((r,j)=>{v.addEventListener('loadedmetadata',r,{once:true});v.addEventListener('error',()=>j(new Error('Video load failed')),{once:true});}),new Promise((_,j)=>setTimeout(()=>j(new Error('Video metadata timeout')),7000))]); v.muted=true; await v.play(); await new Promise(r=>setTimeout(r,500)); const result={duration:v.duration,width:v.videoWidth,height:v.videoHeight,playing:!v.paused,currentTime:v.currentTime,error:v.error?.message??null};v.pause();v.currentTime=0;return result;})()`,awaitPromise:true,returnByValue:true});
      audit.video=playback.result.value??{error:playback.exceptionDetails?.text??'Video check failed'};
    }
    reports.push(audit);
    const layout=await call('Page.getLayoutMetrics');
    const screenshot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width,height:Math.ceil(layout.cssContentSize.height),scale:1}});
    await writeFile(join(out,'site-'+name+'.png'),Buffer.from(screenshot.data,'base64'));
  }
  await writeFile(join(out,'layout-check.json'),JSON.stringify(reports,null,2));
  console.log(JSON.stringify(reports,null,2));
  if(reports.some(r=>r.scrollWidth>r.clientWidth||r.brokenImages.length||r.overflow.length||(r.video&&(!r.video.playing||r.video.error))||(r.figures&&(r.figures.images.length!==8||r.figures.images.some(i=>!i.fits||!i.ratioPreserved)||r.figures.pairs.length!==2||r.figures.pairs.some(p=>!p.sideBySide)))))process.exitCode=1;
}finally{
  if(ws?.readyState===WebSocket.OPEN){try{await call('Browser.close');}catch{}ws.close();}
  for(const p of pending.values())clearTimeout(p.timer);
}
