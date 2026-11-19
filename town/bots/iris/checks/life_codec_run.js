// Runs a codec file (copied from a forum post, untrusted) in a vm sandbox.
// Usage: node life_codec_run.js CODEC.js BOARDS.json OUT.json
// BOARDS.json: [{"id": n, "cells": [index,...]}]. Writes {"id", "hash", "roundtrip", "decodeNull"}.
'use strict';
const fs = require('fs');
const vm = require('vm');
const [codecPath, boardsPath, outPath] = process.argv.slice(2);
const sandbox = { W: 120, H: 80, btoa, atob, Uint8Array, console };
vm.createContext(sandbox);
const api = vm.runInContext(fs.readFileSync(codecPath, 'utf8') + '\n;({ encodeBoard, decodeBoard })', sandbox);
const boards = JSON.parse(fs.readFileSync(boardsPath, 'utf8'));
const N = 120 * 80;
const out = boards.map(({ id, cells }) => {
  const g = new Uint8Array(N);
  for (const i of cells) g[i] = 1;
  const hash = api.encodeBoard(g);
  const back = api.decodeBoard(hash);
  let roundtrip = back !== null;
  if (back) for (let i = 0; i < N; i++) if (back[i] !== g[i]) { roundtrip = false; break; }
  return { id, hash, roundtrip, decodeNull: back === null };
});
fs.writeFileSync(outPath, JSON.stringify(out));
console.log('boards', out.length, 'roundtrip ok', out.filter(o => o.roundtrip).length);
