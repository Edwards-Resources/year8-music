# Next session

**Where things stand (6 August 2026):** Term 3 is built, reviewed, documented, **published and full of playable video**. Live at **https://edwards-resources.github.io/year8-music/**, public repo `Edwards-Resources/year8-music`, Pages on `main` `/docs`. 36 players across the term. `python3 build.py` emits 27 pages into `docs/` from `data/`.

Read **DESIGN.md before touching any CSS.** The rules in it were earned through a finish review, not invented.

## The next task

**Build Term 4, Film Soundtrack**, into the existing system. Then Term 1 (Piano), then Term 2 (Guitar), so the site is complete for the 2027 Year 8 intake.

The previous cohort's material is in `Year 8 (2026)/Archive (pre-2026)/Term 4 - Film and Video Games/`. It needs **rebuilding, not porting**: the registered program is the authority, and the archive is last year's teaching material rather than a source of truth.

Shape of the work: add `data/courses/year8-music/topics/film-soundtrack.json` following `popular-music.json`, add its id to `course.json`, rebuild. No CSS should be needed. **Media is now a solved problem** - use a `media` block for one instructional video, or `listen` tracks each carrying an `embed` for a run of repertoire.

## Model and effort

**Sonnet, medium.** The data schema, the design system and the media components are all settled and documented, so this is content assembly against a fixed structure.

Step up to **Opus, medium-high** only if the visual world needs to change, or for a fresh finish review once a whole new term is built.

## Also outstanding

1. **Thelma Plum has no video**, in Lessons 1 and 22. Matthew found that the "Better in Blak" video says the f-word. A clean release exists commercially but cannot be told apart from the explicit one on YouTube, so the slot is **deliberately open**. Needs a URL he has vetted, or a different song. **If she comes out entirely**, Lesson 1's prose line "Baker Boy, Thelma Plum and Jessica Mauboy are First Nations artists" must change, and the survey drops from three First Nations artists to two.
2. **Channel verified, lyrics not.** Every video id was checked through oEmbed to confirm it exists, embeds, and sits on an official artist or label channel. That says nothing about content. Matthew should listen before teaching from any of them.
3. **DoE external-publishing policy** still unverified, same open question as the Year 10 site.

## How to work on it

- `python3 build.py` regenerates `docs/` from `data/`. **Never edit `docs/` by hand**; it is wiped and rewritten every build.
- **Verify every YouTube id before shipping it.** The oEmbed endpoint returns the real title and channel:
  `https://www.youtube.com/oembed?url=<url-encoded watch url>&format=json`
  This is not ceremony. On 6 August it caught a Love Story id that 404'd and a Sunday Morning result that was a personal re-upload rather than Maroon5VEVO. Search result titles lie.
- **`data/` is reviewed output, not extractor output.** Lessons 19 and 20 carry hand edits: the `ASSESSMENT: ... (10%)` title prefix was stripped and lifted into `assessed: true`. Re-running `tools/extract_canvas.py` straight over the data file would silently revert them. Diff first.
- **The repo is public, so every commit is public** and history is permanent. Grep any new file for the school name before committing. **Ask Matthew before pushing.**
- Local preview: symlink a scratchpad `serve/year8-music` at `docs/`, and point the `year8-music` entry in `School Master/.claude/launch.json` at it. **Both the symlink and the absolute path in that launch config are session-scoped and must be updated each session**, and the port has to move each time because the previous session's server holds the old one. Currently 8796 (was 8795, 8794, 8793, 8765). The base path is doubled in the URL: `http://localhost:<port>/year8-music/year8-music/popular-music/`.
- **The preview proxy caches `site.css` hard.** After a CSS change the page can render with the old stylesheet and look broken. Re-inject it to check the real result:
  `document.querySelector('link[rel=stylesheet]').href += '?v=' + Date.now()`

## Watch out for

- **No live position marker, ever.** Not a tracker, not a current-lesson highlight, not a progress bar. The classes run the same sequence at different speeds, so any position claim is wrong for most of them. `build.py` has no position logic and it must stay that way. This outranks every visual rule in DESIGN.md.
- **Placeholders only look like placeholders if they follow the convention.** The `- video` guard originally ran on `listen` blocks only, so eight prose placeholders printed to students as teaching copy. Fixing that still missed four more that never used the suffix at all ("Setup walkthrough video", three "reference track" lines). A guard written for one block type is not a guard on the data. **Grep the built `docs/` for stray note-to-self text, do not trust the guard.**
- **One ink per lesson, three weights.** `--ink` binds once per page from the leg. Hue never encodes block type. `loud_block()` picks exactly one loud field per lesson and now skips placeholders so an empty slot can never take the ink. A player never takes it either; the task keeps it.
- **No kickers.** Eyebrow labels above headings are an absolute ban.
- **Reading surfaces stay light.** The one Print Black field that is not a print field is the video well, which is the letterbox behind the player. That exception is documented in DESIGN.md; do not widen it.
- **Black type on every spot ink.** White on the pink fails contrast.
- **Grid and flex parents need `min-width:0`** if a child can be wider than the column. The tables carry a 34rem min-width and `.clip` carries `min-width:0` for the same reason. Without it the page slides sideways on a phone instead of the table or player behaving.
- The design hook reports one finding, `#000` in `assets/site.css`. It is a **known false positive**: the opaque stop of the halftone's `mask-image` gradient, where only the alpha channel is read. Do not "fix" it and do not suppress it without asking Matthew.
- Syllabus outcomes were taken verbatim from `Syllabus Reference/Music 7-10 (2024)/NESA - music_7_10_2024 (S4).docx`. Do not reword them and do not add outcomes without a source.
- The teacher master Canvas page is excluded from extraction and must never be published.
- `sample/` holds the **rejected** Rehearsal Marks world. It is an anti-reference, not a starting point.

## Last commit

```
859ff53 Fill the remaining media slots, and fix four more placeholder leaks
```

Pushed to `origin/main`.
