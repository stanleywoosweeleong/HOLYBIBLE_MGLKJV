#!/usr/bin/env python3
"""
Build the Ариун Библи PWA.

Produces:
  site/                      deployable to GitHub Pages
  standalone/<name>.html     one file, works from file://, for sharing offline

Run after parse_bible.py. Bumps CACHE_VERSION automatically.
"""
import json, gzip, base64, os, shutil, subprocess, datetime, sys, re

VERSION = "1.0.1"
PAGES = "https://stanleywoosweeleong.github.io/HOLYBIBLE_MGLKJV/"
NAMESPACE = "mnbible"
SRC, OUT, JSONDIR = "src", "site", "out"

built = datetime.datetime.now().strftime("%Y-%m-%d")
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
CACHE = f"{NAMESPACE}-shell-{stamp}"
DATA_CACHE = f"{NAMESPACE}-text-v{VERSION}"
DATA_NAME = f"data/bible-{VERSION}.bin"
KJV_NAME  = "data/kjv.bin"
KJV_KEY   = "kjv-1769"
STR_NAME  = "data/study.bin"
STR_KEY   = "study-v2"   # bump whenever study.gz content changes

# ---------------------------------------------------------------- data
manifest_src = json.load(open(f"{JSONDIR}/manifest.json", encoding="utf-8"))
books = []
for b in manifest_src["books"]:
    j = json.load(open(f'{JSONDIR}/{b["code"]}.json', encoding="utf-8"))
    books.append({"c": b["code"], "mn": b["mn"], "en": b["en"],
                  "ch": [[[v["v"], v["r"]] for v in c["verses"]] for c in j["chapters"]]})

nb = len(books)
nc = sum(len(b["ch"]) for b in books)
nv = sum(len(c) for b in books for c in b["ch"])
assert (nb, nc, nv) == (66, 1189, 31102), f"REFUSING TO BUILD: {nb}/{nc}/{nv}"

raw = json.dumps({"books": books}, ensure_ascii=False, separators=(",", ":")).encode()
gz = gzip.compress(raw, 9)

os.makedirs(f"{OUT}/data", exist_ok=True)
open(f"{OUT}/{DATA_NAME}", "wb").write(gz)

# ---- optional English KJV (validated against the same versification) ----
kjv = json.load(open("kjv_plain.json", encoding="utf-8"))
kv = sum(len(c) for b in kjv for c in b)
kc = sum(len(b) for b in kjv)
assert (len(kjv), kc, kv) == (66, 1189, 31102), f"REFUSING TO BUILD KJV: {len(kjv)}/{kc}/{kv}"
kgz = gzip.compress(json.dumps(kjv, ensure_ascii=False, separators=(",", ":")).encode(), 9)
open(f"{OUT}/{KJV_NAME}", "wb").write(kgz)

# ---- Strong's dictionaries (Hebrew + Greek), optional download ----
# Study pack: Strong's Hebrew/Greek dictionaries (Open Scriptures, CC BY-SA) plus the
# word-level Strong's tagging of the KJV extracted from CrossWire's KJV2003 SWORD
# module. See STUDY-PACK-LICENSE.txt - this file is kept separate on purpose.
sgz = open("study.gz", "rb").read()
open(f"{OUT}/{STR_NAME}", "wb").write(sgz)

# ---- prune stale data files from earlier builds ----
# Old shells are never served after an update, and the service worker keeps its own
# copy, so leftovers here are pure repository weight.
keep = {os.path.basename(DATA_NAME), os.path.basename(KJV_NAME),
        os.path.basename(STR_NAME)}
for f in sorted(os.listdir(f"{OUT}/data")):
    if f not in keep:
        os.remove(f"{OUT}/data/{f}")
        print(f"  pruned stale data/{f}")

# ---------------------------------------------------------------- manifest
webmanifest = {
    "name": "Ариун Библи", "short_name": "Библи",
    "description": "Монгол Библи — бүрэн офлайн уншигч",
    "lang": "mn", "dir": "ltr",
    "start_url": "./index.html", "scope": "./",
    "display": "standalone", "orientation": "portrait",
    "background_color": "#1E3D5C", "theme_color": "#1E3D5C",
    "categories": ["books", "education"],
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-256.png", "sizes": "256x256", "type": "image/png"},
        {"src": "icons/icon-384.png", "sizes": "384x384", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icons/maskable-192.png", "sizes": "192x192", "type": "image/png",
         "purpose": "maskable"},
        {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png",
         "purpose": "maskable"},
    ],
}
json.dump(webmanifest, open(f"{OUT}/manifest.webmanifest", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

# ---------------------------------------------------------------- QR code
# Generated at build time and inlined as an SVG path: no network call, no image
# file, works offline in a church hall with no signal.
import qrcode
_q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=1, border=2)
_q.add_data(PAGES)
_q.make(fit=True)
_m = _q.get_matrix()
_n = len(_m)
_d = []
for _y, _row in enumerate(_m):
    _x = 0
    while _x < _n:
        if _row[_x]:
            _run = 1
            while _x + _run < _n and _row[_x + _run]:
                _run += 1
            _d.append(f"M{_x} {_y}h{_run}v1h-{_run}z")
            _x += _run
        else:
            _x += 1
QR_SVG = (f'<svg viewBox="0 0 {_n} {_n}" xmlns="http://www.w3.org/2000/svg" '
          f'shape-rendering="crispEdges" role="img" aria-label="QR">'
          f'<rect width="{_n}" height="{_n}" fill="#fff"/>'
          f'<path d="{"".join(_d)}" fill="#000"/></svg>')

# ---------------------------------------------------------------- index.html
tpl = open(f"{SRC}/index.html", encoding="utf-8").read()
page = (tpl.replace("__VERSION__", VERSION)
           .replace("__BUILT__", built)
           .replace("__DATA_URL__", DATA_NAME)
           .replace("__KJV_URL__", KJV_NAME)
           .replace("__STR_URL__", STR_NAME).replace("__STR_KEY__", STR_KEY)
           .replace("__KJV_KEY__", KJV_KEY)
           .replace("__INLINE_KJV__", "")
           .replace("__QR__", QR_SVG).replace("__URL__", PAGES)
           .replace("__INLINE__", ""))
open(f"{OUT}/index.html", "w", encoding="utf-8").write(page)

# ---------------------------------------------------------------- service worker
assets = ["./", "./index.html", "./manifest.webmanifest", "./favicon.ico"]
assets += [f"./icons/{f}" for f in sorted(os.listdir(f"{OUT}/icons"))]
sw = (open(f"{SRC}/sw.js", encoding="utf-8").read()
      .replace("__CACHE__", CACHE)
      .replace("__DATA_CACHE__", DATA_CACHE)
      .replace("__DATA_ASSET__", f"./{DATA_NAME}")
      .replace("__ASSETS__", json.dumps(assets, indent=2)))
open(f"{OUT}/sw.js", "w", encoding="utf-8").write(sw)

# GitHub Pages: do not run the output through Jekyll
open(f"{OUT}/.nojekyll", "w").write("")

INLINE_ICON = '<link rel="icon" href=\'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="%231E3D5C"/><path d="M13.5 5h5v22h-5z" fill="%23D6B25C"/><path d="M7 11h18v4.5H7z" fill="%23D6B25C"/></svg>\'>'

# ---------------------------------------------------------------- standalone
os.makedirs("standalone", exist_ok=True)
# Standalone filenames carry the build date, so a build after midnight leaves the
# previous day's file sitting there looking current. Clear them out.
for f in sorted(os.listdir("standalone")):
    os.remove(f"standalone/{f}")
    print(f"  pruned stale standalone/{f}")
solo = (tpl.replace("__VERSION__", VERSION + "-standalone")
           .replace("__BUILT__", built)
           .replace("__DATA_URL__", "")
           .replace("__KJV_URL__", PAGES + KJV_NAME)
           .replace("__STR_URL__", PAGES + STR_NAME).replace("__STR_KEY__", STR_KEY)
           .replace("__KJV_KEY__", KJV_KEY)
           .replace("__INLINE_KJV__", "")
           .replace("__QR__", QR_SVG).replace("__URL__", PAGES)
           .replace("__QR__", QR_SVG).replace("__URL__", PAGES)
          .replace("__INLINE__", base64.b64encode(gz).decode()))
# a single file has no manifest, icons or service worker to point at
solo = re.sub(r'\n\s*<link rel="manifest"[^>]*>', "", solo)
solo = re.sub(r'\n\s*<link rel="(icon|apple-touch-icon)"[^>]*>', "", solo)
solo = solo.replace("</title>", "</title>\n" + INLINE_ICON, 1)
solo_path = f"standalone/{datetime.datetime.now():%Y-%m%d}-mongolian-bible-standalone.html"
open(solo_path, "w", encoding="utf-8").write(solo)

# ---- bilingual standalone: both texts embedded, for the verification team ----
duo = (tpl.replace("__VERSION__", VERSION + "-bilingual")
          .replace("__BUILT__", built)
          .replace("__DATA_URL__", "")
          .replace("__KJV_URL__", "")
          .replace("__STR_URL__", PAGES + STR_NAME).replace("__STR_KEY__", STR_KEY)
          .replace("__KJV_KEY__", KJV_KEY)
          .replace("__INLINE_KJV__", base64.b64encode(kgz).decode())
          .replace("__QR__", QR_SVG).replace("__URL__", PAGES)
          .replace("__INLINE__", base64.b64encode(gz).decode()))
duo = re.sub(r'\n\s*<link rel="manifest"[^>]*>', "", duo)
duo = re.sub(r'\n\s*<link rel="(icon|apple-touch-icon)"[^>]*>', "", duo)
duo = duo.replace("</title>", "</title>\n" + INLINE_ICON, 1)
duo_path = f"standalone/{datetime.datetime.now():%Y-%m%d}-mongolian-bible-bilingual.html"
open(duo_path, "w", encoding="utf-8").write(duo)

# ---------------------------------------------------------------- checks
def idcheck(path, label):
    """Every element the script looks up must exist in the markup. A silent
    string-replace miss once left the study-pack settings block out entirely,
    and the resulting null dereference hung the boot screen."""
    html = open(path, encoding="utf-8").read()
    script = html.split("<script>")[1]
    # ids may be in the static markup or created dynamically inside the script,
    # so scan the whole file - what matters is that the id exists somewhere.
    ids = set(re.findall(r'id="([A-Za-z][\w-]*)"', html))
    used = set(re.findall(r'\$\("#([A-Za-z][\w-]*)"\)', script))
    missing = sorted(used - ids)
    if missing:
        raise SystemExit(f"BUILD FAILED - {label} references missing elements: {missing}")
    print(f"  element check {label}: {len(used)} ids, all present")


def jscheck(path, label):
    html = open(path, encoding="utf-8").read()
    js = html.split("<script>")[1].split("</script>")[0]
    js = re.sub(r'const INLINE_DATA="[^"]*";', 'const INLINE_DATA="";', js)
    js = re.sub(r'INLINE_KJV="[^"]*"', 'INLINE_KJV=""', js)
    open("/tmp/_c.js", "w").write(js)
    subprocess.run(["node", "--check", "/tmp/_c.js"], check=True)
    print(f"  node --check {label}: OK")

idcheck(f"{OUT}/index.html", "index.html")
idcheck(solo_path, "standalone")
jscheck(f"{OUT}/index.html", "index.html")
jscheck(solo_path, "standalone")
jscheck(duo_path, "bilingual")
subprocess.run(["node", "--check", f"{OUT}/sw.js"], check=True)
print("  node --check sw.js: OK")

# ---- run the built page in a real DOM: catches what a syntax check cannot ----
try:
    r = subprocess.run(["node", "smoke.js", OUT], capture_output=True, text=True)
    print(r.stdout.rstrip())
    if r.returncode != 0:
        print(r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "")
        raise SystemExit("BUILD FAILED - smoke test")
except FileNotFoundError:
    print("  smoke test: skipped (node_modules/jsdom not installed)")

print(f"\nSHELL cache    {CACHE}")
print(f"TEXT cache     {DATA_CACHE}")
print(f"data mn        {len(gz)/1048576:.2f} MB")
print(f"data en (opt)  {len(kgz)/1048576:.2f} MB")
print(f"study (opt)    {len(sgz)/1048576:.2f} MB")
print(f"bilingual      {os.path.getsize(duo_path)/1048576:.2f} MB  -> {duo_path}")
print(f"standalone     {os.path.getsize(solo_path)/1048576:.2f} MB  -> {solo_path}")
print(f"structure      {nb} books / {nc} chapters / {nv} verses")
