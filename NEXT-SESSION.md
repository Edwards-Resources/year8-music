# Next session

**Where things stand (6 August 2026):** Term 3 is finished to the direction contract's own definition: built, reviewed over three rounds, documented in DESIGN.md, and committed. `python3 build.py` emits 27 pages into `docs/` from `data/`.

**Published 6 August 2026.** Public repo at https://github.com/Edwards-Resources/year8-music, Pages serving `main` `/docs` at **https://edwards-resources.github.io/year8-music/**. Verified live: fonts, spot ink and base paths all resolve on the real host, no console errors. The repo name is load-bearing, because the site's base path is hard-coded `/year8-music/`; renaming the repo breaks every link. Matthew chose to publish the full working history and to keep the direction-contract HTML comment in the built pages, matching the Year 10 site.

**Anonymity now covers the repo, not just the site.** The Year 10 repo's README and PRODUCT.md had named the school and Matthew in full while the built site was clean; Matthew confirmed on 6 August 2026 that the school name goes nowhere at all. Both files were corrected there and the rule in `year10-music-2026/PRODUCT.md` was rewritten to cover internal planning files too. Year 8's own files were checked and were already clean. **Grep any new file for the school name before committing it.**

Read **DESIGN.md before touching any CSS.** The rules in it were earned through a finish review, not invented.

## The next task

**Build Term 4, Film Soundtrack**, into the existing system. Then Term 1 (Piano), then Term 2 (Guitar), in that order, so the site is complete for the 2027 Year 8 intake.

The previous cohort's material is in `Year 8 (2026)/Archive (pre-2026)/Term 4 - Film and Video Games/`. It needs **rebuilding, not porting**: the registered program is the authority, and the archive is last year's teaching material rather than a source of truth.

Shape of the work: add `data/courses/year8-music/topics/film-soundtrack.json` following `popular-music.json` exactly, add its id to `course.json`, rebuild. No CSS should be needed. If a new block type is genuinely required, add it to `block_html()` and record it in DESIGN.md, but check first whether an existing type covers it.

## Model and effort

**Sonnet, medium.** The data schema and the design system are both settled and documented, so this is content assembly against a fixed structure rather than design work.

Step up to **Opus, medium-high** only if the visual world needs to change, or for a fresh finish review once a whole new term is built.

## Also outstanding

1. **Six lessons have unfilled media slots:** 8, 11, 13, 16, 22 and 23. The Canvas source carries placeholders written as "Piano ballad - video"; `build.py` detects these and renders an honest "Not added yet" panel rather than showing placeholder text to students. Choosing the tracks is Matthew's call and ties to the Australian-artist focus (Thelma Plum and Eastern Rosellas chosen; the Odesza swap still open).
2. **The site is now public, so every commit is public.** Pushing is no longer a private act: anything committed from here is visible immediately and stays in history even if a later commit removes it. Still **ask Matthew before pushing**.
3. **DoE external-publishing policy** still unverified, same open question as the Year 10 site.

## How to work on it

- `python3 build.py` regenerates `docs/` from `data/`. **Never edit `docs/` by hand**; it is wiped and rewritten every build.
- **`data/` is reviewed output, not extractor output.** Lessons 19 and 20 carry hand edits: the `ASSESSMENT: ... (10%)` title prefix was stripped and lifted into `assessed: true`, which the build renders as a badge. Re-running `tools/extract_canvas.py` straight over the data file would silently revert them. Diff first, apply only what changed.
- Local preview: symlink a scratchpad `serve/year8-music` at `docs/`, and point the `year8-music` entry in `School Master/.claude/launch.json` at it. **Both the symlink and the absolute path inside that launch config are session-scoped and must be updated each session**, and the port has to move each time because the previous session's server keeps holding the old one and `preview_stop` cannot stop another chat's server. Currently 8794 (was 8793, was 8765). The base path is doubled in the URL: `http://localhost:<port>/year8-music/year8-music/popular-music/`.
- Screenshots for any review must be driven over CDP with `Emulation.setDeviceMetricsOverride`. Chrome's `--window-size` plus `--screenshot` lays out at a default width and then crops to the window, which fakes mobile overflow convincingly. There is a working `shoot.mjs` pattern in this session's history.

## Watch out for

- **No live position marker, ever.** Not a tracker, not a current-lesson highlight, not a progress bar, not a most-recent badge. The classes run the same sequence at different speeds, so any position claim is wrong for most of them. `build.py` has no position logic and it must stay that way. This outranks every visual rule in DESIGN.md.
- **One ink per lesson, three weights.** `--ink` binds once per page from the leg. Hue never encodes block type; the weight of the treatment does. Loud is the filled ink bar and `loud_block()` picks exactly one per lesson. Quiet is the black top rule with a keylined label. The encore is the one solid ink field. An earlier version colour-coded panels by block type and the review called it a fidelity failure; it must not come back.
- **No kickers.** Eyebrow labels above headings are an absolute ban, removed in review. Labels are stamp bars or keylined caps inside their own field.
- **Reading surfaces stay light.** Black is for print fields and mastheads only, because the primary screen is a projector in a daylit classroom. A dark reading surface is a regression.
- **Black type on every spot ink.** Print-accurate and the only thing that passes contrast; white on the pink fails.
- **Grid and flex parents need `min-width:0`** if a child can be wider than the column. The tables carry a 34rem min-width, and without it the whole page slides sideways on a phone instead of the table scrolling in its wrapper. This bit once already.
- The design hook reports one finding, `#000` in `assets/site.css`. It is a **known false positive**: the opaque stop of the halftone's `mask-image` gradient, where only the alpha channel is read. DESIGN.md documents it as an alpha derivative deliberately kept out of the palette. Do not "fix" it and do not suppress it without asking Matthew.
- Syllabus outcomes in the data were taken verbatim from `Syllabus Reference/Music 7-10 (2024)/NESA - music_7_10_2024 (S4).docx`. Do not reword them and do not add outcomes without a source.
- The teacher master Canvas page is excluded from extraction and must never be published.
- `sample/` holds the **rejected** Rehearsal Marks world from the first direction roll. It is an anti-reference, not a starting point, and is not part of the build.

## Last commit

```
9501dff Add README and refresh build date stamp
```

Pushed to `origin/main`.
