# Next session

**Where things stand (6 August 2026):** Term 3 and Term 4 are both built, reviewed, published and full of playable video. Live at **https://edwards-resources.github.io/year8-music/**, public repo `Edwards-Resources/year8-music`, Pages on `main` `/docs`. 53 pages, 62 video players across the two terms. `python3 build.py` emits from `data/` into `docs/`.

**Popular Music was revised on 6 August 2026** against Matthew's per-lesson notes: worksheet tables are now typeable, Lesson 9 gained a beat-grid diagram, Lessons 11, 13, 16 and 18 changed repertoire, and Flume and Thelma Plum are out of the term entirely. See "The Flume lesson" below - it is the important one.

## The Flume lesson

Flume's "Never Be Like You" was embedded in **four** lessons (1, 11, 13, 23), live and public, because it had passed the oEmbed channel check: FlumeVEVO, official, exists, embeds. The channel check cannot see lyrics, and the track has an explicit original.

**Apple's catalogue flag is the check that catches this**, and it is cheap:

```
https://itunes.apple.com/search?term=<artist+title>&media=music&entity=song&limit=25&country=AU
```

Read `trackExplicitness` on each result. `explicit` is obvious; **`cleaned` is the one that matters** - it means the listing is an edited version, so an explicit original exists, and a YouTube upload of "the song" is as likely to be that original as not. Flume returned `cleaned`. Every other track in the term returned `notExplicit`.

Run this on any new track **before** the oEmbed check, not after. oEmbed proves the upload is real; the Apple flag is the only programmatic signal about what is in it. Neither replaces Matthew's ear, but between them they would have kept this off the site.

Read **DESIGN.md before touching any CSS.** The rules in it were earned through a finish review, not invented.

## The next task

**Build Term 1 (Piano)**, then Term 2 (Guitar), into the existing system, so the site is complete for the 2027 Year 8 intake.

The previous cohort's material is in `Year 8 (2026)/Archive (pre-2026)/`. It needs **rebuilding, not porting**: the registered program in `Year 8 (2026)/Program and Assessment/` is the authority, and the archive is last year's teaching material rather than a source of truth. This is how Term 4 was built - the archive folder for it was barely used; the program document supplied the real lesson sequence.

Shape of the work: add `data/courses/year8-music/topics/piano.json` (or similar id) following `popular-music.json` and `film-soundtrack.json`, add its id to `course.json`, rebuild. No CSS should be needed. Media is a solved problem - use a `media` block for one instructional video, or `listen` tracks each carrying an `embed` for a run of repertoire.

## Model and effort

**Sonnet, medium.** The data schema, the design system and the media components are all settled and documented, so this is content assembly against a fixed structure.

Step up to **Opus, medium-high** only if the visual world needs to change, or for a fresh finish review once the whole year is built.

## Also outstanding

1. ~~Thelma Plum has no video~~ **Closed 6 August 2026.** She is out of the term entirely, replaced by Miles Phillips' "Eastern Rosellas" in Lessons 1 and 22, which the term already used in Lesson 6 as the I-IV-V example. Lesson 1's prose now reads "Baker Boy and Jessica Mauboy are First Nations artists" and the survey carries two rather than three. Popular Music has no unfilled media slots left.
2. **King Kong (1933) has no video**, in Film Soundtrack Lesson 7. No clean official YouTube upload was found on 6 August - only fan re-uploads - so the slot is deliberately left as a title-only gap rather than risking a mislabelled or unofficial source. Revisit if Matthew finds a channel he trusts.
3. **Channel verified, lyrics not.** Every video id across both terms was checked through oEmbed to confirm it exists, embeds, and sits on an official or clearly legitimate channel. That says nothing about content. Matthew should listen before teaching from any of them.
4. **Tame Impala is deliberately the Official Audio**, not the music video, in Lesson 11. The lyrics are fine; the official video has sexual content and blood in it. If anyone "fixes" that id to the video, the lesson becomes unteachable. The same trap applies to any track chosen for its bass line rather than its clip.
5. **Silverchair's "Israel's Son"** (Lesson 11) has no explicit language but violent lyric content, kept with Matthew's knowledge. Flagged here so it is not quietly dropped by a later session that assumes it was an oversight.
6. **DoE external-publishing policy** still unverified, same open question as the Year 10 site.

## How to work on it

- `python3 build.py` regenerates `docs/` from `data/`. **Never edit `docs/` by hand**; it is wiped and rewritten every build.
- **Verify every YouTube id before shipping it.** The oEmbed endpoint returns the real title and channel:
  `https://www.youtube.com/oembed?url=<url-encoded watch url>&format=json`
  This is not ceremony. It has caught dead ids, a personal re-upload masquerading as an official video, and - while building Term 4 - several fan channels that looked plausible for game and film themes but weren't the composer's or studio's own upload (King Kong 1933, Halo, Super Mario Bros, Zelda). When no clean official source turns up, leave the track title-only rather than embed an unverified one.
- **`data/` is reviewed output, not extractor output.** Popular Music's Lessons 19 and 20 carry hand edits: the `ASSESSMENT: ... (10%)` title prefix was stripped and lifted into `assessed: true`. Re-running `tools/extract_canvas.py` straight over that data file would silently revert them. Diff first. Film Soundtrack was written directly from the registered program rather than extracted from Canvas, since no Canvas course existed yet for that term.
- **The repo is public, so every commit is public** and history is permanent. Grep any new file for the school name before committing. **Ask Matthew before pushing.**
- Local preview: the dev server config lives in the **top-level `School Master/.claude/launch.json`** (not the one inside this site folder, which is not what the preview tool actually reads), under the `year8-music` entry. It points at a scratchpad `serve/year8-music` symlink into `docs/`. **Both the symlink and the absolute scratchpad path in that launch config are session-scoped and must be updated each session**, and the port has to move each time because the previous session's server holds the old one. Currently 8799 (was 8798, 8797, 8796, 8795, 8794, 8793, 8765). The base path is doubled in the URL: `http://localhost:<port>/year8-music/year8-music/popular-music/`.
- **The preview proxy caches `site.css` hard.** After a CSS change the page can render with the old stylesheet and look broken. Re-inject it to check the real result:
  `document.querySelector('link[rel=stylesheet]').href += '?v=' + Date.now()`

## Watch out for

- **No live position marker, ever.** Not a tracker, not a current-lesson highlight, not a progress bar. The classes run the same sequence at different speeds, so any position claim is wrong for most of them. `build.py` has no position logic and it must stay that way. This outranks every visual rule in DESIGN.md.
- **Placeholders only look like placeholders if they follow the convention.** The `- video` / `- audio` guard checks untitled prose and listen tracks the same way. A track with a real title but no `embed` key just renders as a plain tick list (teacher plays it live) rather than an "unfilled" panel - that's the deliberate King Kong/Mario/Zelda/Halo pattern from Term 4, not a bug. **Grep the built `docs/` for stray note-to-self text, do not trust the guard alone.**
- **One ink per lesson, three weights.** `--ink` binds once per page from the leg. Hue never encodes block type. `loud_block()` picks exactly one loud field per lesson and skips placeholders so an empty slot can never take the ink. A player never takes it either; the task keeps it.
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
b46e5f5 Popular Music: typeable tables, a beat grid, and safer repertoire
```

Pushed to `origin/main` on 6 August 2026, so the revisions - including the Flume removal - are live.
