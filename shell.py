# Copied from music-shell cff34be41f, body c54cb2fdec. Do not edit here: edit Sites/music-shell and run sync.py.
"""The shared page shell for the music sites (Years 8, 9, 10 and 11).

One look, one accent per year group: direction B, Stage Card, chosen 19 October
2026. Warm grey ground, every section a white card with an icon-and-word label,
the title in one solid accent card.

Standard library only, like every build that imports it. Each site's build.py
reads its own data and hands the pieces to the functions here; the shell never
reads a site's data itself. So the data, the URLs and the build-time checks all
stay where they are, and only the markup is shared.

What lives here:

- page()             the frame: head, inside-Canvas mode, bar, crumbs, footer
- lesson()           head card, learning intention, the sections, the end cards
- head(), intent()   the two pieces every lesson opens with
- the components     steps, listen, cues, learn, compare, form, book, task,
                     worked, check, reveal, rubric, help, further, exit_ticket,
                     keep
- hub pieces         schedule, assessment, upto, card_grid, fold
- escape hatches     section() and side_card(), for a site's own furniture

Rules the functions hold so the sites cannot break them:

- Never colour alone. Every section carries an icon and a word.
- Text from data goes through rich() or e(). Nothing from data is trusted markup,
  except the html argument of section() and side_card(), which is the site's
  own generated furniture.
- Links between pages of the site are marked "int". Inside a Canvas frame
  shell.js makes them inert, because the Canvas app hands any in-frame link to
  another page of the site out to Safari.
"""

import html
import re
from datetime import date

E = html.escape


def e(s):
    """Escape. The data mixes straight and curly apostrophes; curl only the ones
    inside a word, so contractions and possessives typeset properly and a
    straight quote round a word is left alone."""
    return re.sub(r"(?<=\w)&#x27;(?=\w)", "’", E(str(s), quote=True))


# Where the site is served from, for links written inside data text. Set once
# by a site's build (set_base) before it renders anything.
LINK_BASE = ""

# [label](/site/relative/path/). The path admits only a slash-led run of
# letters, digits and hyphens, so data can never produce an external
# destination or a javascript: URL.
LINK_RE = re.compile(r"\[([^\[\]]+)\]\((/[A-Za-z0-9/-]*)\)")


def set_base(base):
    """Tell rich() where the site is served from, for in-text links."""
    global LINK_BASE
    LINK_BASE = base


def rich(s):
    """Escape, then the inline marks the data uses: **bold**, _italic_ and
    [label](/a/page/of/this/site/). Unbalanced marks are left alone rather
    than guessed at, so a stray underscore never eats the rest of a paragraph.
    A link is marked "int", so it goes inert inside a Canvas frame."""
    out = e(s)
    for mark, tag in (("**", "strong"), ("_", "em")):
        if mark == "_":
            # Only an underscore at a word edge is a mark; snake_case is not,
            # and neither is a blank to write in ("sounds ___ because").
            out = re.sub(r"(?<![\w])_(?=[^\s_])(.+?)(?<=[^\s_])_(?![\w])", r"<em>\1</em>", out)
            continue
        parts = out.split(mark)
        if len(parts) % 2 == 1:
            out = "".join(p if i % 2 == 0 else f"<{tag}>{p}</{tag}>" for i, p in enumerate(parts))
    return LINK_RE.sub(lambda m: f'<a class="int" href="{LINK_BASE}{m.group(2)}">{m.group(1)}</a>', out)


def mmss(sec):
    """A cue time the way a player writes it: minutes unpadded, seconds padded."""
    sec = int(sec)
    return f"{sec // 60}:{sec % 60:02d}"


# ------------------------------------------------------------------ icons
# Simple stroke icons, so no component relies on colour alone to say what it is.

ICONS = {
    "listen": '<path d="M3 14v-2a9 9 0 0 1 18 0v2"/><rect x="2.5" y="14" width="5" height="7" rx="1.5"/><rect x="16.5" y="14" width="5" height="7" rx="1.5"/>',
    "learn": '<path d="M2 5h7a3 3 0 0 1 3 3v12a2.5 2.5 0 0 0-2.5-2.5H2z"/><path d="M22 5h-7a3 3 0 0 0-3 3v12a2.5 2.5 0 0 1 2.5-2.5H22z"/>',
    "compare": '<rect x="3" y="4" width="18" height="16" rx="1.5"/><path d="M3 9.5h18M12 4v16"/>',
    "book": '<path d="M5 3h12a2 2 0 0 1 2 2v16H7a2 2 0 0 1-2-2z"/><path d="M5 17a2 2 0 0 1 2-2h12"/><path d="M9 7h6M9 10.5h4"/>',
    "task": '<path d="M14.5 4.5l5 5L9 20H4v-5z"/><path d="M12.5 6.5l5 5"/>',
    "worked": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9V16h7v-2.1A6 6 0 0 0 12 3z"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.7 2.7L16.5 9.5"/>',
    "help": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.3a2.6 2.6 0 0 1 5 .9c0 1.8-2.5 2.3-2.5 4"/><circle cx="12" cy="17.3" r=".6" fill="currentColor"/>',
    "further": '<path d="M7 17L17 7M8 7h9v9"/>',
    "exit": '<path d="M3 7a2 2 0 0 0 2-2h14a2 2 0 0 0 2 2v3a2 2 0 0 0 0 4v3a2 2 0 0 0-2 2H5a2 2 0 0 0-2-2v-3a2 2 0 0 0 0-4z"/><path d="M14 5v14" stroke-dasharray="2 2.2"/>',
    "key": '<circle cx="8" cy="15" r="4.5"/><path d="M11.2 11.8L20 3M16.5 6.5l2.5 2.5M14 9l2 2"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2" fill="currentColor"/>',
    "criteria": '<path d="M9 6h11M9 12h11M9 18h11"/><path d="M3.5 6l1.3 1.3L7 5M3.5 12l1.3 1.3L7 11M3.5 18l1.3 1.3L7 17"/>',
    "steps": '<path d="M10 6h10M10 12h10M10 18h10"/><path d="M4 5h1.5v3.5M4 8.5h3M4 11.5h2.5l-2.5 3h3M4 17h3l-1.5 1.5c1 0 1.5.5 1.5 1.2S6.4 21 5.5 21H4"/>',
    "note": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6"/><circle cx="12" cy="7.8" r=".6" fill="currentColor"/>',
    "cues": '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2.5M9.5 2.5h5"/>',
    "kit": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12h18"/>',
    "keep": '<path d="M6 3h12v18l-6-4.5L6 21z"/>',
    "plot": '<rect x="3" y="3" width="18" height="18" rx="1.5"/><circle cx="8" cy="9" r="2"/><circle cx="16" cy="9" r="2"/><path d="M6 16h12"/>',
    "assess": '<rect x="5" y="4" width="14" height="17" rx="1.5"/><path d="M9 4V3h6v1M9 10h6M9 14h6M9 18h3"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    "now": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "works": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2.5"/><path d="M12 3a9 9 0 0 1 9 9"/>',
    "play": '<path d="M8 5.5v13l11-6.5z" fill="currentColor" stroke="none"/>',
}


def icon(name, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


# --------------------------------------------------------------- the frame

# Runs before the stylesheet so a framed page never flashes the site's own
# navigation. Year 8's script, unchanged, tested in the Canvas app 19 October 2026.
FRAMED = """<script>
// Inside a Canvas page, Canvas moves students between lessons. Any link to
// another page of this site would make the Canvas app hand the frame to Safari,
// so the site's own navigation hides. Runs before the stylesheet so it never flashes.
try { if (window.self !== window.top) document.documentElement.classList.add('framed'); }
catch (err) { document.documentElement.classList.add('framed'); }
</script>"""


def page(site, *, title, body, description="", crumbs=None, nav_current=None,
         prevnext=None, extras="", site_css=True, site_js=False, comment=""):
    """A whole page.

    site: dict with base, title (the mark in the bar), year (8, 9, 10 or 11),
      key (a short name for device storage, e.g. "y11-2027"), foot (the footer
      line), nav (list of (label, href, key)), and optionally noindex.
    crumbs: list of (label, href or None), the last one being this page.
    prevnext: (prev, next), each None or (kicker, title, href).
    extras: standalone-only furniture between the page and the footer (Year 11's
      works archive). Hidden inside Canvas.
    """
    base = site["base"]
    robots = '<meta name="robots" content="noindex, nofollow">\n' if site.get("noindex") else ""
    full = e(title) if title == site["title"] else f'{e(title)} | {e(site["title"])}'

    nav = ""
    if site.get("nav"):
        cur = ' aria-current="page"'
        links = "".join(
            f'<a class="int" href="{base}{href}"{cur if key == nav_current else ""}>{e(label)}</a>'
            for label, href, key in site["nav"])
        nav = f'<nav class="bar-nav" aria-label="Site">{links}</nav>'

    trail = ""
    if crumbs:
        parts = []
        for i, (label, href) in enumerate(crumbs):
            if href and i < len(crumbs) - 1:
                parts.append(f'<li><a class="int" href="{base}{href}">{e(label)}</a></li>')
            else:
                parts.append(f'<li><span aria-current="page">{e(label)}</span></li>')
        trail = f'<nav class="crumbs wrap" aria-label="Breadcrumb"><ol>{"".join(parts)}</ol></nav>'

    pn = ""
    if prevnext and any(prevnext):
        cells = []
        for item, cls in zip(prevnext, ("pn-prev", "pn-next")):
            if item:
                k, t, href = item
                cells.append(f'<a class="pn {cls} int" href="{base}{href}"><span>{e(k)}</span>{e(t)}</a>')
            else:
                cells.append('<span class="pn-gap"></span>')
        pn = f'<nav class="prevnext" aria-label="Lessons">{"".join(cells)}</nav>'

    css = f'<link rel="stylesheet" href="{base}/assets/site.css">\n' if site_css else ""
    js = f'<script src="{base}/assets/site.js" defer></script>\n' if site_js else ""
    extras = f'<div class="extras wrap">{extras}</div>\n' if extras else ""
    return f"""<!doctype html>
<html lang="en-AU" data-year="{site['year']}" data-site="{e(site['key'])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{robots}<title>{full}</title>
<meta name="description" content="{e(description)}">
{FRAMED}
<link rel="preload" href="{base}/assets/fonts/bricolage-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{base}/assets/fonts/atkinson-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{base}/assets/shell.css">
{css}</head>
<body>
{comment}<a class="skip" href="#main">Skip to the lesson</a>
<header class="bar"><div class="wrap bar-in"><a class="mark int" href="{base}/"><span class="mark-dot" aria-hidden="true"></span>{e(site['title'])}</a>{nav}</div></header>
{trail}
<main id="main" class="wrap">
{body}
{pn}
</main>
{extras}<footer class="foot"><div class="wrap"><p>{e(site['foot'])}</p><p>Updated {date.today().strftime('%-d %B %Y')}</p></div></footer>
<script src="{base}/assets/shell.js" defer></script>
{js}</body>
</html>
"""


# ------------------------------------------------------------- the lesson


def head(title, *, kicker="", num=None, meta="", chips=()):
    """The one solid accent card. num is the big faded figure; leave it out on
    pages that are not a single lesson. chips are short facts a student acts on
    ("Bring: Headphones")."""
    n = f'<span class="num" aria-hidden="true">{e(num)}</span>' if num is not None else ""
    sr = f'<span class="sr">Lesson {e(num)}: </span>' if num is not None else ""
    k = f'<p class="kicker">{e(kicker)}</p>' if kicker else ""
    m = f'<p class="meta">{e(meta)}</p>' if meta else ""
    c = ("<ul class=\"chips\">" + "".join(f"<li>{e(x)}</li>" for x in chips) + "</ul>") if chips else ""
    return (f'<header class="head{" has-num" if n else ""}">{k}<div class="title-row">{n}'
            f'<h1>{sr}{e(title)}</h1></div>{m}{c}</header>')


def criteria_card(criteria, outcomes=(), extra=""):
    lis = "".join(f'<li><input type="checkbox" id="sc{i}"><label for="sc{i}">{rich(c)}</label></li>'
                  for i, c in enumerate(criteria))
    outs = ""
    if outcomes:
        outs = '<p class="outs"><strong>Outcomes</strong> ' + " ".join(f"<span>{e(o)}</span>" for o in outcomes) + "</p>"
    tick = '<p class="fine">Tick them off as you go.</p>' if criteria else ""
    body = f'<ul class="sc-list">{lis}</ul>{tick}' if criteria else ""
    return side_card("Success criteria", "criteria", f"{body}{outs}{extra}", cls="sc")


def intent(text, *, by_end=None, criteria=(), outcomes=(), side=""):
    """Learning intention, then "By the end you can" and the outcomes, with the
    success criteria beside them. The outcomes sit under the intention rather
    than in the criteria card, so a short intention beside a long list of
    criteria does not leave a white hole. On a phone the criteria follow."""
    sub = f'<p class="intent-sub"><strong>By the end you can:</strong> {rich(by_end)}</p>' if by_end else ""
    outs = ""
    if outcomes:
        outs = '<p class="outs"><strong>Outcomes</strong> ' + " ".join(f"<span>{e(o)}</span>" for o in outcomes) + "</p>"
    card = criteria_card(criteria) if criteria else ""
    return section("intent", "Learning intention", "target", None,
                   f'<p class="intent-text">{rich(text)}</p>{sub}{outs}', side=card + side)


def lesson(head_html, intent_html, sections, end=()):
    """The lesson body: head card, intention, the sections in order, then the
    end cards (Need a hand, Go further, Check yourself, Exit ticket, Worth
    keeping), which pair up on a laptop."""
    end_html = f'<div class="end">{"".join(end)}</div>' if end else ""
    return f'{head_html}<div class="layout">{intent_html}<div class="body">{"".join(sections)}</div>{end_html}</div>'


# ------------------------------------------------------- escape hatches


def section(kind, label, ico, title, html_body, *, side="", sid=None):
    """One white card with its label pill. The building block every component
    uses, and the way a site gets its own furniture into the shared look:
    html_body is trusted markup, so pass only generated HTML, never raw data."""
    t = f'<span class="blk-title">{rich(title)}</span>' if title else ""
    sd = f'<div class="side">{side}</div>' if side else ""
    has = " has-side" if side else ""
    ident = f' id="{e(sid)}"' if sid else ""
    return (f'<section class="blk blk-{e(kind)}{has}"{ident}>'
            f'<h2 class="blk-h"><span class="blk-label">{icon(ico)}<span>{e(label)}</span></span>{t}</h2>'
            f'<div class="blk-body">{html_body}</div>{sd}</section>')


def side_card(label, ico, html_body, *, cls=""):
    """A small grey card that sits beside a section's body on a laptop and under
    it on a phone. Criteria, key words, notes, what to bring, a stage plot."""
    return (f'<section class="card {e(cls)}"><h3 class="mini-h">{icon(ico)}<span>{e(label)}</span></h3>'
            f'{html_body}</section>')


def note_card(title, text):
    return side_card(title or "Note", "note", f"<p>{rich(text)}</p>", cls="note")


def keywords_card(pairs):
    kw = "".join(f'<div class="kw"><dt>{rich(k)}</dt><dd>{rich(v)}</dd></div>' for k, v in pairs)
    return side_card("Key words", "key", f"<dl>{kw}</dl>", cls="keys")


def list_card(label, ico, items, cls=""):
    lis = "".join(f"<li>{rich(i)}</li>" for i in items)
    return side_card(label, ico, f'<ul class="plain">{lis}</ul>', cls=cls)


# ------------------------------------------------------------ components


def steps(items, *, title=None, label="In class", side=""):
    """What happens in the room, in order. An item is a string, or a
    (kind, text) pair when the site tags each step ("In the room")."""
    lis = []
    for it in items:
        if isinstance(it, (tuple, list)):
            kind, text = it
            lis.append(f'<li><div><span class="step-kind">{e(kind)}</span>{rich(text)}</div></li>')
        else:
            lis.append(f"<li><div>{rich(it)}</div></li>")
    return section("steps", label, "steps", title, f'<ol class="steps">{"".join(lis)}</ol>', side=side)


def _watch(vid, at=None):
    t = f"&amp;t={int(at)}s" if at else ""
    return f"https://www.youtube.com/watch?v={e(vid)}{t}"


def clip(title, *, embed=None, by="", meta="", pending=""):
    """One recording. The thumbnail and the name are both the control; shell.js
    unfolds the player in place, one at a time on the page. With scripting off
    both are plain links to the recording. A recording with no verified id keeps
    its card and says so, rather than vanishing."""
    # A space leads each part, so the name, the maker and the caption never run
    # together when a reader or a text extractor ignores the stylesheet.
    by_html = f' <span class="by">{rich(by)}</span>' if by else ""
    meta_html = f' <span class="meta">{e(meta)}</span>' if meta else ""
    if not embed:
        msg = rich(pending) if pending else "Not on the site yet."
        return (f'<figure class="clip noplay"><div class="clip-frame"><p>{msg}</p></div>'
                f'<figcaption><span class="clip-name">{rich(title)}</span>{by_html}{meta_html}</figcaption></figure>')
    vid = e(embed)
    return (f'<figure class="clip" data-yt="{vid}">'
            f'<div class="clip-frame"><img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy">'
            f'<a class="clip-play" href="{_watch(embed)}" tabindex="-1" aria-hidden="true">{icon("play")}</a></div>'
            f'<figcaption><a class="clip-name" href="{_watch(embed)}">'
            f'<span class="sr">Play </span>{rich(title)}</a>{by_html}{meta_html}</figcaption></figure>')


def listen(tracks, *, title=None, label="Listen", brief="", side=""):
    """Recordings to hear. tracks: dicts with title, and optionally embed, by,
    meta, pending."""
    clips = "".join(clip(t["title"], embed=t.get("embed"), by=t.get("by", ""), meta=t.get("meta", ""),
                         pending=t.get("pending", "")) for t in tracks)
    one = " one" if len(tracks) == 1 else ""
    b = f'<p class="brief">{rich(brief)}</p>' if brief else ""
    return section("listen", label, "listen", title, f'{b}<div class="clips{one}">{clips}</div>', side=side)


def _cue_list(w, cues, cls="cue-list"):
    """A cue is (seconds, text), or a dict with at, text and optionally sub, a
    list of finer cues inside it (Year 10 breaks some moments down further)."""
    rows = []
    for c in cues:
        if isinstance(c, dict):
            at, text, sub = c["at"], c["text"], c.get("sub")
        else:
            (at, text), sub = c, None
        inner = _cue_list(w, sub, "cue-list cue-sub") if sub else ""
        rows.append(f'<li><a class="cue" data-at="{int(at)}" href="{_watch(w["embed"], at)}">'
                    f'{mmss(at)}<span class="sr"> into {e(w["title"])}</span></a>'
                    f'<div class="cue-w">{rich(text)}</div>{inner}</li>')
    return f'<ol class="{cls}">{"".join(rows)}</ol>'


def cues(works, *, brief="", title=None, label="Cue sheet"):
    """The moments in a recording worth stopping at. works: dicts with title,
    embed, meta, cues (see _cue_list) and optionally note, a closing line under
    the cues. Each time is a real link to that second; shell.js turns it into a
    seek in the player beside it."""
    blocks = []
    for w in works:
        note = f'<p class="fine cue-note">{rich(w["note"])}</p>' if w.get("note") else ""
        blocks.append(f'<div class="gw">{clip(w["title"], embed=w["embed"], meta=w.get("meta", ""))}'
                      f'<div class="gw-cues">{_cue_list(w, w["cues"])}{note}</div></div>')
    b = f'<p class="brief">{rich(brief)}</p>' if brief else ""
    return section("cues", label, "cues", title, f'{b}<div class="gws">{"".join(blocks)}</div>')


def prose(paras):
    """Paragraphs, subheads and lists. An item is a string (a paragraph), a list
    (a bulleted list), or a dict with one of p, h or ul."""
    out = []
    for p in paras:
        if isinstance(p, dict):
            if "h" in p:
                out.append(f'<h3>{rich(p["h"])}</h3>')
            elif "ul" in p:
                out.append("<ul>" + "".join(f"<li>{rich(x)}</li>" for x in p["ul"]) + "</ul>")
            else:
                out.append(f'<p>{rich(p["p"])}</p>')
        elif isinstance(p, list):
            out.append("<ul>" + "".join(f"<li>{rich(x)}</li>" for x in p) + "</ul>")
        else:
            out.append(f"<p>{rich(p)}</p>")
    return f'<div class="prose">{"".join(out)}</div>'


def learn(paras, *, title=None, call=None, keywords=(), label="Learn", side=""):
    """The taught content, written down. call is the one-line big idea above
    the prose; keywords sit beside it."""
    c = f'<p class="call">{rich(call)}</p>' if call else ""
    kw = keywords_card(keywords) if keywords else ""
    return section("learn", label, "learn", title, c + prose(paras), side=kw + side)


def table(headers, rows, *, form=False):
    """A table whose first column names each row. On a phone a table of three or
    more columns becomes one labelled card per row. form=True turns every empty
    cell into a box a student can type in, kept on their device."""
    th = "".join(f'<th scope="col">{e(h)}</th>' for h in headers)
    trs = []
    for ri, r in enumerate(rows, 1):
        rowname = r[0] or f"row {ri}"
        # A frame can leave the first column for the student too ("Moment",
        # "Track by"), and an empty row head printed as a gap reads as broken.
        if form and not r[0]:
            cells = [f'<th scope="row" data-label="{e(headers[0])}"><textarea class="field" rows="2" '
                     f'aria-label="{e(headers[0])}, {rowname}"></textarea></th>']
        else:
            cells = [f'<th scope="row">{rich(r[0])}</th>']
        for h, c in zip(list(headers[1:]) + [""] * len(r), r[1:]):
            if form and not c:
                cells.append(f'<td data-label="{e(h)}"><textarea class="field" rows="2" '
                             f'aria-label="{e(h)}: {e(rowname)}"></textarea></td>')
            else:
                cells.append(f'<td data-label="{e(h)}">{rich(c)}</td>')
        trs.append("<tr>" + "".join(cells) + "</tr>")
    cls = "tbl tbl-form" if form else "tbl"
    return f'<div class="tbl-wrap"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'


def compare(headers, rows, *, title=None, label="Compare", side="", form=False, brief="", sid=None):
    """A table to read, or with form=True a frame to fill in: every empty cell
    becomes a box. A frame whose cells are all empty is a scaffold, and printed
    as a bare grid it looks broken. brief is a line above the table."""
    body = (f'<p class="brief">{rich(brief)}</p>' if brief else "") + table(headers, rows, form=form)
    if form:
        body += '<p class="fine">Type straight into the boxes. Your answers stay on this device.</p>'
    return section("compare", label, "compare", title, body, side=side, sid=sid)


def form(rows, *, title=None, brief="", label="Fill this in", sid=None, side=""):
    """Questions to answer in boxes, one under another: a proposal, a plan, a
    reflection. rows: (label, question, lines). lines sets the box's height;
    every box is a textarea, so shell.js keeps what is typed on this device."""
    lis = []
    for i, (lab, q, lines) in enumerate(rows):
        lis.append(f'<li><p class="form-lab">{rich(lab)}</p>'
                   f'<p class="form-q">{rich(q)}</p>'
                   f'<textarea class="field" rows="{max(1, int(lines or 1))}" '
                   f'aria-label="{e(lab)}"></textarea></li>')
    body = (f'<p class="brief">{rich(brief)}</p>' if brief else "")
    body += f'<ol class="form-list">{"".join(lis)}</ol>'
    body += '<p class="fine">Type straight into the boxes. Your answers stay on this device.</p>'
    return section("form", label, "task", title, body, side=side, sid=sid)


def book(items, *, title="Write this down", label="In your book"):
    lis = "".join(f"<li>{rich(x)}</li>" for x in items)
    return section("book", label, "book", title, f'<ol class="book-list">{lis}</ol>')


def task(text, *, title=None, form=None, label="Your task", side=""):
    """What students do. form=(headers, rows) adds a table to type into."""
    body = f"<p>{rich(text)}</p>" if text else ""
    if form:
        body += table(form[0], form[1], form=True)
        body += '<p class="fine">Type straight into the boxes. Your answers stay on this device.</p>'
    return section("task", label, "task", title, body, side=side)


def worked(*, question=None, model=None, rungs=(), zero=None, marks=None, lead=None,
           text=None, title=None, labels=("Full-mark answer", "Scores 0"), side=""):
    """A task answered so it earns, shown working. Two forms:

    - full: question, model, rungs [(move, text)], zero (answer, why). labels
      names the two takes, so each site keeps its own wording.
    - short: text, a paragraph that walks through one answer (Year 11).
    """
    if text is not None:
        return section("worked", "Worked example", "worked", title, prose([text]), side=side)
    parts = []
    if question:
        m = f' <span class="marks">{e(marks)}</span>' if marks else ""
        parts.append(f'<p class="wq"><span class="wq-label">Question</span> {rich(question)}{m}</p>')
    if lead:
        parts.append(f"<p>{rich(lead)}</p>")
    parts.append(f'<blockquote class="model"><span class="model-label">{icon("check")}{e(labels[0])}</span>'
                 f'<p>{rich(model)}</p></blockquote>')
    if rungs:
        lis = "".join(f'<li><strong class="rung">{e(mv)}</strong> {rich(t)}</li>' for mv, t in rungs)
        parts.append(f'<ol class="rungs">{lis}</ol>')
    if zero:
        ans, why = zero
        parts.append(f'<div class="zero"><span class="zero-label">{e(labels[1])}</span>'
                     f'<p>{rich(ans)}</p><p class="fine">{rich(why)}</p></div>')
    return section("worked", "Worked example", "worked", title, "".join(parts), side=side)


def reveal(summary, items, *, ordered=False, title=None, label="Check yourself"):
    """One fold holding a list: the answers to a task, or the notes from a
    lesson a student missed. Shut until pressed, so a projected page never
    shows the room the answers while the class is still working."""
    tag = "ol" if ordered else "ul"
    lis = "".join(f"<li>{rich(x)}</li>" for x in items)
    return section("reveal", label, "check", title,
                   f'<details class="reveal"><summary>{rich(summary)}</summary>'
                   f'<{tag} class="reveal-list">{lis}</{tag}></details>')


def rubric(criteria, *, bands=(), title=None, lead="", label="Marking criteria"):
    """How a task is marked. criteria: (name, [(band, description)]). bands:
    (band, mark range) pairs for the whole task, drawn once as a key rather
    than repeated on every criterion. One card per criterion, not a wide
    table, because a five-band table does not survive a phone."""
    key = ""
    if bands:
        key = ('<ul class="band-key">' + "".join(
            f'<li><span class="band">{e(b)}</span>{e(r)}</li>' for b, r in bands) + "</ul>")
    cards = []
    for name, rows in criteria:
        lis = "".join(f'<li><span class="band">{e(b)}</span><span>{rich(t)}</span></li>' for b, t in rows)
        cards.append(f'<li class="crit-card"><h3>{rich(name)}</h3><ul class="bands">{lis}</ul></li>')
    ld = f'<p class="brief">{rich(lead)}</p>' if lead else ""
    return section("rubric", label, "assess", title, f'{ld}{key}<ol class="crit-cards">{"".join(cards)}</ol>')


def check(items, *, title=None, label="Check yourself"):
    """Questions with the answer folded away. items: (question, answer) pairs."""
    lis = "".join(f'<li><details><summary>{rich(q)}</summary><div class="ans">{rich(a)}</div></details></li>'
                  for q, a in items)
    return section("check", label, "check", title, f'<ol class="checks">{lis}</ol>')


def help_card(text, *, title=None):
    return section("help", "Need a hand?", "help", title, f"<p>{rich(text)}</p>")


def further(text, *, title=None):
    return section("further", "Go further", "further", title, f"<p>{rich(text)}</p>")


def exit_ticket(text):
    return section("exit", "Exit ticket", "exit", None, f'<p class="exit-q">{rich(text)}</p>')


def keep(text, *, label="Worth keeping"):
    return section("keep", label, "keep", None, f'<p class="keep-q">{rich(text)}</p>')


# ------------------------------------------------------------- hub pieces


def state_pill(state):
    words = {"now": "Up to here", "next": "Next up", "done": "Done", "at": "Assessment",
             "soon": "Not on the site yet"}
    return f'<span class="pill pill-{state}">{"<i></i>" if state == "now" else ""}{words[state]}</span>'


def schedule(groups, *, base, title=None, label="This term", note=""):
    """Every lesson of a term, grouped (usually by week). groups: list of
    (group label, rows), or (group label, rows, intro) where intro is a line
    under the group's label. A row: dict with n (shown as given, e.g. "02"),
    title, href (site-relative, or None when there is no page yet), meta, at
    (True for an assessment lesson), and state: "now", "next", "done" or None.
    "now" is where the class is up to; it is said in words and marked, never
    marked alone.

    A row may also carry date (YYYY-MM-DD): a checkpoint everyone shares, like
    a depth study's milestones. Its state is worked out from the build date and
    worked out again by shell.js when the page is opened, because a page can sit
    for weeks between builds and a stale "Next up" is worse than none."""
    out = []
    for grp in groups:
        g, rows = grp[0], grp[1]
        intro = grp[2] if len(grp) > 2 else ""
        lis = []
        for r in rows:
            st = r.get("state")
            if st:
                pill = state_pill(st)
            elif r.get("at"):
                pill = state_pill("at")
            else:
                # A dated checkpoint has no page of its own, and that is not news.
                pill = "" if r.get("href") or r.get("date") else state_pill("soon")
            name = (f'<a class="int" href="{base}{r["href"]}">{rich(r["title"])}</a>' if r.get("href")
                    else f'<span>{rich(r["title"])}</span>')
            meta = f'<span class="row-meta">{rich(r["meta"])}</span>' if r.get("meta") else ""
            cur = ' aria-current="step"' if st == "now" else ""
            cls = "row" + (f" row-{st}" if st else "") + (" row-at" if r.get("at") else "")
            dated = f' data-date="{e(r["date"])}"' if r.get("date") else ""
            lis.append(f'<li class="{cls}"{cur}{dated}><span class="row-n">{e(r["n"])}</span>'
                       f'<span class="row-t">{name}{meta}</span>{pill}</li>')
        gh = f'<h3 class="grp">{e(g)}</h3>' if g else ""
        gi = f'<p class="grp-intro">{rich(intro)}</p>' if intro else ""
        out.append(f'<div class="grp-wrap">{gh}{gi}<ol class="rows">{"".join(lis)}</ol></div>')
    n = f'<p class="fine sched-note">{rich(note)}</p>' if note else ""
    return section("schedule", label, "list", title, f'{n}<div class="sched">{"".join(out)}</div>')


def assessment(name, *, kind="", issued="", due="", weighting="", about="",
               where="Task and rubric in Canvas"):
    """The term's task, as facts. about is a sentence or two on what the task is,
    in the words students were given; the task itself always lives in Canvas."""
    facts = [(k, v) for k, v in (("Type", kind), ("Issued", issued), ("Due", due), ("Weighting", weighting)) if v]
    dl = "".join(f"<div><dt>{e(k)}</dt><dd>{rich(v)}</dd></div>" for k, v in facts)
    ab = f'<p class="about">{rich(about)}</p>' if about else ""
    return section("assess", "Assessment", "assess", name,
                   f'{ab}<dl class="facts">{dl}</dl><p class="fine">{e(where)}</p>')


def fold(summary, inner):
    """A card folded shut: a bar that opens on the card inside it. Standalone
    furniture for a long list a student only sometimes needs (the term's lessons
    at the foot of a lesson page). A <details>, so it works with scripting off."""
    return f'<details class="fold"><summary>{e(summary)}</summary>{inner}</details>'


def upto(title, *, base, href=None, kicker="", lead="", links=()):
    """Where the class is up to, as the one card to press first. links: extra
    (label, href) pairs after the main button."""
    t = f'<a class="int" href="{base}{href}">{rich(title)}</a>' if href else rich(title)
    l = f'<p>{rich(lead)}</p>' if lead else ""
    go = f'<a class="btn int" href="{base}{href}">Open the lesson</a>' if href else ""
    more = "".join(f'<a class="btn btn-quiet int" href="{base}{h}">{e(lb)}</a>' for lb, h in links)
    k = f'<span class="upto-k">{e(kicker)}</span>' if kicker else ""
    return section("upto", "Up to here", "now", None,
                   f'{k}<p class="upto-t">{t}</p>{l}<p class="btns">{go}{more}</p>')


def card_grid(cards, *, base):
    """Term or unit cards for a home page, down the page in teaching order.
    cards: dicts with title, href, kicker, text, meta, and open (the current
    one, drawn as the accent card). A grid was tried first and the open card
    spanning the row left the others ragged around it."""
    out = []
    for c in cards:
        cls = "tcard open" if c.get("open") else "tcard"
        k = f'<span class="tcard-k">{e(c["kicker"])}</span>' if c.get("kicker") else ""
        tx = f'<p>{rich(c["text"])}</p>' if c.get("text") else ""
        m = f'<p class="tcard-m">{rich(c["meta"])}</p>' if c.get("meta") else ""
        out.append(f'<a class="{cls} int" href="{base}{c["href"]}">{k}<span class="tcard-t">{e(c["title"])}</span>{tx}{m}</a>')
    return f'<div class="tcards">{"".join(out)}</div>'
