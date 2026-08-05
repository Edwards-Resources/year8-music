# Next session

**Where things stand (5 August 2026):** The Year 8 site exists and builds. `python3 build.py` emits 27 pages into `docs/` from `data/`. All 25 Term 3 lessons are in as structured data, extracted from the Canvas block pages. The visual world is chosen, implemented, reviewed and documented in DESIGN.md. Nothing is committed to git yet and no GitHub repo exists.

**Term 3 is finished to the direction contract's own definition.** What remains is content Matthew has to choose (six lessons of repertoire), three more terms, and shipping it. See "What is outstanding".

One structural bug worth knowing about because it will recur: grid items default to `min-width:auto`, so a wide child (the tables carry a 34rem min-width) widens the whole column instead of scrolling inside its `overflow-x:auto` wrapper. Every lesson page with a table was sliding sideways on a phone until `min-width:0` was added to `.lesson-main`/`.tour-main`. If a new block type ever gets a min-width, check the phone.

## Decisions locked this session

- **Repo is `Sites/year8-music/`, no year in the name.** Matthew asked for it to be generic across cohorts. This deliberately differs from `year10-music-2026`. Recorded in PRODUCT.md.
- **No class codes anywhere**, in the site or the data schema. Class codes change every year.
- **No live position marker, ever.** Not a tracker, not a "current lesson" highlight. The classes run the same sequence at different speeds. `build.py` has no position logic at all and the build was checked for stray markers.
- **Every class uses GarageBand.** Ableton was only the online activities. Confirmed by Matthew, and the on-disk documents that contradicted it have now been corrected (see below).
- **Visual world: Tour Tee**, chosen after a re-roll. The first roll gave Rehearsal Marks (engraved score, ultramarine edition livery); Matthew saw a full sample of it and judged it not fun enough for Year 8, then steered for playful. Tour Tee is screenprinted band merch: the term is the tour, each lesson is a date on the back of the shirt. Black print fields, bone stock for reading, five loud spot inks one per leg. Seed key `b2cc7a19`.
  - The superseded Rehearsal Marks sample is still at `sample/index.html` if it is ever worth revisiting. It is not part of the build.

## What is outstanding

1. ~~**The impeccable finish review and DESIGN.md.**~~ **Done 5 August 2026. The review is closed and DESIGN.md exists.** Three fix rounds: eight material fixes, then the reviewer's verdict caught one overcorrection plus three regressions the batch introduced, then a third round of four finish items. Read DESIGN.md before touching the CSS; the rules there are earned, not decorative. Two in particular:
   - **One ink per lesson, three weights.** `--ink` is bound once per page by `.ink-*` on `article.lesson`. Hue never encodes block type, the weight of the treatment does: loud is the filled ink bar (`loud_block()` picks exactly one per lesson), quiet is the black top rule with a keylined label, and the encore is the one solid ink field. An earlier version colour-coded panels by block type; that was a fidelity failure and must not come back.
   - **`--plate`** is the overprint offset of the whole print field, an absolute length, not `em`. It belongs to the plate, not the glyph.
2. ~~**Two extraction bugs.**~~ **Fixed 5 August 2026.**
   - The heading loss was not the fold running in the wrong order. `body` filtered out every block type starting with `_`, which included `_heading`, so the fold below it was dead code. All three `<h3>` headings in the term were being lost, not just Lesson 2's: "Listening survey - five Australian artists" (L1), "The three grooves" (L2) and "The progressions" (L6, a table heading).
   - `is_track` now requires exactly one `" - "` separator, both sides filled, a left side under 40 characters and no sentence punctuation. `group_listening` also restarts the run on a fresh heading instead of dropping the block.
   - The data file was **patched, not overwritten**. `data/` carries hand edits the extractor does not reproduce: Lessons 19 and 20 had their `ASSESSMENT: ... (n%)` title prefix stripped and lifted into `assessed: true`. Re-running the extractor straight over the data file would destroy those. Diff first, apply only what changed.
3. **Content debt, confirmed: six lessons have unfilled media slots.** Lessons 8, 11, 13, 16, 22 and 23 carry placeholder items in the Canvas source written as "Piano ballad - video", "Artist A - video" and similar. `build.py` now detects these and renders an honest "Not added yet" panel instead of showing the placeholder text to students, but the real tracks still need choosing. This is Matthew's judgement call on repertoire, and it ties to the Australian-artist focus already decided (Thelma Plum, Eastern Rosellas chosen; Odesza swap still open).
4. **Terms 1, 2 and 4 do not exist yet.** Only Term 3 (Popular Music) is built. Term 4 is Film Soundtrack, Term 1 Piano, Term 2 Guitar, in that build order. Their material is the previous cohort's, in `Year 8 (2026)/Archive (pre-2026)/`, and needs rebuilding rather than porting.
5. **No git, no GitHub repo, nothing deployed.** Needs `git init`, a repo under `Edwards-Resources`, and Pages pointed at `/docs`. Ask Matthew before creating the repo; he does not want repos created autonomously.

## The GarageBand correction, now made

**Done 5 August 2026, on Matthew's instruction.** `Year 8 (2026)/Year 8 Music Course Reference.md` used to say students build their track "in GarageBand on iPads (8MUG and 8MUU) or Ableton (8MUP)". It now says all three classes use GarageBand and no class composes in Ableton.

The worksheets are what caused the confusion, so the folder inventory in that file now explains them: `Y8_Term3_AbletonMakingBeatsWorksheet.docx` and the two `AbletonNotesAndScales` sheets are **cover lessons** built on `learningmusic.ableton.com`, Ableton's free browser site, with no DAW involved. The `_8MUP` and `_8MUG` suffixes are a pre-filled class name field on an otherwise identical worksheet, not different tools. `Sites/NEXT-SESSION.md` carried the same wrong claim and was corrected too.

Left alone deliberately: the Ableton mentions in `00 Planner/Master To Do.md` and the dashboard are accurate historical records of cover lessons that did run those worksheets.

## How to work on it

- `python3 build.py` regenerates `docs/` from `data/`. Never edit `docs/` by hand.
- Local preview: the symlink `<scratchpad>/serve/year8-music` points at `docs/`, and the `year8-music` entry in `School Master/.claude/launch.json` serves that folder. The site's base path is `/year8-music`, so the URL doubles it: `http://localhost:<port>/year8-music/year8-music/popular-music/`. **Both the symlink and the absolute scratchpad path inside `launch.json` are session-scoped and must be updated each session.** The port also has to move each time, because the previous session's server keeps holding the old one and `preview_stop` cannot stop another chat's server. Now on 8794 (was 8793, was 8765).
- **Preview pane warnings from this session:** `computer` scroll timed out once and wedged the renderer; screenshots after a JS scroll came back blank every time. Navigating directly to a URL and screenshotting the top of the page worked reliably. Do not trust a blank screenshot as evidence of a blank page; check the DOM.
- Port 8765 is held by another chat's stale `teaching-site` server and the launch config at the project root wins over one inside the site folder. That is why the `year8-music` entry was added to `School Master/.claude/launch.json`.

## Model and effort

**Sonnet, medium** for building Terms 4, 1 and 2 into the existing system, and for the six repertoire slots once Matthew has chosen tracks. Mechanical work against a settled schema and a documented design system.

**Opus, medium-high** only if the visual world needs to change again, or for a fresh finish review after a whole new term is built.

## Watch out for

- The world is committed and Matthew chose it after rejecting one alternative. Do not quietly soften it toward a conventional school-site look. The five spot inks, the black print fields and the tour-list form are the design, not decoration. It has now been through a finish review that specifically protected the flat straight-down tour list with no "you are here"; that is the thesis and nothing may soften it into cards or an accordion.
- **No kickers.** Eyebrow labels above headings were removed in review and are an absolute ban. Labels are stamp bars or keylined caps inside their own field.
- Black is used for print fields and mastheads only. The reading surfaces stay light, because the site is watched on a classroom projector in daylight first and read on a phone second. If a dark reading surface creeps in, that is a regression.
- Black type on every spot ink. That is both print-accurate and what passes contrast; white on the pink does not.
- Syllabus outcomes in the data were taken verbatim from `Syllabus Reference/Music 7-10 (2024)/NESA - music_7_10_2024 (S4).docx`. Do not reword them and do not add outcomes without a source.
- No school name, no school branding, `noindex`, and no student names, work or marks. Same product rules as the Year 10 site.
- The teacher master Canvas page is deliberately excluded from extraction and must never be published.
