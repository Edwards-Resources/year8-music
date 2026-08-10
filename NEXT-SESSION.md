# Next session

**Where things stand (10 August 2026):** Terms 1, 3 and 4 are built. Term 2 Guitar is the only gap. Live at **https://edwards-resources.github.io/year8-music/**, public repo `Edwards-Resources/year8-music`, Pages on `main` `/docs`. 79 pages, 77 video players across the three terms. `python3 build.py` emits from `data/` into `docs/`.

**Term 1 Keyboard was built 10 August 2026** and is committed but **not pushed** - Matthew had not been asked yet. `keyboard.json`, 25 lessons, 15 verified video slots, key-word tables at 5, 10, 15, 20 and the registered unit vocabulary as the Lesson 25 glossary. It sits first in `course.json`, so the home page now opens on Term 1. See "Three things Term 1 turned up" below before building Term 2.

**Popular Music was revised on 6 August 2026** against Matthew's per-lesson notes: worksheet tables are now typeable, Lesson 9 gained a beat-grid diagram, Lessons 11, 13, 16 and 18 changed repertoire, and Flume and Thelma Plum are out of the term entirely. See "The Flume lesson" below - it is the important one.

**Key-word tables added 7 August 2026.** Ten of them, matching the fill-in tables built on the Year 10 site the same day: one at the end of each section listing that section's key words with a blank beside each, plus a whole-term glossary in each Wrap-Up lesson (both Lesson 25s). They are ordinary `table` blocks with headers `["Key word", "What it means"]` and an empty second cell, so they inherit the existing fillable-table behaviour and per-lesson saving. **No table lists a word the page it sits on defines** - the answer must never sit above the blank - and the build script asserts this rather than trusting the author. Sections that teach only one or two new words carry earlier words forward.

Year 10's per-table **Clear** button was deliberately not ported: Year 8 has no equivalent, and adding one touches all 45 tables and the finish-reviewed design system. Worth doing as its own task if the two sites should match.

## The Flume lesson

Flume's "Never Be Like You" was embedded in **four** lessons (1, 11, 13, 23), live and public, because it had passed the oEmbed channel check: FlumeVEVO, official, exists, embeds. The channel check cannot see lyrics, and the track has an explicit original.

**Apple's catalogue flag is the check that catches this**, and it is cheap:

```
https://itunes.apple.com/search?term=<artist+title>&media=music&entity=song&limit=25&country=AU
```

Read `trackExplicitness` on each result. `explicit` is obvious; **`cleaned` is the one that matters** - it means the listing is an edited version, so an explicit original exists, and a YouTube upload of "the song" is as likely to be that original as not. Flume returned `cleaned`. Every other track in the term returned `notExplicit`.

Run this on any new track **before** the oEmbed check, not after. oEmbed proves the upload is real; the Apple flag is the only programmatic signal about what is in it. Neither replaces Matthew's ear, but between them they would have kept this off the site.

Read **DESIGN.md before touching any CSS.** The rules in it were earned through a finish review, not invented.

## Deployed, and how it nearly wasn't

The 6 August revisions are **live and verified against the live URL** as at 7 August 2026, 07:54 AEST. Flume and Thelma Plum return zero hits across all 25 lesson pages.

Getting there took eleven hours, for a reason worth not repeating. Five commits went out across four pushes in about ten minutes. Each push triggers its own Pages deployment, they collided (`Deployment request failed... due to in progress deployment`), and retrying with `gh run rerun` wedged run 31102698316 in a state GitHub could not clear: it reported `queued` while force-cancel returned `409 Cannot cancel a workflow re-run that has not yet queued` and plain cancel claimed it was already completed. That run held the deployment lock, so a fresh build request and a clean push each sat through the 10-minute timeout and aborted.

**What actually cleared it:** toggling the Pages publishing source in the web UI - Settings, Pages, Build and deployment, folder `/docs` to `/ (root)`, Save, then straight back to `/docs`, Save. That fires new deployments outside the jammed queue. It has to be done in the UI; the equivalent `gh api --method PUT .../pages` call is blocked as a repo-settings write. Set it back to `/docs` or the site 404s, since there is no `index.html` at the repo root.

**Two rules this earned:**

- **Verify the deployment, not the push.** A green `git push` proves the code reached GitHub and nothing else. The only honest check is fetching the live URL and looking for something that exists only in the new build:
  ```bash
  curl -s "https://edwards-resources.github.io/year8-music/year8-music/popular-music/lesson-11/" | grep -c 'class="fill"'
  ```
  This was reported to Matthew as live when it was not, and he found it by opening the page.
- **Batch handoff edits into one commit.** One push, one deployment, no collision. Committing each documentation tweak separately is free on an ordinary repo and is not free on a Pages repo.

## First, a five-minute job

**Popular Music Lesson 13 needs Matthew's ear on one track.** He asked for The Easybeats' "Friday On My Mind" as the vocal-riff example, for a "na na na na" section. No such section could be located - the famous hook in that song is the guitar riff - so it went in as asked and was flagged rather than swapped or quietly left wrong. If he names a different song, swap the track and its `Vocal riff - ` title prefix in `popular-music.json` Lesson 13 and rebuild. Nothing else depends on it.

## Three things Term 1 turned up

Read these before Term 2. All three are about the source documents, not the site.

1. **The unit is called Keyboard on the site, not Piano.** This file and PRODUCT.md both said "Term 1 Piano", which came from the archive folder name. The registered program says keyboard everywhere, the classroom instruments are keyboards, and the task is "Keyboard Skills". The program is the authority, so the topic id is `keyboard` and the name is Keyboard, with the registered unit title "The Keys to Success" as the subtitle. **Matthew has not confirmed this** - if he prefers Piano, rename the id, the folder under `docs/` will follow on rebuild, and fix the pointer in `course.json`.

2. **Two documents name different repertoire.** The program teaches Hot Cross Buns from the Beats & Tunes booklet. The Semester 1 task overview names "Morning" from Peer Gynt and Ode to Joy as the assessment melodies. Both are now on the site and neither was dropped: Hot Cross Buns is the teaching melody at Lessons 4 and 9, Ode to Joy arrives at Lesson 11 and Morning Mood at Lesson 16, so students choose between the two assessment pieces with six lessons left. Worth Matthew reconciling the two documents even so.

3. **The Week 8 due date and the lesson sequence disagree by about a lesson.** The schedule says the task is due Week 8 of Term 1. The program's own sequence puts the Keyboard Skills Test at Lesson 21, and at 2.5 lessons a week that lands early in Week 9. The site says "Due Week 8" because the registered schedule is the authority, and the assessed flag sits on Lessons 21 and 22 because the program's sequence is. Not resolvable from the documents.

Also worth knowing: **`build.py` does not assert the key-word rule**, despite what this file said on 7 August. It was checked by hand for Term 3 and Term 4, and by a throwaway script for Term 1. Do the same for Term 2, or add the assert properly.

## The next task

**Build Term 2 (Guitar)**, and the site is complete for the 2027 Year 8 intake.

The registered program is `Year 8 (2026)/Program and Assessment/Year 8 Music Term 2.docx`, unit title "Striking the Right Chord". It runs guitar performance alongside tone colour as the listening strand: string names and single-string riffs, then multi-string riffs, then open chords and strumming, orchestral families and world instruments, a Week 7 performance and listening assessment, and a three-week band project to finish. It has a full 25-lesson learning-experience table, same shape as Term 1's.

**Its header block is wrong in the source document** and should not be copied: it says YEAR 12 and UNIT LENGTH 4 TERMS, both left over from whatever it was pasted from. It is a Year 8, one-term unit. Tell Matthew; the .docx wants fixing, not just the site.

The previous cohort's material is in `Year 8 (2026)/Archive (pre-2026)/Term 2 - Guitar/`, including a guitar booklet PDF. It needs **rebuilding, not porting**: the registered program is the authority and the archive is last year's teaching material. Term 1 and Term 4 were both built this way and the archive was barely opened.

Shape of the work: add `data/courses/year8-music/topics/guitar.json` following `keyboard.json`, which is the closest model since both are skills-and-repertoire units, add its id to `course.json` between `keyboard` and `popular-music`, rebuild. No CSS needed. Term 2 wants more `listen` blocks than Term 1 did, because tone colour is half the unit: orchestral families, then world instruments (djembe, gamelan, sitar, shamisen, balafon are the ones the program names).

**Tone colour is taught again in Term 3 Lesson 18.** Check what `popular-music.json` already says about it so the two terms agree rather than defining it twice, differently.

## Model and effort

**Sonnet, medium.** The data schema, the design system and the media components are all settled and documented, so this is content assembly against a fixed structure.

Step up to **Opus, medium-high** only if the visual world needs to change, or for a fresh finish review once the whole year is built.

## Also outstanding

1. ~~Thelma Plum has no video~~ **Closed 6 August 2026.** She is out of the term entirely, replaced by Miles Phillips' "Eastern Rosellas" in Lessons 1 and 22, which the term already used in Lesson 6 as the I-IV-V example. Lesson 1's prose now reads "Baker Boy and Jessica Mauboy are First Nations artists" and the survey carries two rather than three. Popular Music has no unfilled media slots left.
2. **King Kong (1933) has no video**, in Film Soundtrack Lesson 7. No clean official YouTube upload was found on 6 August - only fan re-uploads - so the slot is deliberately left as a title-only gap rather than risking a mislabelled or unofficial source. Revisit if Matthew finds a channel he trusts.
3. **Channel verified, lyrics not.** Every video id across both terms was checked through oEmbed to confirm it exists, embeds, and sits on an official or clearly legitimate channel. That says nothing about content. Matthew should listen before teaching from any of them.
4. **Tame Impala is deliberately the Official Audio**, not the music video, in Lesson 11. The lyrics are fine; the official video has sexual content and blood in it. If anyone "fixes" that id to the video, the lesson becomes unteachable. The same trap applies to any track chosen for its bass line rather than its clip.
5. **Silverchair's "Israel's Son"** (Lesson 11) has no explicit language but violent lyric content, kept with Matthew's knowledge. Flagged here so it is not quietly dropped by a later session that assumes it was an oversight.
6. **Ads on the embedded videos.** Matthew has YouTube Premium and still gets an ad every time. Almost certainly because the embeds go through `youtube-nocookie.com`, a separate domain from `youtube.com`, so his login cookies are never sent and the player treats him as signed out. No URL parameter disables ads; an authenticated Premium session is the only mechanism.

   **Do not "fix" this by swapping the embed domain.** `youtube-nocookie.com` is there so students are not tracked on every lesson page, and changing it trades their privacy for one teacher's ad-free playback - and may not even work, since Chrome and Safari restrict the third-party cookies a `youtube.com` embed depends on. Better: clicking the video title in the player's top bar already opens it on YouTube signed in, or add a small "Open on YouTube" link under each player. Diagnose first by loading `https://www.youtube-nocookie.com/embed/2SUwOgmvzK4` and `https://www.youtube.com/embed/2SUwOgmvzK4` in his teaching browser; if both show ads, cookie blocking is defeating it and no site change will help. Raised 7 August 2026, deferred - "it's fine for now".
7. **DoE external-publishing policy** still unverified, same open question as the Year 10 site.

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
- **Two-column tables are the exception to the 34rem floor.** The floor exists so a four-column worksheet is not crushed; a two-column table has nothing to crush, so `build.py` tags it `is-narrow` and it drops to 19rem, fits a phone, and loses the swipe hint. 28 of the site's 45 tables are two-column. If a table ever gains a third column it picks the floor and the hint back up automatically. **Do not hardcode the hint back on**: a table that no longer clips must not tell a student to slide it.
- The design hook reports one finding, `#000` in `assets/site.css`. It is a **known false positive**: the opaque stop of the halftone's `mask-image` gradient, where only the alpha channel is read. Do not "fix" it and do not suppress it without asking Matthew.
- Syllabus outcomes were taken verbatim from `Syllabus Reference/Music 7-10 (2024)/NESA - music_7_10_2024 (S4).docx`. Do not reword them and do not add outcomes without a source.
- The teacher master Canvas page is excluded from extraction and must never be published.
- `sample/` holds the **rejected** Rehearsal Marks world. It is an anti-reference, not a starting point.

## Last commit

```
9298d24 Build Term 1 Keyboard, 25 lessons
```

**Committed on 10 August 2026 and not pushed.** Matthew has not been asked yet, and this repo is public, so nothing goes out without him saying so. Once it is pushed, verify the deployment rather than the push:

```bash
curl -s "https://edwards-resources.github.io/year8-music/year8-music/keyboard/lesson-12/" | grep -c 'thumb tucks under'
```
