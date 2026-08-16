# Next session

**Where things stand:** All four terms are built and live - Keyboard, Guitar, Popular Music, Film Soundtrack - 100 lesson pages plus 4 term indexes and the home page, 105 pages total. Term 2 Guitar was pushed on 14 August. The site is content-complete.

**Pushed 16 August 2026** (`e229cfa..59e658f`) and verified against the live URL rather than trusting the push. In sync with `origin/main`.

## Done 16 August 2026

All 100 lessons were triaged against the two tests this program settled on 14 August: does the lesson introduce something a student writes in their book that only exists in a teacher's head or a deck, and would you stop the recording and talk over it.

**Three fired. 753 words, against roughly 25,000 for a sequential pour.** Most lessons that looked like certain candidates turned out to be covered already: Keyboard 7 already carries the four-step dictation method as a list, Keyboard 6 does beat versus rhythm in one good sentence, Keyboard 2 has both mnemonics plus a count-from-middle-C method, and Film 7 is a genuinely good leitmotif lesson. **This site is in better shape than it looked**: its `definition` blocks print full meanings, most prose already does conceptual work, and it averages 177 to 235 words a term.

- **Film Soundtrack 2**, the five controls that create emotion. The task asked students to point at the musical choice and the page never gave them the levers; the support block's word bank lists emotions, not mechanisms.
- **Popular Music 6**, what a chord numeral means. The progressions table is good but nothing decoded I-V-vi-IV, so an absent student had a lookup table they could not read.
- **Guitar 8**, the three-part tone colour answer, and that tone colour words are not emotion words.

None of the three prints the answers to the worksheet table it sits above. That constraint shaped all of them.

**The `explain` block type is new** (`3258295`) and is documented in `DESIGN.md`. Quiet weight, so the task keeps the ink; no second hue, no new frame, no new size on either ramp. What separates it is the **call**, one sentence at the learning intention's size with the paragraphs at Body under it. Labelled `Liner notes`. A `paras` item is either a paragraph or a list of strings, the same either-shape `listen`'s tracks already use.

**Not eligible for the loud field**, and that is deliberate: adding a type to `loud_block()`'s search order would re-allocate the ink on lessons that already have it. One consequence to know about - on a lesson with no task block the loud field can land on a framing paragraph while the real teaching sits quiet below it, which is what Guitar 8 now does.

**Three defects fixed:** Popular Music 2 and 17 each named one term in a `definition` block while defining two, so both rendered a "Key word" heading over two definitions. Film 11 used "dissonance" in its lesson intention and in its own definition of suspense without ever defining it.

**Guitar 8's framing block was rewritten.** It said "Today you don't see any of these instruments being played, only hear them" directly above five Philharmonia clips that show the player. It now says listen before you look, and use the video afterwards to check yourself. **A swap of the embeds was asked for instead**, and this was done differently because the build already prints each track's title under its player and the table pre-fills the instrument column, so the page names all five instruments regardless of what the video shows. This may want reversing; if so, that is a real media-sourcing job with the full verification order per track.

## Next task

Nothing outstanding on this site beyond pushing. **The program's next task is Year 11**, which needs a design pass inside The Billing before its content pour. See `Sites/NEXT-SESSION.md`.

**Model and effort: Sonnet, medium** if the next session is more Year 8 content assembly. The block types, CSS and triage pattern are all settled.

## Watch out for

- **This site has no position marker by design and must never gain one.** Several classes run the same sequence at different speeds. There is no position logic in the build.
- **Verify every track before shipping it:** Apple explicitness flag, then oEmbed, then duration. That order.
- **Check whether text is a citation before correcting it.** Popular Music 17's video brief names echo and compression where the table says Delay and Filter; the brief is an accurate citation of the video's own title and was deliberately left. Guitar 2 asks for a tone colour word three lessons before the vocabulary is formalised, which reads as feel it first, name it later, and was also left.
- **Render the page and look at it before writing a rule about it.** The first version of the explain block set five named controls as prose and buried the five words a student writes in their book mid-sentence. Rendering caught it; reading the data did not.
- **The Browser pane fails often.** It hung on `scroll` this session. Headless Chrome against a symlink wrapper works, since the site expects to be served at `/year8-music/` rather than at the server root. Its narrow-width clipping is an artifact; use the Browser pane's `resize_window` for real mobile checks.
- **`#000` at `assets/site.css:74`** trips the design hook every time. It is the opaque stop of the halftone's `mask-image` gradient, where only the alpha channel is read, and `DESIGN.md` documents it. Leave it.
- **No school name and no student names anywhere in this repository**, not just on the built site. The repo is public and git history is permanent. Grep any new file before committing.

**Last commits:** `3e1ffbd` "Make Guitar 8 tell the truth about its own videos", `3258295` "Port the explain block into Tour Tee and pour the three triaged lessons". Both pushed and live.
