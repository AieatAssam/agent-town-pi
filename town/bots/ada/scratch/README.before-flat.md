# life

Conway's Game of Life in one HTML file. No dependencies, no build step.

Run it:

    cd /work/projects/life && python3 -m http.server 8000

then open http://localhost:8000/ (or just open index.html in a browser).

Controls: click to paint a single cell, shift-click for a 3x3 blob, Space or the button to pause, R to randomise, C to clear,
H or the rule button to switch between Life (B3/S23) and HighLife (B36/S23).

Wrap-around edges work (torus). Rules are a small table at the top of the script,
so adding one is a single line.

## Sharing a board (URL hash)

The board is in the URL after `#`. Format v1:

- `v1b` + 1600 base64url characters: a 1200-byte bitmap, MSB first, row-major.
- `v1r` + runs `skip.count,skip.count,...`: live cells as runs, row-major, where skip counts empty cells after the previous run.

The encoder writes whichever is shorter (a 2% random board is ~850 characters; a 30% board is 1603).
The decoder refuses anything malformed and leaves the board alone.

- The hash is written when you edit, randomise, clear, or pause. It is not written every tick.
  So while the board runs, the link shows the board at the last of those, not the current one.
- The rule (Life or HighLife) is not in the link.
- Pasting a new `#...` into the address bar loads that board.

Tests for the codec: `node test_codec.js` (round-trips and malformed hashes).
