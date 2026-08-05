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
by Matthew after a re-roll steered for fun and playful. Seed key b2cc7a19.
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


def loud_block(blocks):
    """Index of the one block on a lesson that carries the filled ink field.

    The loud weight belongs to the thing the student has to act on. In an ordinary
    lesson that is the task. Assessment lessons carry no task block, which is why
    they used to render with no filled field at all and read as the least printed
    pages on the site; there the criteria list, or failing that the first named
    paragraph, is what the student acts on. Exactly one per lesson, always.
    """
    for want in ("activity",), ("list",), ("prose",):
        for i, b in enumerate(blocks):
            if b["type"] in want and (want[0] != "prose" or b.get("title") or b.get("heading")):
                return i
    return -1


def block_html(block, loud=False):
    t = block["type"]
    h = block.get("heading")
    head = f'<h3 class="blk-h">{e(h)}</h3>' if h else ""

    if t == "listen":
        tracks = block["tracks"]
        # The Canvas pages carry unfilled media slots written as "Something - video".
        # They are placeholders, not repertoire, and must never render as content.
        if all(x.rstrip().lower().endswith("- video") for x in tracks):
            return ('<section class="blk panel quiet"><h3 class="panel-h">Listening</h3>'
                    '<div class="panel-in"><p>Not added yet. The tracks for this lesson '
                    'are still being chosen.</p></div></section>')
        rows = "".join(
            f'<li><span class="tick" aria-hidden="true"></span><span>{e(x)}</span></li>'
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
        th = "".join(f"<th>{e(c)}</th>" for c in block["headers"])
        rows = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>"
                       for r in block["rows"])
        # The table keeps a min-width, so on a phone it scrolls inside this wrapper.
        # A scroll region needs a name and keyboard focus, or it is unreachable
        # without a pointer, and the hint says so in words rather than a fading edge.
        label = e(f"{h}, table" if h else "Table")
        # The hint goes above the wrapper, so it is read before the clip, not after.
        return (f'<section class="blk">{head}'
                '<p class="tablehint">Swipe the table sideways to see the rest.</p>'
                f'<div class="tablewrap" role="region" tabindex="0" aria-label="{label}">'
                f"<table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table>"
                "</div></section>")

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
        terms = "".join(f'<span class="term">{e(x)}</span>' for x in block.get("terms") or [])
        return panel("Key words", f'<p class="terms">{terms}</p>' if terms else "")

    if t == "support":
        return panel(block.get("title") or "Need a hand?")

    if t == "extension":
        return panel("Go further")

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

    if t == "prose":
        title = block.get("title") or h
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
    blocks = "".join(block_html(b, loud=(i == li))
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
