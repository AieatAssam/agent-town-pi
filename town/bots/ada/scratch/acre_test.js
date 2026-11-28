
const els={};
function mk(id){return {id,innerHTML:'',textContent:'',className:'',children:[],appendChild(c){this.children.push(c)},addEventListener(t,f){(this.l=this.l||{})[t]=f},onclick:null};}
const document={getElementById:(id)=>(els[id]=els[id]||mk(id)),createElement:()=>mk('div')};

const TOTAL = 1023, COLS = 33, FIRST = 31;
const grid = document.getElementById('grid');
const readout = document.getElementById('readout');
let owned = [];
const cells = [];

function build() {
  grid.innerHTML = '';
  cells.length = 0;
  for (let i = 0; i < TOTAL; i++) {
    const d = document.createElement('div');
    d.className = 'c';
    d.addEventListener('click', () => { buy(i); render(); });
    grid.appendChild(d);
    cells.push(d);
  }
}

function reset() {
  owned = new Array(TOTAL).fill(false);
  for (let i = 0; i < FIRST; i++) owned[i] = true;
  render();
}

function buy(i) {
  if (i < 0 || i >= TOTAL || owned[i]) return false;
  owned[i] = true;
  return true;
}

function nextFree(n) {
  let bought = 0;
  for (let i = 0; i < TOTAL && bought < n; i++) {
    if (buy(i)) bought++;
  }
  return bought;
}

function randomFree(n) {
  let bought = 0;
  let free = [];
  for (let i = 0; i < TOTAL; i++) if (!owned[i]) free.push(i);
  while (bought < n && free.length) {
    const k = Math.floor(Math.random() * free.length);
    const i = free[k];
    free[k] = free[free.length - 1];
    free.pop();
    buy(i);
    bought++;
  }
  return bought;
}

function count() {
  let n = 0;
  for (const o of owned) if (o) n++;
  return n;
}

function render() {
  let n = 0;
  for (let i = 0; i < TOTAL; i++) {
    const c = cells[i];
    c.className = 'c' + (owned[i] ? (i < FIRST ? ' first' : ' own') : '');
    if (owned[i]) n++;
  }
  const pct = (n / TOTAL * 100).toFixed(1);
  let line = `${n.toLocaleString()} of 1,023 acres (${pct}%)`;
  if (n === TOTAL) {
    line += ' . all of it. the toy cannot tell you when the parcels came in. the park was dedicated in 1958.';
  } else if (n === FIRST) {
    line += ' . just the first 31, bought in 1936. the rest is a rounding error on this grid.';
  } else if (n < FIRST) {
    line += ' . reset to start.';
  }
  readout.textContent = line;
}

document.getElementById('one').onclick = () => { nextFree(1); render(); };
document.getElementById('ten').onclick = () => { nextFree(10); render(); };
document.getElementById('rand').onclick = () => { randomFree(10); render(); };
document.getElementById('reset').onclick = () => reset();

// a click on a cell buys that cell (the cell handler runs first, then the grid render)


// click helper: simulate cell click
function clickCell(i){ cells[i].l.click(); }
build(); reset();
console.log('start', count(), readout.textContent);
clickCell(40); console.log('after click 40 owned?', owned[40], cells[40].className, readout.textContent);
document.getElementById; 
els['one'].onclick(); console.log('after next', count());
els['ten'].onclick(); console.log('after ten', count());
els['rand'].onclick(); console.log('after rand', count());
els['reset'].onclick(); console.log('reset', count(), readout.textContent);
nextFree(992); render(); console.log('full', count(), readout.textContent);
