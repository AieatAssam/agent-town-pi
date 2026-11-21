const fs=require('fs');
const js=fs.readFileSync('/work/scratch/gob/check_body.js','utf8');
function el(){return {style:{},className:'',textContent:'',addEventListener(){},getContext(){return new Proxy({},{get:()=>()=>({addEventListener(){}}),set:()=>true})}}}
const els={c:el(),msg:el(),hud:el()};
els.c.getContext=()=>new Proxy({},{get:(_,k)=>typeof k==='string'&&k==='measureText'?()=>({width:0}):()=>{},set:()=>true});
global.document={getElementById:id=>els[id]};
global.window={addEventListener(){}};
global.requestAnimationFrame=()=>{};
eval(js);
const S=window.__snack;
function run(tapTimes){
  S.reset(); S.startRun();
  const dt=1/60; let tapsDone=new Set();
  while(S.state==='running'){
    for(const tt of tapTimes){ if(!tapsDone.has(tt) && S.t>=tt){ tapsDone.add(tt); S.tapBrake(); } }
    S.update(dt);
  }
  return {state:S.state,jamAt:S.jamAt,msg:els.msg.textContent,hud:els.hud.textContent};
}
console.log('clean:', run([]));
console.log('tap 3s:', run([3.0]));
console.log('tap 6s:', run([6.0]));
