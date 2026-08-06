#!/usr/bin/env python3
"""
Export the Mongolian Bible to e-Sword and MySword modules.

Outputs (all SQLite, all UTF-8):
  modules/<name>.bbli        e-Sword 11+ / HD / X / Android   (HTML formatting)
  modules/<name>.bblx        same database, older extension   (see note below)
  modules/<name>.bbl.mybible MySword for Android              (theWord formatting)

Both e-Sword extensions carry identical HTML content: e-Sword 11 and later read the
HTML-based module regardless of which of the two extensions it is given, and older
installers only recognise .bblx. Shipping both costs nothing and avoids a support
question.

Formatting carried through from the source document:
  supplied words (grey italic)   -> <i>…</i>          / <FI>…<Fi>
  words of Christ (red)          -> <font color=…>    / <FR>…<Fr>
"""
import json, sqlite3, os, glob, datetime, zipfile, shutil

OUT = "modules"
NAME = "MongolianKJV2026"
DESCRIPTION = "Ариун Библи — Mongolian (KJV 2026 Revision)"
ABBREV = "MNKJV"
INFO = ("Mongolian Bible, 2026 revision of the King James Version.<br>"
        "Text © the Mongolian Bible translation team. Used with permission.<br>"
        "66 books · 1,189 chapters · 31,102 verses (KJV versification).")
RED = "#9B2F2A"

os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ load
mani = json.load(open("out/manifest.json", encoding="utf-8"))["books"]
books = []
for b in mani:
    j = json.load(open(f'out/{b["code"]}.json', encoding="utf-8"))
    books.append(j["chapters"])

nb = len(books)
nc = sum(len(x) for x in books)
nv = sum(len(c["verses"]) for x in books for c in x)
assert (nb, nc, nv) == (66, 1189, 31102), f"REFUSING TO EXPORT: {nb}/{nc}/{nv}"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def coalesce(runs):
    """Merge neighbouring runs that share a style, so the output does not end up
    with <i>word</i><i> </i> where the source happened to split a run."""
    out = []
    for r in runs:
        k = "red" if r.get("c") == "red" else ("i" if (r.get("c") == "sup" or r.get("i")) else "")
        if out and out[-1][0] == k:
            out[-1][1] += r["t"]
        else:
            out.append([k, r["t"]])
    return out


def wrap(runs, red_open, red_close, it_open, it_close, escape):
    parts = []
    for k, t in coalesce(runs):
        # keep leading/trailing spaces outside the tag - tidier and avoids <i> </i>
        lead = t[:len(t) - len(t.lstrip())]
        trail = t[len(t.rstrip()):]
        core = escape(t.strip())
        if not core:
            parts.append(escape(t))
            continue
        if k == "red":
            parts.append(lead + red_open + core + red_close + trail)
        elif k == "i":
            parts.append(lead + it_open + core + it_close + trail)
        else:
            parts.append(escape(lead) + core + escape(trail))
    return "".join(parts).strip()


def as_html(runs):
    return wrap(runs, f'<font color="{RED}">', "</font>", "<i>", "</i>", esc)


def as_theword(runs):
    return wrap(runs, "<FR>", "<Fr>", "<FI>", "<Fi>", lambda t: t)


def rows(fmt):
    for bi, chapters in enumerate(books, start=1):
        for c in chapters:
            for v in c["verses"]:
                yield (bi, c["c"], v["v"], fmt(v["r"]))


# ------------------------------------------------------------------ e-Sword
def build_esword(path):
    if os.path.exists(path):
        os.remove(path)
    db = sqlite3.connect(path)
    db.execute("""CREATE TABLE Details (Description NVARCHAR(250), Abbreviation NVARCHAR(50),
                  Information TEXT, Version INT, Font NVARCHAR(50), RightToLeft BOOL,
                  OT BOOL, NT BOOL, Apocrypha BOOL, Strong BOOL)""")
    # Version 4 tells e-Sword the Scripture column holds HTML rather than RTF
    db.execute("INSERT INTO Details VALUES (?,?,?,?,?,?,?,?,?,?)",
               (DESCRIPTION, ABBREV, INFO, 4, "DEFAULT", 0, 1, 1, 0, 0))
    db.execute("CREATE TABLE Bible (Book INT, Chapter INT, Verse INT, Scripture TEXT)")
    db.executemany("INSERT INTO Bible VALUES (?,?,?,?)", rows(as_html))
    db.execute("CREATE INDEX BookChapterVerseIndex ON Bible (Book, Chapter, Verse)")
    db.commit()
    db.execute("VACUUM")
    db.close()
    return path


# ------------------------------------------------------------------ MySword
def build_mysword(path):
    if os.path.exists(path):
        os.remove(path)
    now = datetime.date.today().isoformat()
    db = sqlite3.connect(path)
    db.execute("""CREATE TABLE Details (Description NVARCHAR(255), Abbreviation NVARCHAR(50),
                  Comments TEXT, Version TEXT, VersionDate DATETIME, PublishDate DATETIME,
                  RightToLeft BOOL, OT BOOL, NT BOOL, Strong BOOL, CustomCSS TEXT)""")
    db.execute("INSERT INTO Details VALUES (?,?,?,?,?,?,?,?,?,?,?)",
               (DESCRIPTION, ABBREV, INFO.replace("<br>", "\n"), "1.0.1", now, now,
                0, 1, 1, 0, ""))
    db.execute("""CREATE TABLE Bible (Book INT, Chapter INT, Verse INT, Scripture TEXT,
                  PRIMARY KEY (Book, Chapter, Verse))""")
    db.executemany("INSERT INTO Bible VALUES (?,?,?,?)", rows(as_theword))
    db.commit()
    db.execute("VACUUM")
    db.close()
    return path


bbli = build_esword(f"{OUT}/{NAME}.bbli")
shutil.copyfile(bbli, f"{OUT}/{NAME}.bblx")
mys = build_mysword(f"{OUT}/{NAME}.bbl.mybible")

# ------------------------------------------------------------------ verify
for p in (f"{OUT}/{NAME}.bbli", f"{OUT}/{NAME}.bblx", mys):
    db = sqlite3.connect(p)
    n = db.execute("SELECT COUNT(*) FROM Bible").fetchone()[0]
    bk = db.execute("SELECT COUNT(DISTINCT Book) FROM Bible").fetchone()[0]
    ch = db.execute("SELECT COUNT(*) FROM (SELECT DISTINCT Book,Chapter FROM Bible)").fetchone()[0]
    d = db.execute("SELECT * FROM Details").fetchone()
    sample = db.execute(
        "SELECT Scripture FROM Bible WHERE Book=43 AND Chapter=3 AND Verse=16").fetchone()[0]
    db.close()
    assert (bk, ch, n) == (66, 1189, 31102), f"{p}: {bk}/{ch}/{n}"
    print(f"{os.path.basename(p):<34} {os.path.getsize(p)/1048576:>5.2f} MB  "
          f"{bk} books / {ch} ch / {n:,} verses")
    print(f"    John 3:16 -> {sample[:78]}")

with zipfile.ZipFile(f"{OUT}/{NAME}-modules.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".zip"):
            continue
        z.write(f"{OUT}/{f}", f)
print(f"\nzip: {os.path.getsize(f'{OUT}/{NAME}-modules.zip')/1048576:.2f} MB")
