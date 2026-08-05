#!/usr/bin/env python3
"""Pull the Year 8 Term 3 lessons out of the Canvas block pages into data JSON.

The Canvas pages are inline-styled exports, but they are consistently built: each
lesson starts at an `<!-- ==== LESSON n ==== -->` comment, and every block inside
it is a div whose first <strong> names the block ("Learning intention", "Your
task", "Exit ticket"). That label is what we classify on, never the colours.

    python3 tools/extract_canvas.py "<path to Term 3 folder>" > out.json

Output is reviewed by hand before it becomes data/. This script is a first pass,
not the authority; the registered program is.
"""

import html
import json
import os
import re
import sys
from html.parser import HTMLParser

LESSON_RE = re.compile(r"<!--\s*=+\s*LESSON\s+(\d+)\s*=+\s*-->", re.I)

# Block types lifted out of the body and rendered from the lesson header instead.
# _heading is deliberately not here: it is consumed by the fold in extract().
CONSUMED = ("_intention", "_criteria", "_question")


class Chunk(HTMLParser):
    """Flatten a fragment into labelled text, list items and tables."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.items = []
        self.tables = []
        self._li = None
        self._tbl = None
        self._row = None
        self._cell = None
        self._strongs = []
        self._summary = []
        self._in_strong = False
        self._in_summary = False

    def handle_starttag(self, tag, attrs):
        if tag == "li":
            self._li = []
        elif tag == "table":
            self._tbl = []
        elif tag == "tr":
            self._row = []
        elif tag in ("td", "th"):
            self._cell = []
        elif tag == "strong":
            self._in_strong = True
            self._strongs.append([])
        elif tag == "summary":
            # <summary> names a <details> block the way <strong> names a div.
            self._in_summary = True
        elif tag == "br":
            self._push("\n")

    def handle_endtag(self, tag):
        if tag == "li" and self._li is not None:
            got = clean("".join(self._li))
            if got:
                self.items.append(got)
            self._li = None
        elif tag == "table" and self._tbl is not None:
            if self._tbl:
                self.tables.append(self._tbl)
            self._tbl = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self._tbl.append(self._row)
            self._row = None
        elif tag in ("td", "th") and self._cell is not None:
            self._row.append(clean("".join(self._cell)))
            self._cell = None
        elif tag == "strong":
            self._in_strong = False
        elif tag == "summary":
            self._in_summary = False

    def handle_data(self, data):
        self._push(data)

    def _push(self, data):
        if self._cell is not None:
            self._cell.append(data)
        elif self._li is not None:
            self._li.append(data)
        else:
            self.text.append(data)
        if self._in_summary:
            self._summary.append(data)
        elif self._in_strong and self._strongs:
            self._strongs[-1].append(data)

    @property
    def label(self):
        """A <details> is named by its summary; anything else by its first <strong>."""
        if self._summary:
            return clean("".join(self._summary))
        return clean("".join(self._strongs[0])) if self._strongs else ""

    @property
    def strongs(self):
        return [clean("".join(s)) for s in self._strongs]

    @property
    def body(self):
        """Everything after the leading label."""
        got = clean("".join(self.text))
        lab = self.label
        if lab and got.startswith(lab):
            got = got[len(lab):]
        return clean(got)


def clean(s):
    s = html.unescape(s)
    s = s.replace("—", " - ").replace("–", "-")
    s = re.sub(r"[ \t\n\r]+", " ", s)
    return s.strip(" \t\n\r-·").strip()


def parse(fragment):
    p = Chunk()
    p.feed(fragment)
    return p


def top_level(fragment):
    """Split a lesson fragment into its top-level <div>, <h3> and <table> chunks."""
    out = []
    depth = 0
    buf = []
    for tok in re.split(r"(<[^>]+>)", fragment):
        if not tok:
            continue
        m = re.match(r"<\s*(/?)\s*(div|table|h3|details)\b", tok, re.I)
        if m:
            closing, _tag = m.group(1), m.group(2).lower()
            if not closing:
                if depth == 0 and buf:
                    out.append("".join(buf))
                    buf = []
                depth += 1
            buf.append(tok)
            if closing:
                depth -= 1
                if depth <= 0:
                    out.append("".join(buf))
                    buf = []
                    depth = 0
            continue
        buf.append(tok)
    if buf:
        out.append("".join(buf))
    return [c for c in out if clean(re.sub(r"<[^>]+>", " ", c))]


def classify(chunk):
    """One top-level chunk to one data block."""
    p = parse(chunk)
    label = p.label
    low = label.lower()
    body = p.body
    is_h3 = bool(re.match(r"\s*<\s*h3\b", chunk, re.I))

    if p.tables:
        head, *rows = p.tables[0]
        return {"type": "table", "headers": head, "rows": rows}

    if low.startswith("learning intention"):
        return {"type": "_intention", "text": body}
    if low.startswith("success criteria"):
        return {"type": "_criteria", "items": p.items or [body]}
    if low.startswith("our question"):
        return {"type": "_question", "text": body}
    if low.startswith("your task"):
        return {"type": "activity", "title": label, "text": body, "items": p.items}
    if low.startswith("exit ticket"):
        return {"type": "exit", "text": body}
    if low.startswith("extension"):
        return {"type": "extension", "text": body, "items": p.items}
    if low.startswith("need a hand"):
        return {"type": "support", "title": label, "text": body, "items": p.items}
    if low.startswith("key word"):
        terms = p.strongs[1:] or [label.split(":", 1)[-1].strip()]
        return {"type": "definition", "terms": terms, "text": body}

    if is_h3:
        return {"type": "_heading", "text": clean(re.sub(r"<[^>]+>", " ", chunk))}

    if p.items:
        return {"type": "list", "title": label, "items": p.items, "text": body}

    text = body or clean(re.sub(r"<[^>]+>", " ", chunk))
    if not text:
        return None
    return {"type": "prose", "title": label, "text": text}


def group_listening(blocks):
    """A run of short "Artist - Track" prose blocks is one listening list.

    The Canvas pages set each track as its own dashed-border div, which reads as
    a list on the page but arrives here as separate blocks.
    """
    def is_track(b):
        """One "Left - Right" line, not a sentence that happens to contain a dash.

        clean() rewrites every em dash as " - ", so "contains a dash" on its own
        matches far too much. Require exactly one separator, both sides filled, a
        short left side, and no sentence punctuation anywhere.
        """
        if b["type"] != "prose" or b.get("title"):
            return False
        text = b.get("text", "")
        if len(text) >= 70 or text.count(" - ") != 1 or re.search(r"[.!?;:]", text):
            return False
        left, right = (s.strip() for s in text.split(" - "))
        return bool(left) and bool(right) and len(left) < 40

    out = []
    run = []

    def flush():
        if len(run) >= 2:
            out.append({
                "type": "listen",
                "heading": run[0].get("heading", ""),
                "tracks": [b["text"] for b in run],
            })
        else:
            out.extend(run)
        run.clear()

    for b in blocks:
        if is_track(b):
            if run and "heading" in b:
                flush()  # a fresh heading ends the previous group and opens a new one
            run.append(b)
            continue
        flush()
        out.append(b)
    flush()
    return out


def extract(path):
    raw = open(path, encoding="utf-8").read()
    parts = LESSON_RE.split(raw)
    lessons = []
    for i in range(1, len(parts), 2):
        number = int(parts[i])
        frag = parts[i + 1]

        title = ""
        blocks = []
        for c in top_level(frag):
            flat = clean(re.sub(r"<[^>]+>", " ", c))
            m = re.match(r"Lesson\s+%d\b[ ·:.-]*(.+)" % number, flat)
            if m and not title:
                title = m.group(1).strip()
                continue
            got = classify(c)
            if got:
                blocks.append(got)

        intention = next((b["text"] for b in blocks if b["type"] == "_intention"), "")
        criteria = next((b["items"] for b in blocks if b["type"] == "_criteria"), [])
        # Drop only the blocks lifted out above. _heading has to survive this far,
        # because the fold below is what consumes it.
        body = [b for b in blocks if b["type"] not in CONSUMED]

        # Fold a bare heading into the block that follows it.
        folded = []
        pending = None
        for b in body:
            if b["type"] == "_heading":
                pending = b["text"]
                continue
            if pending:
                b = dict(b, heading=pending)
                pending = None
            folded.append(b)

        folded = group_listening(folded)

        lessons.append({
            "number": number,
            "title": title,
            "intention": intention,
            "criteria": criteria,
            "blocks": folded,
        })
    return lessons


def main():
    folder = sys.argv[1]
    files = sorted(
        f for f in os.listdir(folder)
        if f.endswith(".html") and "TEACHER MASTER" not in f
    )
    all_lessons = []
    for f in files:
        all_lessons.extend(extract(os.path.join(folder, f)))
    all_lessons.sort(key=lambda l: l["number"])
    json.dump(all_lessons, sys.stdout, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
