#!/usr/bin/env python3
"""Build the Year 8 Music site.

Reads data/, writes docs/. Standard library only, on purpose: no package manager,
no lockfile, nothing that needs updating in three years when nobody is looking.

    /usr/bin/python3 build.py

Every page is generated. Never edit anything in docs/ by hand; it gets overwritten.

Since 19 November 2026 every page is drawn by the shared music shell (shell.py,
copied in from ../music-shell by sync.py; never edit the copy here). This file
reads Year 8's data and hands each piece to a shell function. What is still
Year 8's own: the beat grid, the two runs on Film Soundtrack, and assets/site.js,
which carries saved answers across from the old storage names.

One rule this build enforces structurally: there is no "current lesson" anywhere.
Several classes run this sequence at different speeds, so the site never marks a
position. If you find yourself adding one, read PRODUCT.md first.
"""

import json
import os
import re
import shutil

import shell as S

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs")
ASSETS = os.path.join(ROOT, "assets")

e = S.e


def load(*parts):
    with open(os.path.join(DATA, *parts), encoding="utf-8") as f:
        return json.load(f)


def write(path_parts, markup):
    path = os.path.join(OUT, *path_parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(markup)


def shell_site(site, nav):
    return {"base": site["base"], "title": site["title"], "year": 8, "key": "y8",
            "foot": "Class material. Assessment tasks, submissions and marks stay in Canvas.",
            "nav": nav, "noindex": site.get("noindex")}


# ------------------------------------------------------------------ helpers


def flat_lessons(topic):
    return [l for s in topic["sections"] for l in s["lessons"]]


def leg_of(topic, number):
    for s in topic["sections"]:
        if s["from"] <= number <= s["to"]:
            return s
    return topic["sections"][0]


def topic_path(course, topic):
    return f"/{course['id']}/{topic['id']}/"


def page_path(course, topic, ref):
    """Site-relative address of a lesson number or one of the topic's extra pages.
    These addresses are what Canvas frames point at, so they never change."""
    if isinstance(ref, int):
        return f"/{course['id']}/{topic['id']}/lesson-{ref}/"
    return f"/{course['id']}/{topic['id']}/{ref}/"


def page_of(topic, ref):
    if isinstance(ref, int):
        return next(l for l in flat_lessons(topic) if l["number"] == ref)
    return next(p for p in topic.get("pages", []) if p["slug"] == ref)


def is_placeholder(text):
    """An unfilled media slot carried over from the Canvas pages, written as
    "Something - video": a note to the author, never a sentence for a student."""
    t = (text or "").rstrip().lower()
    return t.endswith("- video") or t.endswith("- audio")


def strip_prefix(title, prefix):
    """ "Your task - Screen off" names the task "Screen off" under the Your task
    label, and "Need a hand? Start small" is "Start small" under Need a hand.
    The bare label on its own adds nothing to the label, so it is dropped."""
    if not title:
        return None
    if title.startswith(prefix):
        return title[len(prefix):].lstrip(" -:?.") or None
    return title


# ------------------------------------------------------------- the two runs
#
# Two teachers share one set of iPads, so the classes running this term take the
# same lessons in two orders: the iPads first and the listening after, or the
# other way round. A run is a sequence, never a position. It says what comes after
# what for a class on that run; it never says where any class is up to, so it
# carries no dates, no class names and no teacher names, and the build still has no
# idea which lesson is "now".


def run_numbers(run):
    """[(block, item, number or None)] with numbering that skips unnumbered blocks."""
    out, n = [], 0
    for b in run["blocks"]:
        for item in b["items"]:
            if b.get("numbered", True):
                n += 1
                out.append((b, item, n))
            else:
                out.append((b, item, None))
    return out, n


def run_sequence(topic, run):
    """Every page the run visits, in order, each once: [(ref, label)]."""
    items, total = run_numbers(run)
    seq, seen = [], set()
    for b, item, n in items:
        label = f"{n} of {total}" if n else b["name"].lower()
        for ref in item["pages"]:
            if ref not in seen:
                seen.add(ref)
                seq.append((ref, label))
    missing = [l["number"] for l in flat_lessons(topic) if l["number"] not in seen]
    assert not missing, f"run {run['id']} never visits lessons {missing}"
    return seq


def pages_phrase(topic, refs):
    def name(r):
        return f"Lesson {r}" if isinstance(r, int) else page_of(topic, r)["title"]
    nums = [r for r in refs if isinstance(r, int)]
    if len(nums) > 2 and nums == list(range(nums[0], nums[-1] + 1)) and len(nums) == len(refs):
        return f"Lessons {nums[0]} to {nums[-1]}"
    if len(refs) == 2 and all(isinstance(r, int) for r in refs):
        return f"Lesson {refs[0]}, then Lesson {refs[1]}"
    return ", then ".join(name(r) for r in refs)


def runs_html(course, topic, base):
    """The run chooser, then each run as a schedule. With scripting off every run
    shows; with it on, only the one chosen on this device."""
    runs = topic.get("runs")
    if not runs:
        return ""
    buttons = "".join(
        f'<button type="button" class="runbtn" data-run="{e(r["id"])}" aria-pressed="false">'
        f'{e(r["name"])}</button>' for r in runs)
    chooser = S.section(
        "runs", "Assessment run", "list", "The assessment run",
        '<p class="brief">The lessons up to the task, in the order your class does them. '
        'Your teacher will tell you which run is yours.</p>'
        f'<div class="runswitch" role="group" aria-label="Choose your run" hidden>{buttons}</div>'
        '<p class="runprompt fine" hidden>Choose your class&rsquo;s run to see its order.</p>')
    panels = []
    for r in runs:
        items, total = run_numbers(r)
        groups, current, rows = [], None, []
        for b, item, n in items:
            if b is not current:
                if current is not None:
                    groups.append((current["name"], rows, current["weeks"]))
                current, rows = b, []
            refs = item["pages"]
            target = refs[0] if refs else item.get("link")
            where = pages_phrase(topic, refs) if refs else ""
            words = ". ".join(x for x in (where, item.get("note", "").rstrip(".")) if x)
            flag = f'**{item["flag"]}.** ' if item.get("flag") else ""
            rows.append({"n": str(n) if n else "·", "title": item["title"],
                         "href": page_path(course, topic, target),
                         "meta": f"{flag}{words}.", "at": bool(item.get("flag"))})
        groups.append((current["name"], rows, current["weeks"]))
        panels.append(f'<div class="run" id="{e(r["id"])}" data-run="{e(r["id"])}">'
                      + S.schedule(groups, base=base, title=f'{r["name"]}', label="Assessment run",
                                   note=r["blurb"])
                      + "</div>")
    return f'<div class="runs" data-topic="{e(topic["id"])}">{chooser}{"".join(panels)}</div>'


def run_nav_html(course, topic, ref, base):
    """Previous and next along each run, hidden until a run has been chosen. When
    one is showing, site.js hides the plain lesson order under it."""
    navs = []
    for r in topic.get("runs", []):
        seq = run_sequence(topic, r)
        idx = next(i for i, (x, _) in enumerate(seq) if x == ref)
        cells = []
        for j, cls, word in ((idx - 1, "pn-prev", "Previous"), (idx + 1, "pn-next", "Next")):
            if 0 <= j < len(seq):
                p = seq[j][0]
                cells.append(f'<a class="pn {cls} int" href="{base}{page_path(course, topic, p)}">'
                             f'<span>{word}</span>{e(page_of(topic, p)["title"])}</a>')
            else:
                cells.append('<span class="pn-gap"></span>')
        navs.append(f'<div class="runnav" data-run="{e(r["id"])}" hidden>'
                    f'<p class="runnav-h">{e(r["name"])} run &middot; {e(seq[idx][1])} '
                    '<button type="button" class="run-off">Show every lesson in order</button></p>'
                    f'<nav class="prevnext" aria-label="{e(r["name"])} run">{"".join(cells)}</nav></div>')
    return "".join(navs)


# --------------------------------------------------------------- beat grid


def beatgrid_svg(block):
    """Four bars of drum grid with the chord blocks drawn above it.

    A student who has just watched a multitrack tutorial can record two layers and
    still have no picture of what "line them up" means. The thing being taught is
    a spatial relationship, so it is drawn. The grid is described in data (rows of
    sixteen hits, and a chord per bar), so a later lesson can draw a different
    groove without touching this function.
    """
    rows = block["rows"]
    chords = block["chords"]
    bars, per_bar = 4, 4
    steps = bars * per_bar
    lab_w, cell, row_h = 108, 44, 40
    top = 66
    w = lab_w + steps * cell
    h = top + len(rows) * row_h + 34

    p = ['<text x="0" y="16" class="bg-lab" font-size="15">Chords</text>']
    # One block per bar, each landing exactly on beat 1, which is the whole claim
    # the diagram is making.
    for i, ch in enumerate(chords):
        x = lab_w + i * per_bar * cell
        p.append(f'<rect x="{x + 2}" y="24" width="{per_bar * cell - 4}" height="34" rx="6" class="bg-chord"/>')
        p.append(f'<text x="{x + per_bar * cell / 2}" y="47" class="bg-ch" font-size="20">{e(ch)}</text>')
    for r, row in enumerate(rows):
        y = top + r * row_h
        p.append(f'<text x="0" y="{y + 26}" class="bg-lab" font-size="15">{e(row["name"])}</text>')
        for s in range(steps):
            x = lab_w + s * cell
            p.append(f'<rect x="{x}" y="{y + 4}" width="{cell}" height="{row_h - 8}" class="bg-cell"/>')
            if row["hits"][s] == "x":
                p.append(f'<rect x="{x + 8}" y="{y + 12}" width="{cell - 16}" height="{row_h - 24}" rx="3" class="bg-hit"/>')
    # Bar lines run through both the chord band and the drums, because the
    # alignment between them is the point being made.
    bottom = top + len(rows) * row_h
    for b in range(bars + 1):
        x = lab_w + b * per_bar * cell
        p.append(f'<line x1="{x}" y1="20" x2="{x}" y2="{bottom}" class="bg-bar"/>')
    for b in range(bars):
        x = lab_w + b * per_bar * cell + per_bar * cell / 2
        p.append(f'<text x="{x}" y="{bottom + 24}" class="bg-beat" font-size="13">Bar {b + 1}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" class="beatgrid" role="img" '
            f'aria-label="{e(block["alt"])}">{"".join(p)}</svg>')


def beatgrid(block, side=""):
    cap = f'<p class="bg-cap">{S.rich(block["caption"])}</p>' if block.get("caption") else ""
    # A region that clips gets a name, keyboard focus, and a hint in words at the
    # width where it actually clips.
    body = ('<p class="bg-hint fine">Swipe the diagram sideways to see all four bars.</p>'
            f'<div class="bgwrap" role="region" tabindex="0" aria-label="{e(block["alt"])}">'
            f'{beatgrid_svg(block)}</div>{cap}')
    return S.section("beatgrid", "Diagram", "compare", block.get("title") or "Lining the layers up",
                     body, side=side)


# ------------------------------------------------------------------- blocks


def keyword_pairs(block):
    """A definition block carries its terms and one run of text, "Term - meaning.
    Term - meaning." Split it back into pairs for the Key words card."""
    terms = block.get("terms") or []
    text = block.get("text") or ""
    if len(terms) == 1:
        lead = re.match(rf"\s*{re.escape(terms[0])}\s+-\s+", text, re.I)
        return [(terms[0], text[lead.end():] if lead else text)]
    spots = []
    for t in terms:
        m = re.search(rf"(?:^|(?<=\. )){re.escape(t)}\s+-\s+", text, re.I)
        if not m:
            return None
        spots.append((m.start(), m.end(), t))
    spots.sort()
    pairs = []
    for i, (start, end, t) in enumerate(spots):
        stop = spots[i + 1][0] if i + 1 < len(spots) else len(text)
        pairs.append((t, text[end:stop].strip()))
    return pairs


def fill_keys(idx, rows):
    """The old storage name of every box in a fill-in table, in the order the
    shell draws them (row by row, left to right). site.js reads data-old to put
    back anything saved before the move."""
    return [f"{idx}-{ri}-{ci}" for ri, r in enumerate(rows) for ci, c in enumerate(r) if not c]


def tag_fields(markup, keys):
    parts = markup.split('<textarea class="field"')
    assert len(parts) - 1 == len(keys), "fill-in boxes and saved names no longer line up"
    out = parts[0]
    for k, rest in zip(keys, parts[1:]):
        out += f'<textarea class="field" data-old="{k}"' + rest
    return out


def take_side(kind):
    """Section kinds that can hold a side card on a laptop."""
    return kind in ("prose", "explain", "listen", "media", "table", "activity", "list", "beatgrid")


def block_section(b, idx, side=""):
    """One block as one shell section, or "" for a block with nothing to show."""
    t = b["type"]

    if t == "prose":
        if is_placeholder(b.get("text")):
            return S.listen([{"title": "Video for this lesson",
                              "pending": "Not added yet. The video for this lesson is still being chosen."}],
                            label="Watch", side=side)
        return S.learn([b["text"]], title=b.get("title") or b.get("heading"), side=side)

    if t == "explain":
        paras = [p for p in (b.get("paras") or []) if p]
        if not b.get("call") and not paras:
            return ""
        return S.learn(paras, title=b.get("heading"), call=b.get("call"), side=side)

    if t == "listen":
        tracks = [x if isinstance(x, dict) else {"title": x} for x in b["tracks"]]
        if all(is_placeholder(x["title"]) for x in tracks):
            return S.listen([{"title": "Tracks for this lesson",
                              "pending": "Not added yet. The tracks for this lesson are still being chosen."}],
                            title=b.get("heading"), side=side)
        clips = [{"title": x["title"], "embed": x.get("embed"),
                  "pending": "" if x.get("embed") else "Not added yet."} for x in tracks]
        return S.listen(clips, title=b.get("heading"), side=side)

    if t == "media":
        if not b.get("embed"):
            return S.listen([{"title": "Video for this lesson",
                              "pending": "Not added yet. The video for this lesson is still being chosen."}],
                            label="Watch", side=side)
        return S.listen([{"title": "Video for this lesson", "embed": b["embed"]}],
                        label="Watch", brief=b.get("brief", ""), side=side)

    if t == "table":
        rows = [[str(c).strip() for c in r] for r in b["rows"]]
        fillable = any(not c for r in rows for c in r)
        if not fillable:
            return S.compare(b["headers"], rows, title=b.get("heading"), label="Table", side=side)
        markup = S.compare(b["headers"], rows, title=b.get("heading"), label="Fill in",
                           form=True, side=side)
        return tag_fields(markup, fill_keys(idx, rows))

    if t == "activity":
        title = strip_prefix(b.get("title"), "Your task")
        if b.get("items"):
            lis = "".join(f"<li>{S.rich(x)}</li>" for x in b["items"])
            body = (f"<p>{S.rich(b['text'])}</p>" if b.get("text") else "") + f'<ul class="plain-list">{lis}</ul>'
            return S.section("task", "Your task", "task", title, body, side=side)
        return S.task(b.get("text", ""), title=title, side=side)

    if t == "list":
        return S.steps(b["items"], title=b.get("title") or b.get("heading"), label="Step by step", side=side)

    if t == "beatgrid":
        return beatgrid(b, side=side)

    return ""


def end_card(b):
    t = b["type"]
    if t == "support":
        return S.help_card(b["text"], title=strip_prefix(b.get("title"), "Need a hand"))
    if t == "extension":
        return S.further(b["text"])
    if t == "exit":
        return S.exit_ticket(b["text"])
    return None


def lesson_sections(blocks):
    """The blocks in order. Key words wait for the next section that can hold a
    side card; support, extension and the exit ticket go to the end cards."""
    sections, end, keys = [], [], []

    def keys_card():
        pairs = [p for k in keys for p in k]
        return S.keywords_card(pairs) if pairs else ""

    for i, b in enumerate(blocks):
        t = b["type"]
        card = end_card(b)
        if card is not None:
            end.append(card)
            continue
        if t == "definition":
            pairs = keyword_pairs(b)
            if pairs is None:
                # Text that cannot be split back into terms prints as written.
                sections.append(S.section("keys", "Key words", "key", None, f"<p>{S.rich(b['text'])}</p>"))
            else:
                keys.append(pairs)
            continue
        side = ""
        if keys and take_side(t):
            side, keys = keys_card(), []
        html = block_section(b, i, side=side)
        if html:
            sections.append(html)
    if keys:
        # Nothing after them could hold a side card, so they get a card of their own.
        kw = "".join(f'<div class="kw"><dt>{S.rich(k)}</dt><dd>{S.rich(v)}</dd></div>'
                     for pairs in keys for k, v in pairs)
        sections.append(S.section("keys", "Key words", "key", None, f'<div class="keys"><dl>{kw}</dl></div>'))
    return sections, end


# -------------------------------------------------------------------- pages


def topic_schedule(course, topic, base, title="Every lesson"):
    groups = []
    for s in topic["sections"]:
        rows = [{"n": str(l["number"]), "title": l["title"], "href": page_path(course, topic, l["number"]),
                 "meta": l["intention"], "at": bool(l.get("assessed"))} for l in s["lessons"]]
        groups.append((s["name"], rows, f"Lessons {s['from']} to {s['to']}"))
    return S.schedule(groups, base=base, title=title, label="This term",
                      note="Every lesson of the term, in order. Go straight to the one you need.")


def build_topic(site, sh, course, topic):
    base = site["base"]
    total = len(flat_lessons(topic))
    hd = S.head(topic["name"], kicker=topic["term"], meta=f"{topic['subtitle']}. {total} lessons.")

    outs = "".join(f"<li><strong>{e(c)}</strong> {S.rich(t)}</li>" for c, t in topic["outcomes"])
    about = S.section("about", "This unit", "learn", None,
                      S.prose([topic["blurb"], {"h": "The question for this term"}, topic["question"]]),
                      side=S.side_card("Outcomes", "target", f'<ul class="plain outcomes">{outs}</ul>'))

    a = topic["assessment"]
    links = "".join(f'<p><a class="int" href="{base}{page_path(course, topic, p["slug"])}">{e(p["title"])}</a></p>'
                    for p in topic.get("pages", []))
    task = S.section("assess", "Assessment", "assess", a["name"],
                     f'<p class="about">{S.rich(a["detail"])}</p>'
                     f'<dl class="facts"><div><dt>When</dt><dd>{S.rich(a["when"])}</dd></div></dl>'
                     f'{links}<p class="fine">The task notification and submission are in Canvas.</p>')

    body = hd + about + task + runs_html(course, topic, base) + topic_schedule(course, topic, base)
    return S.page(sh, title=topic["name"], body=body, description=topic["blurb"],
                  crumbs=[("Home", "/"), (topic["name"], None)], nav_current=topic["id"], site_js=True)


def build_lesson(site, sh, course, topic, lesson, prev_l, next_l):
    """A numbered lesson, or one of the topic's extra pages (Quiz Revision), which
    sits outside the 25 lessons and so has no number and no plain prev/next; the
    runs are the only way through it."""
    base = site["base"]
    numbered = "number" in lesson
    ref = lesson["number"] if numbered else lesson["slug"]
    total = len(flat_lessons(topic))

    if numbered:
        leg = leg_of(topic, lesson["number"])
        hd = S.head(lesson["title"], kicker=topic["name"], num=lesson["number"],
                    meta=f"Lesson {lesson['number']} of {total}, in {leg['name']}.",
                    chips=("Assessment task",) if lesson.get("assessed") else ())
    else:
        hd = S.head(lesson["title"], kicker=topic["name"], meta="Revision.")

    sections, end = lesson_sections(lesson["blocks"])
    body = S.lesson(hd, S.intent(lesson["intention"], criteria=lesson["criteria"]), sections, end)
    # The run order sits straight above the plain one, which it replaces once chosen.
    if topic.get("runs"):
        body += run_nav_html(course, topic, ref, base)

    def pn(l, word):
        return (f"{word}: Lesson {l['number']}", l["title"], page_path(course, topic, l["number"])) if l else None

    here = f"Lesson {lesson['number']}" if numbered else lesson["title"]
    title = f"Lesson {lesson['number']}: {lesson['title']}" if numbered else lesson["title"]
    extras = S.fold(f"All {total} lessons in {topic['name']}", topic_schedule(course, topic, base))
    return S.page(sh, title=title, body=body, description=lesson["intention"],
                  crumbs=[("Home", "/"), (topic["name"], topic_path(course, topic)), (here, None)],
                  nav_current=topic["id"],
                  prevnext=(pn(prev_l, "Previous"), pn(next_l, "Next")) if numbered else None,
                  extras=extras, site_js=True)


def build_home(site, sh, course, topics):
    hd = S.head(site["title"], meta="Everything we do in class, lesson by lesson. "
                                    "Miss one and you can pick up exactly what the class did.")
    cards = [{"title": t["name"], "href": topic_path(course, t), "kicker": t["term"],
              "text": t["subtitle"], "meta": f"{len(flat_lessons(t))} lessons",
              "open": i == len(topics) - 1} for i, t in enumerate(topics)]
    return S.page(sh, title=site["title"], body=hd + S.card_grid(cards, base=site["base"]),
                  description="Year 8 Music class material, lesson by lesson.", nav_current="home")


# --------------------------------------------------------------------- main


def main():
    site = load("site.json")
    S.set_base(site["base"])
    if len(site["courses"]) != 1:
        raise SystemExit("this build expects one course per site")
    course = load("courses", site["courses"][0], "course.json")
    topics = [load("courses", course["id"], "topics", f"{tid}.json") for tid in course["topics"]]
    nav = [("Home", "/", "home")] + [(t["term"], topic_path(course, t), t["id"]) for t in topics]
    sh = shell_site(site, nav)

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    pages = 0
    cid = course["id"]
    for topic in topics:
        write([cid, topic["id"], "index.html"], build_topic(site, sh, course, topic))
        pages += 1
        lessons = flat_lessons(topic)
        for i, lesson in enumerate(lessons):
            write([cid, topic["id"], f"lesson-{lesson['number']}", "index.html"],
                  build_lesson(site, sh, course, topic, lesson,
                               lessons[i - 1] if i else None,
                               lessons[i + 1] if i + 1 < len(lessons) else None))
            pages += 1
        for extra in topic.get("pages", []):
            write([cid, topic["id"], extra["slug"], "index.html"],
                  build_lesson(site, sh, course, topic, extra, None, None))
            pages += 1

    write(["index.html"], build_home(site, sh, course, topics))
    pages += 1

    shutil.copytree(ASSETS, os.path.join(OUT, "assets"))
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    print(f"built {pages} pages into docs/")


if __name__ == "__main__":
    main()
