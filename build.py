#!/usr/bin/env python3
"""Build the Year 8 Music site.

Reads data/, writes docs/. Standard library only, on purpose: no package manager,
no lockfile, nothing that needs updating in three years when nobody is looking.

    python3 build.py

Every page is generated. Never edit anything in docs/ by hand; it gets overwritten.

One rule this build enforces structurally: there is no "current lesson" anywhere.
Several classes run this sequence at different speeds, so the site never marks a
position. If you find yourself adding one, read PRODUCT.md first.
"""

import html
import json
import os
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs")
ASSETS = os.path.join(ROOT, "assets")

# The five legs of the tour, in print order. Spot inks, screenprint-loud.
LEG_INK = {"A": "pink", "B": "yellow", "C": "cyan", "D": "lime", "E": "orange"}


def load(*parts):
    with open(os.path.join(DATA, *parts), encoding="utf-8") as f:
        return json.load(f)


def e(s):
    return html.escape(str(s), quote=True)


def write(path_parts, markup):
    path = os.path.join(OUT, *path_parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(markup)


# ------------------------------------------------------------------ helpers


def flat_lessons(topic):
    return [l for s in topic["sections"] for l in s["lessons"]]


def leg_of(topic, number):
    for s in topic["sections"]:
        if s["from"] <= number <= s["to"]:
            return s
    return topic["sections"][0]


def lesson_href(site, course, topic, lesson):
    return f"{site['base']}/{course['id']}/{topic['id']}/lesson-{lesson['number']}/"


# ---------------------------------------------------------------- page shell


def layout(site, title, body, description="", crumbs=None):
    base = site["base"]
    robots = '<meta name="robots" content="noindex, nofollow">' if site.get("noindex") else ""
    crumbs = crumbs or []
    trail = ""
    if crumbs:
        parts = []
        for i, (label, href) in enumerate(crumbs):
            if href and i < len(crumbs) - 1:
                parts.append(f'<li><a href="{base}{href}">{e(label)}</a></li>')
            else:
                parts.append(f'<li><span aria-current="page">{e(label)}</span></li>')
        trail = ('<nav class="crumbs" aria-label="Breadcrumb"><div class="wrap">'
                 f'<ol>{"".join(parts)}</ol></div></nav>')

    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{robots}
<title>{e(title)} | {e(site['title'])}</title>
<meta name="description" content="{e(description)}">
<link rel="stylesheet" href="{base}/assets/site.css">
</head>
<body>
<!--
THESIS: The term is the tour and every lesson is a date on the back of the shirt.
Refuses the school course-card grid and the week accordion: the term page is a
tour back-print you read straight down, with no "you are here" anywhere.
OWN-WORLD: Screenprint. Black print fields for covers, bone garment stock for
reading, five loud spot inks (pink, yellow, cyan, lime, orange) one per leg.
Heavy grotesque caps with a single overprint offset, halftone dot fields, thick
rules, black type on every spot ink. Recognisable with all content removed.
STORY: A student finds their date in the list, opens it, and works down a lesson
laid out like a gig page: the billing, the set, the task, the way out.
FIRST VIEWPORT: Black print field, unit name at poster scale as a tour logo,
25 DATES beneath it, and the tour list starting immediately with no hero card.
FORM: Band merch back-print tour list, candidate 6 of the grounded list, chosen
by the user after a re-roll steered for fun and playful. Seed key b2cc7a19.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish
review, the verdict, and DESIGN.md
-->
<a class="skip" href="#main">Skip to content</a>
<header class="bar">
  <div class="wrap"><a class="brand" href="{base}/">{e(site['title'])}</a></div>
</header>
{trail}
<main id="main">
{body}
</main>
<footer class="foot">
  <div class="wrap">
    <p>Class material. Assessment tasks, submissions and marks stay in Canvas.</p>
    <p class="foot-date">Updated {date.today().strftime('%-d %B %Y')}</p>
  </div>
</footer>
<script src="{base}/assets/site.js" defer></script>
</body>
</html>
"""


# ------------------------------------------------------------------- blocks


def is_placeholder(text):
    """True for an unfilled media slot carried over from the Canvas pages.

    They are written as "Something - video": a note to the author about what to find,
    never a sentence meant for a student. The listen blocks have always been checked
    for this, but the same placeholders also arrive as untitled prose, and there they
    printed to the page as if they were teaching copy. One test, used by both.
    """
    t = (text or "").rstrip().lower()
    return t.endswith("- video") or t.endswith("- audio")


def unfilled_media(label, what):
    """The honest stand-in for a media slot that has no media yet.

    Quiet weight, the same as every other titled block, because an empty slot must
    not shout louder than the lesson around it.
    """
    return (f'<section class="blk panel quiet"><h3 class="panel-h">{label}</h3>'
            f'<div class="panel-in"><p>Not added yet. The {what} for this lesson '
            f'{"are" if what.endswith("s") else "is"} still being chosen.</p>'
            f'</div></section>')


def player_html(embed, title):
    """The 16:9 well. Lazy, so a lesson carrying six of them still opens on the board."""
    return (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{e(embed)}" '
            f'title="{e(title)}" loading="lazy" allowfullscreen '
            'allow="accelerometer; clipboard-write; encrypted-media; picture-in-picture">'
            '</iframe></div>')


def clip_html(track):
    """One named thing to listen to, with its player if it has one yet.

    A track with no embed keeps its place in the grid and says so, rather than
    disappearing, so the run still reads as the complete set the lesson names.
    """
    name = f'<p class="clip-t">{e(track["title"])}</p>'
    if track.get("embed"):
        return f'<div class="clip">{player_html(track["embed"], track["title"])}{name}</div>'
    return f'<div class="clip"><div class="video video-none"><p>Not added yet</p></div>{name}</div>'


def loud_block(blocks):
    """Index of the one block on a lesson that carries the filled ink field.

    The loud weight belongs to the thing the student has to act on. In an ordinary
    lesson that is the task. Assessment lessons carry no task block, which is why
    they used to render with no filled field at all and read as the least printed
    pages on the site; there the criteria list, or failing that the first named
    paragraph, is what the student acts on. Exactly one per lesson, always.

    A placeholder can never take the ink. Today's placeholders are all untitled and
    so were never eligible, but a titled one would otherwise print "Not added yet"
    as the loudest thing on the page.
    """
    for want in ("activity",), ("list",), ("prose",):
        for i, b in enumerate(blocks):
            if b["type"] in want and (want[0] != "prose" or b.get("title") or b.get("heading")):
                if is_placeholder(b.get("text")):
                    continue
                return i
    return -1


def beatgrid_html(block):
    """Four bars of drum grid with the chord blocks drawn above it.

    A student who has just watched a multitrack tutorial can record two layers and
    still have no picture of what "line them up" means. Words do not carry it: the
    thing being taught is a spatial relationship, so it is drawn. Print Black rules
    on bone with the leg ink for the chord blocks, which is the same two-colour
    budget every other object on the page works inside.

    The grid is described in data - rows of sixteen hits, and a chord per bar - so
    a later lesson can draw a different groove without touching this function.
    """
    rows = block["rows"]
    chords = block["chords"]
    bars, per_bar = 4, 4
    steps = bars * per_bar
    lab_w, cell, row_h = 108, 44, 40          # user units, viewBox space
    top = 66                                   # chord band above the drum rows
    w = lab_w + steps * cell
    h = top + len(rows) * row_h + 34

    p = []
    # The chord band. One block per bar, each landing exactly on beat 1, which is
    # the whole claim the diagram is making.
    p.append('<text x="0" y="16" class="bg-lab" font-size="15">Chords</text>')
    for i, ch in enumerate(chords):
        x = lab_w + i * per_bar * cell
        p.append(f'<rect x="{x + 2}" y="24" width="{per_bar * cell - 4}" height="34" '
                 'class="bg-chord"/>')
        p.append(f'<text x="{x + per_bar * cell / 2}" y="47" class="bg-ch" '
                 f'font-size="20">{e(ch)}</text>')

    # The drum rows. A filled square is a hit, so the pattern reads at board size.
    for r, row in enumerate(rows):
        y = top + r * row_h
        p.append(f'<text x="0" y="{y + 26}" class="bg-lab" font-size="15">'
                 f'{e(row["name"])}</text>')
        for s in range(steps):
            x = lab_w + s * cell
            p.append(f'<rect x="{x}" y="{y + 4}" width="{cell}" height="{row_h - 8}" '
                     'class="bg-cell"/>')
            if row["hits"][s] == "x":
                p.append(f'<rect x="{x + 8}" y="{y + 12}" width="{cell - 16}" '
                         f'height="{row_h - 24}" class="bg-hit"/>')

    # Bar lines run the full height, through both the chord band and the drums,
    # because the alignment between them is the point being made.
    bottom = top + len(rows) * row_h
    for b in range(bars + 1):
        x = lab_w + b * per_bar * cell
        p.append(f'<line x1="{x}" y1="20" x2="{x}" y2="{bottom}" class="bg-bar"/>')
    for b in range(bars):
        x = lab_w + b * per_bar * cell + per_bar * cell / 2
        p.append(f'<text x="{x}" y="{bottom + 24}" class="bg-beat" font-size="13">'
                 f'Bar {b + 1}</text>')

    svg = (f'<svg viewBox="0 0 {w} {h}" class="beatgrid" role="img" '
           f'aria-label="{e(block["alt"])}">{"".join(p)}</svg>')
    cap = f'<p class="bg-cap">{e(block["caption"])}</p>' if block.get("caption") else ""
    # Same rule as the tables: a region that clips gets a name, keyboard focus, and
    # a hint in words at the width where it actually clips.
    return ('<section class="blk panel quiet"><h3 class="panel-h">'
            f'{e(block.get("title") or "Lining the layers up")}</h3>'
            '<div class="panel-in">'
            '<p class="tablehint">Swipe the diagram sideways to see all four bars.</p>'
            f'<div class="bgwrap" role="region" tabindex="0" '
            f'aria-label="{e(block["alt"])}">{svg}</div>{cap}</div></section>')


def block_html(block, loud=False, idx=0):
    t = block["type"]
    h = block.get("heading")
    head = f'<h3 class="blk-h">{e(h)}</h3>' if h else ""

    if t == "listen":
        # A track is either a bare title or {"title", "embed"}. Both shapes live in
        # the same list, so a block can be half filled while it is worked through.
        tracks = [x if isinstance(x, dict) else {"title": x} for x in block["tracks"]]
        # Placeholders, not repertoire, and they must never render as content.
        if all(is_placeholder(x["title"]) for x in tracks):
            return unfilled_media("Listening", "tracks")

        # Once anything in the run is playable the whole run becomes a clip grid.
        # Mixing a player column against a tick list reads as two different blocks.
        if any(x.get("embed") for x in tracks):
            title = block.get("heading") or "Listen"
            clips = "".join(clip_html(x) for x in tracks)
            return (f'<section class="blk panel quiet"><h3 class="panel-h">{e(title)}</h3>'
                    f'<div class="panel-in"><div class="clips">{clips}</div></div></section>')

        rows = "".join(
            f'<li><span class="tick" aria-hidden="true"></span><span>{e(x["title"])}</span></li>'
            for x in tracks
        )
        # The heading is the truth: these runs are sometimes a listening list and
        # sometimes a set of named things (the three grooves). Only say "Listen"
        # when the source page did not name the group itself. Titled means quiet
        # panel, the same as every other named block, so one content shape does
        # not print two ways from one lesson to the next.
        title = block.get("heading") or "Listen"
        return (f'<section class="blk panel quiet"><h3 class="panel-h">{e(title)}</h3>'
                f'<div class="panel-in"><ul class="tracks">{rows}</ul></div></section>')

    if t == "table":
        # A worksheet table is one that arrives with empty cells: the data says what
        # the columns are and leaves the answers blank. Those blanks are the whole
        # point of the block, so they become fields a student can type into rather
        # than dead space they have to copy into a book. A reference table (every
        # cell filled, as in Lesson 1's survey) is left exactly as it was.
        fillable = any(not str(c).strip() for r in block["rows"] for c in r)
        th = "".join(f"<th>{e(c)}</th>" for c in block["headers"])

        def cell(c, ri, ci):
            if not (fillable and not str(c).strip()):
                return f"<td>{e(c)}</td>"
            # aria-label reads the row's first filled cell and the column head, so
            # the field is identifiable out of context: "Piano ballad, Mood".
            row_name = next((str(x).strip() for x in block["rows"][ri] if str(x).strip()), "")
            col = block["headers"][ci] if ci < len(block["headers"]) else ""
            label = ", ".join(x for x in (row_name, col) if x) or "Answer"
            return (f'<td class="fillcell"><input type="text" class="fill" '
                    f'data-cell="{idx}-{ri}-{ci}" aria-label="{e(label)}"></td>')

        rows = "".join(
            "<tr>" + "".join(cell(c, ri, ci) for ci, c in enumerate(r)) + "</tr>"
            for ri, r in enumerate(block["rows"])
        )
        # The table keeps a min-width, so on a phone it scrolls inside this wrapper.
        # A scroll region needs a name and keyboard focus, or it is unreachable
        # without a pointer, and the hint says so in words rather than a fading edge.
        label = e(f"{h}, table" if h else "Table")
        # Two columns fit a phone, so they drop the 34rem floor and stop asking to be
        # swiped. The hint goes with it: a table that no longer clips must not tell a
        # student to slide it, and the hint sits above the wrapper so it is read
        # before the clip rather than after.
        narrow = len(block["headers"]) <= 2
        hint = ("" if narrow
                else '<p class="tablehint">Swipe the table sideways to see the rest.</p>')
        cls = "tablewrap" + (" is-fill" if fillable else "") + (" is-narrow" if narrow else "")
        note = ('<p class="fillnote">Type straight into the boxes. Your answers stay '
                'on this device and are still here if you close the page.</p>'
                if fillable else "")
        return (f'<section class="blk">{head}{hint}'
                f'<div class="{cls}" role="region" '
                f'tabindex="0" aria-label="{label}">'
                f"<table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table>"
                f"</div>{note}</section>")

    # One ink per lesson, three weights. The leg's spot ink comes from the article,
    # so hue never encodes block type; the weight of the treatment does. Loud is the
    # filled ink bar and belongs to the task alone, because the task is the one thing
    # a student has to do. Everything else is a quiet bone box under a black rule.
    def panel(label, extra=""):
        items = "".join(f"<li>{e(i)}</li>" for i in block.get("items") or [])
        inner = f"<p>{e(block['text'])}</p>" if block.get("text") else ""
        inner += f"<ul>{items}</ul>" if items else ""
        cls = "blk panel" if loud else "blk panel quiet"
        return (f'<section class="{cls}">{head}'
                f'<h3 class="panel-h">{e(label)}</h3>'
                f'<div class="panel-in">{extra}{inner}</div></section>')

    if t == "activity":
        return panel(block.get("title") or "Your task")

    if t == "definition":
        # One box per word. The extractor used to fold two unrelated elements into
        # a single Key words panel - timbre with dynamics, structure with drop - and
        # a student reading it could not tell where one definition stopped. A block
        # carrying exactly one term names that term in its own heading; a genuine
        # group of related words keeps the plural label.
        # With one term the heading carries the word, so the chip would print it
        # twice in a row; the chips stay where they are doing work, naming several.
        names = block.get("terms") or []
        if len(names) == 1:
            return panel(f"Key word: {names[0]}")
        terms = "".join(f'<span class="term">{e(x)}</span>' for x in names)
        return panel("Key words", f'<p class="terms">{terms}</p>' if terms else "")

    if t == "support":
        return panel(block.get("title") or "Need a hand?")

    if t == "extension":
        return panel("Go further")

    if t == "explain":
        # The block a student who missed the lesson can teach themselves from, and
        # the only long read on the page. It takes the quiet weight like every other
        # named block: the task keeps the ink, because the task is still the thing
        # to act on. What sets this block apart is the call - one sentence carrying
        # the idea, set at the learning intention's size - so the back of a daylit
        # room gets the claim off the board and the student at home reads the rest.
        # That is the two-distance split the whole system is built for, done inside
        # one block instead of with a second ink.
        #
        # Paragraphs arrive as a list rather than as one string split on blank
        # lines, so the data says where a paragraph ends instead of the renderer
        # guessing. A block with no call and no paragraphs is not a thin block, it
        # is an empty one, and it prints nothing.
        #
        # An item is either a paragraph or a list of strings, the same either-shape
        # the listen block's tracks already use. This exists because the first
        # explain block written was a five-item set of controls set as prose, and
        # rendering it showed the five names a student has to write down buried mid
        # sentence. A set is bulleted; keeping it in one field rather than adding a
        # second means the data decides where in the read the set falls.
        call = block.get("call") or ""
        items = [p for p in (block.get("paras") or []) if p]
        if not call and not items:
            return ""
        inner = f'<p class="call">{e(call)}</p>' if call else ""
        for p in items:
            if isinstance(p, list):
                inner += "<ul>" + "".join(f"<li>{e(x)}</li>" for x in p) + "</ul>"
            else:
                inner += f"<p>{e(p)}</p>"
        return ('<section class="blk panel quiet explain">'
                f'{head}<h3 class="panel-h">Liner notes</h3>'
                f'<div class="panel-in">{inner}</div></section>')

    if t == "exit":
        # The way out: a solid ink field, the only one on the page, so the lesson
        # ends on a printed beat rather than another bordered box.
        return ('<section class="blk encore"><div class="encore-in">'
                '<h3 class="encore-h">Encore</h3>'
                f'<p>{e(block["text"])}</p></div></section>')

    # A named list or a named paragraph is the same printed object as a support or
    # extension block, so it takes the same quiet treatment. Without this the
    # assessment lessons, which are almost entirely titled prose, render as bare
    # text and end up the least printed pages on a site about printing.
    cls = "blk panel" if loud else "blk panel quiet"

    if t == "list":
        items = "".join(f"<li><span>{e(i)}</span></li>" for i in block["items"])
        title = block.get("title") or block.get("heading") or ""
        if not title:
            return f'<section class="blk"><ol class="steps">{items}</ol></section>'
        return (f'<section class="{cls}"><h3 class="panel-h">{e(title)}</h3>'
                f'<div class="panel-in"><ol class="steps">{items}</ol></div></section>')

    if t == "media":
        # A filled slot and an empty one are the same shape on the page: the quiet
        # panel labelled Video. Only the inside changes, so a lesson does not
        # re-flow when the track is finally picked.
        if not block.get("embed"):
            return unfilled_media("Video", "video")
        brief = f'<p>{e(block["brief"])}</p>' if block.get("brief") else ""
        return (
            '<section class="blk panel quiet"><h3 class="panel-h">Video</h3>'
            '<div class="panel-in">'
            + player_html(block["embed"], block.get("brief") or "Video for this lesson")
            + f'{brief}</div></section>'
        )

    if t == "beatgrid":
        return beatgrid_html(block)

    if t == "prose":
        title = block.get("title") or h
        # Eight lessons carry their unfilled video slot as untitled prose rather than
        # as a listen block, and printed it to the page as a sentence. Same slot, same
        # honest notice, whichever shape it arrives in.
        if is_placeholder(block.get("text")):
            return unfilled_media("Video", "video")
        if not title:
            return f'<section class="blk"><p>{e(block["text"])}</p></section>'
        return (f'<section class="{cls}"><h3 class="panel-h">{e(title)}</h3>'
                f'<div class="panel-in"><p>{e(block["text"])}</p></div></section>')

    return ""


# -------------------------------------------------------------------- pages


def tour_list(site, course, topic):
    """The back-print: every lesson of the term as a tour date."""
    legs = []
    for s in topic["sections"]:
        ink = LEG_INK.get(s["letter"], "pink")
        rows = []
        for l in s["lessons"]:
            flag = '<span class="flag">Assessment</span>' if l.get("assessed") else ""
            cls = " is-assessed" if l.get("assessed") else ""
            rows.append(
                f'<li class="date{cls}">'
                f'<a href="{lesson_href(site, course, topic, l)}">'
                f'<span class="no">{l["number"]}</span>'
                f'<span class="what"><span class="tt">{e(l["title"])}</span>'
                f'<span class="int">{e(l["intention"])}</span></span>'
                f"{flag}</a></li>"
            )
        legs.append(f"""<section class="leg ink-{ink}">
  <div class="leg-head">
    <span class="leg-letter" aria-hidden="true">{s['letter']}</span>
    <h2>{e(s['name'])}</h2>
    <span class="leg-range">Lessons {s['from']} to {s['to']}</span>
  </div>
  <ol class="dates">{''.join(rows)}</ol>
</section>""")
    return "".join(legs)


def build_topic(site, course, topic):
    total = len(flat_lessons(topic))
    outcomes = "".join(f'<li><span class="code">{e(c)}</span> {e(t)}</li>'
                       for c, t in topic["outcomes"])
    a = topic["assessment"]

    body = f"""<div class="print">
  <div class="wrap">
    <h1 class="logo">{e(topic['name'])}</h1>
    <p class="count">{e(topic['term'])} &middot; {total} dates &middot; {e(topic['subtitle'])}</p>
    <p class="blurb">{e(topic['blurb'])}</p>
  </div>
  <div class="halftone" aria-hidden="true"></div>
</div>

<div class="wrap">
  <section class="askbox">
    <h2>The question for this term</h2>
    <div class="askbox-in"><p>{e(topic['question'])}</p></div>
  </section>

  <div class="tour">
    <div class="tour-main">
      <div class="tour-head">
        <h2>The dates</h2>
        <p>Every lesson of the term, in order. Go straight to the one you need.</p>
      </div>
      {tour_list(site, course, topic)}
    </div>
    <aside class="tour-side">
      <section class="panel ink-pink">
        <h3 class="panel-h">{e(a['name'])}</h3>
        <div class="panel-in">
          <p class="when">{e(a['when'])}</p>
          <p>{e(a['detail'])}</p>
          <p class="small">The task notification and submission are in Canvas.</p>
        </div>
      </section>
      <section class="panel outcomes">
        <h3 class="panel-h">Outcomes</h3>
        <div class="panel-in"><ul>{outcomes}</ul></div>
      </section>
    </aside>
  </div>
</div>"""
    return layout(site, topic["name"], body, topic["blurb"],
                  [("Home", "/"), (topic["name"], None)])


def build_lesson(site, course, topic, lesson, prev_l, next_l):
    leg = leg_of(topic, lesson["number"])
    ink = LEG_INK.get(leg["letter"], "pink")
    total = len(flat_lessons(topic))

    crit = "".join(
        f'<li><input type="checkbox" id="c{i}"><label for="c{i}">{e(c)}</label></li>'
        for i, c in enumerate(lesson["criteria"])
    )
    li = loud_block(lesson["blocks"])
    # The block index goes through so a fillable table's saved answers are keyed to
    # its position in the lesson, not just to the page. Two tables on one lesson
    # would otherwise share one set of stored values.
    blocks = "".join(block_html(b, loud=(i == li), idx=i)
                     for i, b in enumerate(lesson["blocks"]))
    flag = ('<p class="assessed-flag">This lesson is an assessment task</p>'
            if lesson.get("assessed") else "")

    nav = []
    if prev_l:
        nav.append(f'<a class="pn prev" href="{lesson_href(site, course, topic, prev_l)}">'
                   f'<span>Previous</span><strong>{e(prev_l["title"])}</strong></a>')
    if next_l:
        nav.append(f'<a class="pn next" href="{lesson_href(site, course, topic, next_l)}">'
                   f'<span>Next</span><strong>{e(next_l["title"])}</strong></a>')

    body = f"""<article class="lesson ink-{ink}">
<div class="print print-lesson">
  <div class="wrap">
    <div class="bill">
      <span class="big-no" aria-hidden="true">{lesson['number']}</span>
      <h1>{e(lesson['title'])}</h1>
    </div>
    <p class="of">Lesson {lesson['number']} of {total} &middot; {e(leg['name'])}</p>
    {flag}
  </div>
  <div class="halftone" aria-hidden="true"></div>
</div>

<div class="wrap lesson-body">
  <div class="lesson-main">
    <section class="intention">
      <p>{e(lesson['intention'])}</p>
    </section>
    {blocks}
  </div>
  <aside class="lesson-side">
    <section class="panel">
      <h3 class="panel-h">How you know you have it</h3>
      <div class="panel-in"><ul class="crit">{crit}</ul>
      <p class="small">Ticks save on this device only.</p></div>
    </section>
    <a class="back" href="{site['base']}/{course['id']}/{topic['id']}/">All {total} dates</a>
  </aside>
</div>

<nav class="prevnext wrap" aria-label="Lessons">{''.join(nav)}</nav>
</article>"""

    crumbs = [("Home", "/"), (topic["name"], f"/{course['id']}/{topic['id']}/"),
              (f"Lesson {lesson['number']}", None)]
    return layout(site, f"Lesson {lesson['number']}: {lesson['title']}", body,
                  lesson["intention"], crumbs)


def build_home(site, courses):
    cards = []
    for course, topics in courses:
        for t in topics:
            n = len(flat_lessons(t))
            cards.append(f"""<li class="poster">
  <a href="{site['base']}/{course['id']}/{t['id']}/">
    <span class="poster-name">{e(t['name'])}</span>
    <span class="poster-sub">{e(t['term'])} &middot; {e(t['subtitle'])} &middot; {n} dates</span>
  </a>
</li>""")

    body = f"""<div class="print print-home">
  <div class="wrap">
    <h1 class="logo">{e(site['title'])}</h1>
    <p class="blurb">Everything we do in class, lesson by lesson. Miss one and you can pick up exactly what the class did.</p>
  </div>
  <div class="halftone" aria-hidden="true"></div>
</div>
<div class="wrap">
  <ul class="posters">{''.join(cards)}</ul>
  <p class="rest">The rest of the year goes up here as each term is written.</p>
</div>"""
    return layout(site, site["title"], body, "Year 8 Music class material, lesson by lesson.")


# --------------------------------------------------------------------- main


def main():
    site = load("site.json")
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    courses = []
    for cid in site["courses"]:
        course = load("courses", cid, "course.json")
        topics = [load("courses", cid, "topics", f"{tid}.json") for tid in course["topics"]]
        courses.append((course, topics))

    pages = 0
    for course, topics in courses:
        cid = course["id"]
        for topic in topics:
            write([cid, topic["id"], "index.html"], build_topic(site, course, topic))
            pages += 1
            lessons = flat_lessons(topic)
            for i, lesson in enumerate(lessons):
                write([cid, topic["id"], f"lesson-{lesson['number']}", "index.html"],
                      build_lesson(site, course, topic, lesson,
                                   lessons[i - 1] if i else None,
                                   lessons[i + 1] if i + 1 < len(lessons) else None))
                pages += 1

    write(["index.html"], build_home(site, courses))
    pages += 1

    shutil.copytree(ASSETS, os.path.join(OUT, "assets"))
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    print(f"built {pages} pages into docs/")


if __name__ == "__main__":
    main()
