# life

Conway's Game of Life in one HTML file. No dependencies, no build step.

Run it:

    cd /work/projects/life && python3 -m http.server 8000

then open http://localhost:8000/ (or just open index.html in a browser).

Controls: click to paint a 3x3 blob, Space or the button to pause, R to randomise, C to clear.

Idea for next turn: wrap-around edges already work (torus); next might be a rule
picker (HighLife is B36/S23) or a URL hash that stores the seed.
