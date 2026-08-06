#!/usr/bin/env python3
"""
Mongolian Bible DOCX -> structured JSON.

Reads word/document.xml, classifies every paragraph, and emits one JSON file per
book plus a manifest. Preserves the two semantic formattings found in the source:
  - grey italic  = KJV "supplied word" (not in the original languages)
  - red          = words of Christ

Fails loudly: any structural anomaly is reported and, if fatal, aborts the write.
"""
import re, json, os, sys, unicodedata
from collections import defaultdict

DOC = 'unpacked/word/document.xml'
OUT = 'out'

# ---------- KJV versification: chapter count per book, in canonical order ----------
KJV_CHAPTERS = [
    50,40,27,36,34,24,21,4,31,24,22,25,29,36,10,13,10,42,150,31,12,8,66,52,5,48,12,
    14,3,9,1,4,7,3,3,3,2,14,4,
    28,16,24,21,28,16,16,13,6,6,4,4,5,3,6,4,3,1,13,5,5,3,5,1,1,1,22
]
ENGLISH = [
    "Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth",
    "1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra",
    "Nehemiah","Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Solomon",
    "Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos",
    "Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah",
    "Malachi","Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians",
    "2 Corinthians","Galatians","Ephesians","Philippians","Colossians",
    "1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon",
    "Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude",
    "Revelation"
]
USFM = ["GEN","EXO","LEV","NUM","DEU","JOS","JDG","RUT","1SA","2SA","1KI","2KI",
    "1CH","2CH","EZR","NEH","EST","JOB","PSA","PRO","ECC","SNG","ISA","JER","LAM",
    "EZK","DAN","HOS","JOL","AMO","OBA","JON","MIC","NAM","HAB","ZEP","HAG","ZEC",
    "MAL","MAT","MRK","LUK","JHN","ACT","ROM","1CO","2CO","GAL","EPH","PHP","COL",
    "1TH","2TH","1TI","2TI","TIT","PHM","HEB","JAS","1PE","2PE","1JN","2JN","3JN",
    "JUD","REV"]

REDS  = {'FF0000','E2322C','C00000'}          # words of Christ (inconsistent in source)
GREYS = {'8B8B8A','3D3D3C','808080','A6A6A6','8C8681','2E2E2D'}  # supplied words

def unescape(s):
    return (s.replace('&lt;','<').replace('&gt;','>')
             .replace('&quot;','"').replace('&apos;',"'").replace('&amp;','&'))

def runs_of(p):
    """Yield (text, superscript, italic, colorclass) for each run, runs merged later."""
    for r in re.findall(r'<w:r(?:\s[^>]*)?>.*?</w:r>', p, re.S):
        texts = re.findall(r'<w:t(?:\s[^>]*)?>(.*?)</w:t>', r, re.S)
        if not texts:
            if '<w:tab/>' in r or '<w:br/>' in r:
                yield (' ', False, False, None)
            continue
        rpr = re.search(r'<w:rPr>.*?</w:rPr>', r, re.S)
        rpr = rpr.group(0) if rpr else ''
        sup = 'w:val="superscript"' in rpr
        ital = '<w:i/>' in rpr
        col = re.search(r'<w:color w:val="([0-9A-Fa-f]{6})"', rpr)
        col = col.group(1).upper() if col else None
        cls = 'red' if col in REDS else ('sup' if col in GREYS else None)
        yield (unescape(''.join(texts)), sup, ital, cls)

def merge(runs):
    """Coalesce adjacent runs that share formatting (Word fragments them by rsid)."""
    out = []
    for t, s, i, c in runs:
        if not t:
            continue
        key = (s, i, c)
        if out and out[-1][0] == key:
            out[-1][1] += t
        else:
            out.append([key, t])
    return out

def main():
    d = open(DOC, encoding='utf-8').read()
    paras = re.findall(r'<w:p\b.*?</w:p>|<w:p\b[^>]*/>', d, re.S)

    def ptxt(x):
        return ''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', x, re.S)).strip()
    toc = []
    for x in paras[:12]:
        t = ptxt(x)
        if t.startswith(('ХУУЧИН ГЭРЭЭ:', 'ШИНЭ ГЭРЭЭ:')):
            toc += [b.strip() for b in t.split(':', 1)[1].split(',') if b.strip()]
    TOC = {re.sub(r'\s+', ' ', b).strip().lower(): b for b in toc}
    SINGLE = {re.sub(r'\s+', ' ', b).strip().lower()
              for b, n in zip(toc, KJV_CHAPTERS) if n == 1}
    print(f'book names in table of contents: {len(TOC)}')

    books, cur, curkey = [], None, None
    problems, repairs = [], []
    byname = {}
    head_re = re.compile(r'^(.+?)\s+(\d+)$')

    def norm(s):
        return re.sub(r'\s+', ' ', s).strip().lower()

    for idx, p in enumerate(paras):
        segs = merge(runs_of(p))
        plain = ''.join(t for _, t in segs).strip()
        if not plain:
            continue
        centred = '<w:jc w:val="center"/>' in p
        bold = '<w:b/>' in p

        if re.fullmatch(r'[\d\s]+', plain) or plain.startswith(('ХУУЧИН ГЭРЭЭ:', 'ШИНЭ ГЭРЭЭ:')):
            continue

        # ---- single-chapter books are headed by the bare name, with no number
        if norm(plain) in SINGLE and norm(plain) not in byname:
            repairs.append(f'p{idx}: heading "{plain}" has no chapter number (single-chapter book)')
            cur = {'name': TOC.get(norm(plain), plain), 'chapters': []}
            books.append(cur); byname[norm(plain)] = cur
            cur['chapters'].append({'c': 1, 'verses': []})
            continue

        # ---- chapter heading: centred/bold, OR text matches "<current book> <n>"
        m = head_re.match(plain)
        if m:
            name, ch = m.group(1).strip(), int(m.group(2))
            key = norm(name)
            known = key in byname or key in TOC
            if centred or bold or known:
                if not (centred or bold):
                    repairs.append(f'p{idx}: heading "{plain}" lost its bold/centre formatting')
                if key in byname and byname[key]['name'] != name:
                    repairs.append(f'p{idx}: book name spelled "{name}", elsewhere "{byname[key]["name"]}"')
                if key not in byname:
                    cur = {'name': name, 'chapters': []}
                    books.append(cur); byname[key] = cur
                else:
                    cur = byname[key]
                curkey = key
                cur['chapters'].append({'c': ch, 'verses': []})
                continue

        if (centred or bold) and norm(plain) in TOC:
            continue

        # ---- verse(s): split on every superscript number, so two verses
        #      sharing one paragraph are still separated
        if cur is None or not cur['chapters']:
            if centred or bold:
                continue
            problems.append(f'p{idx}: text before any chapter heading -> {plain[:50]!r}')
            continue
        verses_here, body, vnum = [], [], None
        for (s, i, c), t in segs:
            if s and t.strip().isdigit():
                if vnum is not None:
                    verses_here.append((vnum, body))
                vnum, body = int(t.strip()), []
            else:
                body.append({'t': t, **({'c': c} if c else {}), **({'i': True} if i and not c else {})})
        if vnum is not None:
            verses_here.append((vnum, body))

        if not verses_here:
            # continuation of the previous verse (stray paragraph break mid-verse)
            ch = cur['chapters'][-1]
            if ch['verses']:
                ch['verses'][-1]['r'].append({'t': ' '})
                ch['verses'][-1]['r'].extend(body)
                repairs.append(f'p{idx}: verse split across a paragraph break in {cur["name"]} {ch["c"]}')
            else:
                problems.append(f'p{idx}: orphan text -> {plain[:50]!r}')
            continue
        if len(verses_here) > 1:
            repairs.append(f'p{idx}: {len(verses_here)} verses share one paragraph in '
                           f'{cur["name"]} {cur["chapters"][-1]["c"]} '
                           f'(v{verses_here[0][0]}-{verses_here[-1][0]})')
        for vn, bd in verses_here:
            cur['chapters'][-1]['verses'].append({'v': vn, 'r': bd})

    # ---------------- validation ----------------
    print(f'books found: {len(books)} (expected 66)')
    total_v = 0
    fatal = []
    for n, b in enumerate(books):
        chs = [c['c'] for c in b['chapters']]
        if chs != list(range(1, len(chs) + 1)):
            fatal.append(f'{b["name"]}: chapter numbers not 1..N -> {chs[:12]}')
        if n < 66 and len(chs) != KJV_CHAPTERS[n]:
            fatal.append(f'{b["name"]}: {len(chs)} chapters, KJV has {KJV_CHAPTERS[n]}')
        for c in b['chapters']:
            vs = [v['v'] for v in c['verses']]
            total_v += len(vs)
            if vs != list(range(1, len(vs) + 1)):
                miss = set(range(1, max(vs) + 1)) - set(vs) if vs else {1}
                dup = {x for x in vs if vs.count(x) > 1}
                fatal.append(f'{b["name"]} {c["c"]}: missing {sorted(miss)} dup {sorted(dup)}')
            for v in c['verses']:
                if not ''.join(r['t'] for r in v['r']).strip():
                    fatal.append(f'{b["name"]} {c["c"]}:{v["v"]}: EMPTY verse')

    print(f'chapters: {sum(len(b["chapters"]) for b in books)} (KJV 1189)')
    print(f'verses:   {total_v} (KJV 31102)')
    print(f'\nauto-repaired source glitches: {len(repairs)}')
    for x in repairs[:40]:
        print('   ~', x)
    print(f'\nunclassified paragraphs: {len(problems)}')
    for x in problems[:15]:
        print('  ', x)
    print(f'\nSTRUCTURAL ERRORS: {len(fatal)}')
    for x in fatal[:40]:
        print('  !', x)

    if fatal and '--force' not in sys.argv:
        print('\nAborting write. Fix the source or pass --force.')
        return 1

    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for n, b in enumerate(books):
        code = USFM[n] if n < 66 else f'X{n}'
        json.dump(b, open(f'{OUT}/{code}.json', 'w', encoding='utf-8'),
                  ensure_ascii=False, separators=(',', ':'))
        manifest.append({'i': n + 1, 'code': code, 'mn': b['name'],
                         'en': ENGLISH[n] if n < 66 else '?',
                         'ch': len(b['chapters']),
                         'v': sum(len(c['verses']) for c in b['chapters'])})
    json.dump({'lang': 'mn', 'books': manifest},
              open(f'{OUT}/manifest.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'\nwrote {len(manifest)} book files to {OUT}/')
    return 0

sys.exit(main())
