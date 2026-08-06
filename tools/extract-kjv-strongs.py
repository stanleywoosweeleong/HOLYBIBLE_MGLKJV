#!/usr/bin/env python3
"""Extract word-level Strong's tagging from the CrossWire KJV SWORD module."""
import re, json, gzip
from pysword.modules import SwordModules

NOTE  = re.compile(r'<note\b.*?</note>', re.S)      # study/translation footnotes
TITLE = re.compile(r'<title\b.*?</title>', re.S)    # editorial section headings
TOKEN = re.compile(r'<(w|transChange)\b([^>]*?)(?:/>|>(.*?)</\1>)', re.S)
STR   = re.compile(r'strong:([HG])0*(\d+)')
TAG   = re.compile(r'<[^>]+>')

def verse_segments(raw):
    raw = TITLE.sub('', NOTE.sub('', raw))
    segs, pos = [], 0
    for m in TOKEN.finditer(raw):
        pre = TAG.sub('', raw[pos:m.start()]); pos = m.end()
        if pre: segs.append([pre, None])
        text = TAG.sub('', m.group(3) or '')
        if not text: continue
        if m.group(1) == 'transChange':
            segs.append([text, None, 1])            # KJV italics: supplied word
        else:
            nums = [g[0] + str(int(g[1])) for g in STR.findall(m.group(2))]
            segs.append([text, nums or None])
    tail = TAG.sub('', raw[pos:])
    if tail: segs.append([tail, None])
    return segs

def build(path="m"):
    mods = SwordModules(path); mods.parse_modules()
    bible = mods.get_bible_from_module('KJV')
    bl = bible._structure.get_books()
    order = list(bl['ot']) + list(bl['nt'])
    assert len(order) == 66
    out, nv, notes = [], 0, 0
    for b in order:
        book = []
        for c in range(1, b.num_chapters + 1):
            vs = []
            for v in range(1, b.chapter_lengths[c - 1] + 1):
                raw = bible.get(books=[b.name], chapters=[c], verses=[v], clean=False)
                if '<note' in raw: notes += 1
                vs.append(verse_segments(raw)); nv += 1
            book.append(vs)
        out.append(book)
    assert nv == 31102, nv
    print(f"verses {nv}  ·  footnotes stripped from {notes} verses")
    return out

if __name__ == "__main__":
    t = build()
    gzip.open('kjvstrongs.gz','wb',9).write(
        json.dumps(t, ensure_ascii=False, separators=(',',':')).encode())
