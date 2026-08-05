# Year 8 Music

Lesson material for a Year 8 Music course, published with GitHub Pages. Students read
it; assessment stays in Canvas.

Read `DESIGN.md` before touching any CSS. The rules in it were earned through a finish
review, not invented.

## How it works

- `data/` is the source of truth. One file per course, one per topic.
- `build.py` turns that into static pages in `docs/`. Standard library only, no
  dependencies to install and nothing to keep updated.
- `docs/` is what GitHub Pages serves. It is generated. Never edit it by hand.

## Building

```
python3 build.py
```

## Adding a listening example

Find the lesson in the topic file and set the `embed` on its media block to the YouTube
video id (the part after `v=`), not the whole URL:

```json
{ "type": "media", "n": 1, "brief": "...", "embed": "dQw4w9WgXcQ" }
```

A media block with no `embed` renders an honest "Not added yet" panel rather than
showing a placeholder to students.

## Adding a topic

1. Create `data/courses/year8-music/topics/<id>.json`, following `popular-music.json`.
2. Add the id to `topics` in `data/courses/year8-music/course.json`.
3. Rebuild.

No CSS should be needed. If a new block type is genuinely required, add it to
`block_html()` and record it in `DESIGN.md`.

## No position marker

The site never shows where a class is up to. Several classes run the same sequence at
different speeds, so any position claim is wrong for most of them. `build.py` has no
position logic and it must stay that way.

## What must never go on this site

Student names, student work, marks, markbook data, NESA past papers or marking
guidelines, the school's name or branding, and copyright audio or video files.
Recordings are embedded from YouTube, never uploaded. The site is public.
