const fs = require('fs');
const html = fs.readFileSync('/work/projects/squashed-scone/index.html', 'utf8');
const js = html.split('<script>')[1].split('</script>')[0];
function el(id){ return {id, value: id==='k'?'1':(id==='lat'?'45':'' ), textContent:'', listeners:{}, addEventListener(t,f){this.listeners[t]=f;}}; }
const els = {c:{width:560,height:560,getContext(){return new Proxy({}, {get:(t,p)=> (p in t)?t[p]:(typeof p==='string'? (()=>{}):undefined), set:(t,p,v)=>{t[p]=v;return true;}});}}, k:el('k'), lat:el('lat'), kv:el('kv'), latv:el('latv'), out:el('out'), real:el('real')};
els.k.value='1'; els.lat.value='45';
global.document = { getElementById: id => els[id] };
eval(js);
console.log('REAL k=1:\n' + els.out.textContent);
els.k.value='50'; els.k.listeners.input();
console.log('\nk=50:\n' + els.out.textContent);
els.lat.value='0'; els.lat.listeners.input();
console.log('\nlat 0, k=50 diff:', els.out.textContent.split('\n')[5]);
els.lat.value='90'; els.k.value='100'; els.lat.listeners.input(); els.k.listeners.input();
console.log('\nlat 90 k=100:\n' + els.out.textContent);
els.real.listeners.click();
console.log('\nafter real click k=', els.k.value, els.out.textContent.split('\n')[0]);
