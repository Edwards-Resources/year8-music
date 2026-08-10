# Next session

**Where things stand:** All four terms are now built - Keyboard, Guitar, Popular Music, Film Soundtrack - 100 lesson pages plus 4 term indexes and the home page, 105 pages total. **Term 2 Guitar was built and committed today (10 August 2026) but is not pushed** - Matthew has not been asked yet. `guitar.json`, 25 lessons, 20 registered vocabulary terms taught and glossaried, 22 verified video slots (riff/chord tutorials from Andy Guitar and JustinGuitar, orchestral families from Philharmonia Orchestra, world instruments from named performers/institutions). Registered in `course.json` between `keyboard` and `popular-music`. The 2027 Year 8 intake site is content-complete.

**Next task:** Get Matthew's sign-off to push. On push, verify against the **live URL**, not the push (see "Deployed, and how it nearly wasn't" in git history / prior commits for why - batch into one commit, one push). Then tell Matthew two things outside the site itself:
1. The Term 2 program docx (`Year 8 (2026)/Program and Assessment/Year 8 Music Term 2.docx`) has a wrong header block - says YEAR 12 and UNIT LENGTH 4 TERMS, leftover from whatever it was pasted from. It's a Year 8, one-term unit. The docx wants fixing, not just the site.
2. Whether the unit should stay named "Guitar" - the docx itself titles it "Striking the Right Chord" with no ambiguity like Term 1's Piano/Keyboard question, so this one is low-risk, but confirm anyway.

**Model/effort recommendation:** Sonnet, low-medium for the push/verify/handoff step - mechanical. Step up to Opus, medium if Matthew wants a finish review now that all four terms exist, since that's a cross-term consistency judgement call, not content assembly.

**Watch out for:**
- **Local preview is session-scoped.** The dev server config lives in the **top-level `School Master/.claude/launch.json`**, `year8-music` entry. It points at a scratchpad `serve/year8-music` symlink into `docs/`. Both the symlink and the absolute scratchpad path must be recreated each session, and the port has to move each time (currently 8803, was 8802, 8801...8793, 8765) because the previous session's server holds the old one.
- **The repo is public** (`Edwards-Resources/year8-music`), so every commit is public and history is permanent. Grep any new file for the school name before committing. **Ask Matthew before pushing**, always.
- **Never edit `docs/` by hand** - `python3 build.py` wipes and rewrites it from `data/` every run.
- **Verify every YouTube id before shipping it**, oEmbed first, then the Apple catalogue `trackExplicitness` check for anything with lyrics, before the oEmbed check - see "The Flume lesson" further down this file for why the order matters. Both Smoke on the Water (Deep Purple) and Come As You Are (Nirvana), used as riff examples in Guitar, came back `notExplicit`.
- **Read DESIGN.md before touching any CSS** - the rules in it were earned through a finish review, not invented.
- The outstanding items list below (Popular Music's Easybeats question, the King Kong gap in Film Soundtrack, the YouTube Premium ads issue, the DoE publishing policy question) is unrelated to Guitar and still open - don't assume it was cleaned up as a side effect of this session.

## Also outstanding (carried forward, unrelated to Guitar)

1. **Popular Music Lesson 13 needs Matthew's ear on one track.** He asked for The Easybeats' "Friday On My Mind" as the vocal-riff example; no "na na na na" section could be located (the famous hook is the guitar riff), so it went in as asked and was flagged. If he names a different song, swap it in `popular-music.json` Lesson 13 and rebuild.
2. **King Kong (1933) has no video**, Film Soundtrack Lesson 7 - no clean official YouTube upload found, left as a title-only gap rather than risking an unofficial source.
3. **Ads on the embedded videos.** Matthew has YouTube Premium and still gets ads, because `youtube-nocookie.com` embeds don't carry his login cookies. Do not "fix" this by swapping to the tracked `youtube.com` domain - see the full reasoning in git history (commit around 7 August 2026) if this comes up again. Deferred - "it's fine for now".
4. **DoE external-publishing policy** still unverified for the whole site.

## Last commit

```
3ddd0ea Build Term 2 Guitar, 25 lessons
```

Committed locally, **not pushed**. 29 files changed (guitar.json, course.json, docs/index.html, 25 new lesson pages, new topic index).
