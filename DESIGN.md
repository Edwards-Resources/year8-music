# Design: Year 8 Music

**This site is on the shared music shell**, since 19 November 2026. Every page (the 100 lessons, Quiz Revision, the four term pages and home) is built by `shell.py` and styled by `assets/shell.css`. The look belongs to the shell, not to this repo, and is the same across the music sites apart from one accent per year group. Year 8's is orange (`#C2410C`), set by `data-year="8"`.

The screenprint tour-shirt look it replaced (black print fields, bone stock, one spot ink per leg, Archivo Black) is in git history up to `7f48c54`.

## Where the look lives

- **`../music-shell/README.md`**: what the shell is, what each file does, and its rules. The shell is a local repo beside this one and is never pushed.
- **`../.serve/proto/redesign/SHELL-PLAN.md`**: the plan the shell was built to.
- **`shell.py`, `assets/shell.css`, `assets/shell.js` and the fonts in `assets/fonts/`** are copies. Never edit them here. Edit `music-shell/`, then run `python3 music-shell/sync.py year8-music` from `Sites/`.

## How the data reaches the shell

The data did not move. `data/courses/year8-music/` is read as before and `build.py` hands the pieces to shell functions.

### Lessons

| Data | On the page |
| --- | --- |
| `title`, `number`, its leg | Head card: the topic as kicker, the number large, "Lesson n of 25, in Chords and Harmony." as the meta line. An `assessed` lesson carries an "Assessment task" chip |
| `intention`, `criteria` | Learning intention, with the success criteria beside it |
| `prose` | Learn, with the title kept |
| `explain` | Learn, with the `call` large over the paragraphs. A `paras` item that is a list prints as bullets |
| `listen` | Listen. The `heading` is the title; a track with no `embed` keeps its place and says "Not added yet." |
| `media` | Watch, with the `brief` above the player |
| Placeholders ("Something - video") | A Watch or Listen card that says the video or tracks are still being chosen. The placeholder text never prints |
| `table` with every cell filled | Table |
| `table` with empty cells | Fill in: every empty cell is a box, including the first column when a row is left for the student to name ("Moment", "Track by") |
| `definition` | Key words, split back into term and meaning, beside the next section that can take a side card, or on their own card when nothing after them can |
| `activity` | Your task. "Your task - Screen off" becomes the title "Screen off"; plain "Your task" adds nothing to the label and is dropped |
| `list` | Step by step |
| `beatgrid` | Diagram: this site's own furniture (below) |
| `support`, `extension`, `exit` | The end cards: Need a hand, Go further, Exit ticket. "Need a hand? Start small" becomes the title "Start small" |

The old site gave one block per lesson the loud ink field. The shell has no loud block, so that rule is gone.

Under the lesson, standalone only: every lesson of the term, folded shut.

### Term pages

Head card, "This unit" (the blurb and the question for the term, with the outcomes beside them), the assessment card with links to any extra pages, the assessment runs where the topic has them, then every lesson grouped by leg.

**No position marker anywhere, ever.** Several classes run this sequence at different speeds. See `PRODUCT.md`.

### Home

The four terms as cards. Home opens Term 4.

## What is still this site's own

- **The beat grid** (Popular Music Lesson 8). Drawn as SVG by `beatgrid_svg()` and styled in `assets/site.css` with the shell's colours.
- **The two runs** (Film Soundtrack). On the term page, a chooser and each run as a schedule; on a lesson page, previous and next along the chosen run, which replace the plain ones. `assets/site.js` keeps the choice on the device under `y8:run:<topic>`, and `#ipads-first` or `#listening-first` in a link opens that run. Inside Canvas neither order shows, because Canvas moves students between lessons.
- **Saved answers from before the move.** The old site kept ticks and typed answers under `y8:<page>`. Each fill-in box carries its old name in `data-old`, and `assets/site.js` puts anything saved the old way back into the boxes once per page per device. It never deletes the old entries.
