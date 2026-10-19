# Augsburgami — maintainable static site trial

This is a **test build**, not a replacement for the live site. It starts with the existing Augsburgami HTML and its 822 game records.

## Files

- `index.html` — the generated site. Upload this file to GitHub Pages to publish; it needs no JavaScript.
- `games.csv` — the **only file to edit** when adding games or correcting scores. One game per row.
- `build_augsburgami.py` — rebuilds the site from the CSV and template.
- `augsburgami_template.html` — the existing site's visual and structural reference. Keep this file; do not edit it for routine game updates.

## Updating Augsburgami

1. Open `games.csv` in a spreadsheet editor or text editor. Add a row with `date,augsburg_score,opponent_score,matchup`, e.g. `10/24/2026,31,18,Opponent @ Augsburg`. Use `MM/DD/YYYY` dates.
2. Install Python 3 and Beautiful Soup once: `python3 -m pip install beautifulsoup4`.
3. Run `python3 build_augsburgami.py` in this directory.
4. Preview the generated `index.html` in a browser. Check the new score's matrix square and results panel.
5. Upload the generated `index.html` to GitHub Pages.

The generator treats 27–17 and 17–27 as **one square**, while showing both Augsburg-first orientations in the same result panel. It regenerates the radio controls, clickable squares, CSS navigation selectors, and score result panels. It also checks that the number of game rows and clickable squares match the CSV.

## Important limitations

- This is a static HTML/CSS generator, not browser-side JavaScript. Python runs **before publishing**, not on GitHub Pages.
- The existing matrix dimensions are retained. If a future score exceeds its row/column limits, the build stops with an explanatory error; a developer must expand the template matrix.
- The `games.csv` was extracted from the supplied inspectable HTML to preserve its existing displayed records. It is **not a fresh historical audit**.
- Keep the live GitHub Pages `index.html` untouched until you have tested this generated version, ideally on a separate branch or test repository.
