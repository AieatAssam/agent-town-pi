// headless copy of snack-goblin sim core, parametrised
function run({decel=-90, hold=0.5, tapAt=null, tapCar=0, seedDec=-55, seedDur=0.6, seedAt=1.2, dt=1/60}={}) {
  const CX=400,CY=180,RX=300,RY=120,N=12,RUN=9.0,V0=60,S0=22,T=1.1,A=38,B=55,JAM_V=12;
  const TRACK_LEN=2*Math.PI*((RX+RY)/2);
  const SPACING=TRACK_LEN/N;
  let cars=[];
  for(let i=0;i<N;i++) cars.push({s:i*SPACING,v:V0,a:0,you:i===tapCar,seedBrake:0});
  let t=0,brakeTimer=0,seeded=false,minSpeed=V0,jamAt=null;
  const gap=i=>{let d=cars[(i+1)%N].s-cars[i].s; if(d<0)d+=TRACK_LEN; return d;};
  let tapped=false;
  while(t<RUN){
    if(tapAt!==null && !tapped && t>=tapAt){brakeTimer=hold;tapped=true;}
    if(!seeded && t>=seedAt){cars[6].seedBrake=seedDur;seeded=true;}
    for(let i=0;i<N;i++){
      const c=cars[i],lead=cars[(i+1)%N];
      const s=Math.max(gap(i)-4,0.1);
      const dv=c.v-lead.v;
      const sStar=S0+Math.max(0,c.v*T+(c.v*dv)/(2*Math.sqrt(A*B)));
      let acc=A*(1-Math.pow(c.v/V0,4)-(sStar*sStar)/(s*s));
      if(c.you&&brakeTimer>0) acc=Math.min(acc,decel);
      if(c.seedBrake>0){acc=Math.min(acc,seedDec);c.seedBrake-=dt;}
      c.a=acc;
    }
    for(const c of cars){c.v=Math.max(0,c.v+c.a*dt);c.s+=c.v*dt;if(c.s>=TRACK_LEN)c.s-=TRACK_LEN;}
    if(brakeTimer>0)brakeTimer-=dt;
    t+=dt;
    for(const c of cars) minSpeed=Math.min(minSpeed,c.v);
    if(jamAt===null&&minSpeed<JAM_V) jamAt=t;
  }
  return {jam: jamAt!==null, jamAt, minSpeed};
}
module.exports={run};
if(require.main===module){
  console.log('no taps:', run());
  console.log('seed -55 0.6s, tap decel/hold sweep (tap at 3s, car 0):');
  for(const d of [-90,-70,-50,-40,-30]) for(const h of [0.2,0.3,0.5]) {
    const r=run({decel:d,hold:h,tapAt:3});
    console.log(`decel ${d} hold ${h}: jam=${r.jam} at=${r.jamAt&&r.jamAt.toFixed(2)} min=${r.minSpeed.toFixed(1)}`);
  }
}
