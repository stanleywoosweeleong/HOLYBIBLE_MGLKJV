# Ариун Библи — Mongolian Bible PWA

Offline-first Progressive Web App for the Mongolian Bible revision (2026).
Text © the Mongolian Bible translation team. Used with permission.

**Structure verified at build time: 66 books / 1,189 chapters / 31,102 verses.**
The build script refuses to produce output if any of those three numbers is wrong,
and the app refuses to display anything if the downloaded text fails the same check.

---

## Deploying to GitHub Pages

1. Push the contents of this folder to a repository (branch `main`).
2. Settings → Pages → Source: *Deploy from a branch* → `main` / `/ (root)`.
3. Wait for the build, then open `https://<user>.github.io/<repo>/`.

`.nojekyll` is present so GitHub does not filter the `data/` folder.
HTTPS is required for the service worker — GitHub Pages provides it.

### Files

| Path | Purpose |
|---|---|
| `index.html` | App shell, UI, and all logic |
| `data/bible-1.0.1.bin` | Mongolian Bible, gzipped JSON (1.66 MB) |
| `data/kjv.bin` | English KJV, optional download (1.21 MB) |
| `sw.js` | Service worker — precaches all 16 assets |
| `manifest.webmanifest` | Install metadata |
| `icons/` | PWA icons + iOS `apple-touch-icon` |
| `tools/` | The DOCX converter and build script |
| `tester-guide-mn.txt` | Instructions in Mongolian to forward to the team |

## Rebuilding after a text correction

```bash
python3 tools/docx-to-json.py     # DOCX -> out/*.json, aborts on any structural error
python3 tools/build.py            # -> site/ and standalone/, bumps CACHE_VERSION
```

`build.py` writes a fresh shell cache name on every run, so returning users are
prompted to update rather than being served stale text.

### Two caches, deliberately

| Cache | Name | Replaced when |
|---|---|---|
| Shell | `mnbible-shell-<timestamp>` | every build (~110 KB) |
| Text | `mnbible-text-v<VERSION>` | only when `VERSION` changes |

A UI or layout fix costs returning users about 110 KB. The 1.66 MB scripture text is
refetched **only** when you bump `VERSION`, i.e. when the text has actually been
corrected. Do not put the data file back into `SHELL_ASSETS` — that would force a
full re-download on every cosmetic change, which matters on metered mobile data.
Bump `VERSION` in `build.py` when the text itself changes — that also renames
`data/bible-<version>.bin`, which guarantees the new text cannot be served from an
old cache entry.

## The three builds

- **`site/`** — the PWA. Installs to the home screen, updates over the air.
  English is an opt-in download from Settings, not part of the first install.
- **`standalone/…-standalone.html`** — 2.2 MB, Mongolian only. Opens directly from
  `file://`, so it travels by WhatsApp, email, or USB stick with no server and no
  internet at all. For general distribution.
- **`standalone/…-bilingual.html`** — 3.9 MB, both texts embedded, parallel view
  available immediately. Intended for the verification team.

## The English parallel text

Source: KJV (1769 Authorized Version), public domain. Validated at build time
against the same 66 / 1,189 / 31,102 versification as the Mongolian, so verses
pair by index with no mapping table.

In the PWA the English is downloaded on demand and stored in **IndexedDB**, not in
the service worker cache — so it survives app updates instead of being re-downloaded
each time `CACHE_VERSION` changes. The download is verified (decompressed and
counted) *before* it is stored, so a truncated transfer is discarded rather than
kept. Settings has a delete button to reclaim the space.

`kjv.bin` is deliberately **not** version-named. The KJV text will never be revised,
so standalone files handed out today must keep resolving after the Mongolian text is
corrected and `VERSION` is bumped. Do not rename or remove it.

The Mongolian-only standalone fetches the English from the absolute URL

    https://stanleywoosweeleong.github.io/HOLYBIBLE_MGLKJV/data/kjv.bin

set as `PAGES` in `build.py`. Change it there if the repository ever moves.
The optional-download rows hide themselves only when no persistent store is available,
which the app determines by testing (`MSTORE`), not by inspecting the protocol. Current
Chrome does allow IndexedDB on `file://`, so a standalone opened straight from disk can
still keep a download — earlier guidance here that said otherwise was wrong.

The standalone builds carry an inline `data:` favicon. Without one the browser requests
`/favicon.ico`, which on a file origin resolves to `file:///C:/favicon.ico` and logs
"Unsafe attempt to load URL … 'file:' URLs are treated as unique security origins".
Harmless, but it looked like a fault.

Known limitation: this KJV source is plain text and does not carry the italics that
mark translator-supplied words. The Mongolian side does preserve them. If the team
wants the English italics for comparison, a different source text would be needed.

## Installing

- **Android / Chrome** — "Add to Home screen" prompt, or ⋮ → Install app.
- **iOS / Safari** — Share → Add to Home Screen. (iOS only installs from Safari.)
- **Desktop Chrome/Edge** — install icon in the address bar.

After the first load the app is fully offline. The whole download is about 1.9 MB.

## Markers (bookmarks, highlights, notes, tags)

One record per verse, the model used by AndBible and yukuku/androidbible:

    {b, c, v, bm, col, note, tags[], t, m}

`b`/`c` are zero-based book and chapter indices, `v` is the verse number, `col` is
0–10 (0 = no highlight), `t`/`m` are created/modified timestamps.

Ten highlight colours, matching what e-Sword offers:

| | | | |
|---|---|---|---|
| 1 Шар yellow | 2 Ногоон green | 3 Цэнхэр blue | 4 Ягаан pink |
| 5 Улбар шар orange | 6 Улаан red | 7 Нил ягаан violet | 8 Номин teal |
| 9 Цайвар ногоон lime | 10 Саарал grey | | |

**The colours carry no built-in meaning.** The defaults are only the colours' own
names — Шар, Ногоон, Цэнхэр — never categories. One reader marks promises yellow,
another marks commands yellow, and the app must not contradict either. Settings →
🎨 Өнгөний нэр lets each colour be named by the reader ("Амлалт", "Тушаал",
"Залбирал"); those names then appear under the swatches in the verse editor, as filter
chips in the bookmark manager, and beside each marker in the list. Blank or
whitespace-only entries fall back to the colour name. Stored in `mnbible.colnames`.

**Colours 1–5 keep their original hues.** The five new ones were appended rather than
inserted, so highlights made before this change still display as the reader set them.
Do not reorder this list — `col` is stored as a number, and reordering would silently
repaint every existing highlight in the wrong colour.

Each has a separate night value. Body text contrast is 11.6:1 or better on every day
colour and 7:1 or better on every night colour, so a highlighted verse stays as
readable as an unhighlighted one. Imported `col` values are clamped to 0–10. A record that ends
up with no bookmark, no colour, no note and no tags deletes itself, so the store
never accumulates empty rows.

### Storage

Markers live in **IndexedDB** (`mnbible` database, `marks` store, keyed by `"b:c:v"`).
IndexedDB is blocked on `file://` origins in Chrome, which is exactly how the standalone
build opens, so `localStorage` remains a working fallback — not an error path. The mode
in use is shown in Settings under Хувилбарын мэдээлэл, and both paths are tested.

Migration is automatic and one-way: a bare `[b,c,v]` array or a `{ver:2}` object in
`localStorage` is moved into IndexedDB on first load, and the original is kept as
`mnbible.marks.bak` rather than being thrown away.

### Soft delete

Deleting never destroys anything. `del` holds the deletion timestamp; `0` means live.

- Deleted markers leave the reading view and the main list, and appear under 🗑 Хогийн сав.
- Each can be restored individually, or purged individually, or the whole bin emptied.
- Editing a deleted marker restores it automatically.
- Clearing a marker's last property (no bookmark, no colour, no note, no tags) soft-deletes
  it rather than dropping the row.
- **Nothing is ever auto-purged.** The bin is emptied only when someone explicitly asks.
  A marker made today is still recoverable in ten years unless deliberately purged.

Export includes the bin; import merges by `m` timestamp, so the newer edit wins and
re-importing the same file is harmless.

## Night reading

Two night levels, because a screen bright enough on a bus is too bright in a ger at
night:

| | Background | Text | Contrast |
|---|---|---|---|
| Шөнө · Энгийн | `#12161A` | `#DFE4E8` cool | 14.2:1 |
| Шөнө · Зөөлөн | `#141210` | `#D8CFC0` warm | 12.1:1 |

The soft level warms the whole palette, not just the text — background, rules, links
and the red-letter colour all shift, so nothing stays cold blue against a warm page.
Highlighted verses stay legible on it, 6.5:1 at worst.

Neither uses pure white on pure black: that combination causes halation, where the
text appears to smear, and it is the worst case for reading in the dark. The
brightness control only appears while night mode is on. Stored in `mnbible.dim`.

## Installation guide

Settings carries a per-platform guide above the QR section: Android (Chrome and
Samsung Internet), iPhone/iPad, Windows (Chrome and Edge), Mac (Safari and Chrome),
and an "after installing" tab. Each is written in Mongolian first, then English.

It is deliberately *all* platforms rather than the one the reader is holding. A pastor
with only an iPhone still has to talk a congregation member through installing on
Android, and cannot do that from a guide that detected iOS and hid the rest.

📋 Заавраа хуулах copies the whole thing as plain text for pasting into Messenger or
WhatsApp. `tools/install_guide.py` holds the source; menu paths were checked against
each browser's current wording and will need revisiting as they change.

The iPhone tab carries a red warning that Add to Home Screen is not optional — Safari
deletes a bookmarked site's storage after seven days of no interaction, taking the
reader's highlights and downloads with it.

## Share / QR code

Settings ends with a collapsed **📱 Хуваалцах · QR код** section. Collapsed by default so
nothing is on screen unless someone opens it.

The QR is generated by `build.py` from `PAGES` and inlined as an SVG path (~4 KB, 37×37
modules, error correction M). No image file, no network call, no third-party QR service —
it renders in a hall with no signal.

**🖥 Дэлгэцэнд том харуулах** opens a full-screen projection view: white background
regardless of night mode (projectors need the contrast), QR sized to `min(62vh, 62vw)`,
and the URL in large monospace beneath. Tap anywhere or press Esc to leave. It also
requests browser fullscreen where available, so the address bar disappears.

If the repository URL ever changes, edit `PAGES` in `build.py` — the QR regenerates
automatically. Do not hand-edit the SVG.

## Concordance

**One search box, no modes.** The query decides what it is:

| Typed | Result |
|---|---|
| `Гал 2:20`, `Gal 2:20`, `Ps 23` | the passage, as a card |
| `Jo 3:16` | the candidate books, as buttons |
| `H127`, `G26`, `h0127` | the lexicon entry |
| `Шүтээн` | its inflected forms, then every verse using any of them |
| `бүх үндэстэн` | that phrase, searched literally |
| (empty) | a few example queries |

The three-mode toggle was removed: it made the reader classify their own question
before asking it. A word search now *is* the concordance — forms with counts appear
above the verses, and tapping one narrows to it. With the study pack installed, an
English word also offers the matching Strong's entries at the foot of the results.

The concordance groups a word's inflected forms by **prefix**.

This is the one place Mongolian grammar works in our favour. Its suffixes attach at
the end, so typing `есүс` gathers есүс, есүсийн, есүсийг, есүст, есүсээр, есүстэй and
есүсээс — 7 forms, 980 occurrences — with no stemming rules and no guesswork. Each
form is listed with its own count and can be tapped to narrow to that form alone.

**Prefix matching is mechanical, not semantic.** `хайр` (love) also catches `хайрч`
from Эхлэл 19:3, which is хайрах, to bake. That is why the individual forms are always
shown with counts: the reader can see and exclude a form that does not belong. Do not
"fix" this with a stemmer — a wrong stemmer would hide the evidence instead of showing
it.

Typing Latin letters searches the KJV instead, with the same behaviour (`love` → love,
loved, loveth, lovers, lovest, lovely).

### Implementation

Nothing extra is downloaded. A form→count table is built in the browser on first use,
one book at a time with a yield between so the phone stays responsive and can show a
percentage. Roughly 0.5 s for Mongolian (36,355 distinct forms from 660,693 tokens)
and 0.2 s for English, then cached for the session.

Only the count table is held. Occurrences are found by a single scan when a word is
chosen — about 150–200 ms — which keeps memory small on cheap phones. Displayed
occurrences are capped at 250; the true total is always shown.

## Study pack — Strong's lexicon and KJV word tagging

Optional 2.85 MB download, stored in IndexedDB so it survives app updates. One file,
`data/study.bin`, holding two things:

- **Strong's Hebrew and Greek dictionaries** — 14,197 entries.
- **Word-level Strong's tagging of the KJV** — all 31,102 verses, 349,076 tagged words,
  extracted from CrossWire's KJV2003 SWORD module with `pysword`.

The extractor strips `<note>` and `<title>` before parsing. Without that, study
footnotes leak into the verse text — Genesis 1:4 ended "…from the darkness.the light
from…: Heb. between the light and between the darkness". 5,844 verses were affected.
It also keeps `<transChange type="added">` as italics, which is the KJV's own marking
of translator-supplied words — 21,578 of them — matching the convention the Mongolian
text uses.

### What it does

With the pack installed and the English parallel line showing, every KJV word becomes
tappable. Tapping opens its Strong's entry — lemma, transliteration, pronunciation,
derivation, definition and KJV usage, with cross-reference numbers tappable in turn.
Words translating more than one original word show each entry
(`God` in John 3:16 → G3588 and G2316).

A Strong's number typed in *any* search mode (`H7225`, `h7225`, `H07225`, `G26`) is
recognised and offered to the lexicon rather than reported as not found.

The lexicon is also browsable on its own as the third search mode (📖 Лексикон):
enter a number (`H430`), or an English word to find entries where it appears among the
KJV renderings (`love` → 24 entries).

### The honest limit

Tapping a **Mongolian** word still cannot show a Strong's number. That needs word-level
alignment between this translation and the original languages, which does not exist and
only the translation team could create. The route is Mongolian verse → its KJV line →
tap the English word.

### Licensing

**Read `STUDY-PACK-LICENSE.txt`.** This data is kept as a separate optional file, and
deliberately not merged with the Mongolian text, because the CrossWire KJV module
carries `DistributionLicense=GPL` while its own About text grants "a general public
license to use this text for any purpose". The Mongolian text remains the translation
team's copyright and is unaffected. If certainty is needed before wide distribution,
write to modules@crosswire.org.

Regenerate with `tools/extract-kjv-strongs.py` if the source module is updated.

**When the pack's contents change, bump `STR_KEY` in `build.py`** (currently
`study-v2`). The pack lives in IndexedDB and is never re-fetched while a copy exists
under the same key — so without a bump, everyone who already downloaded it keeps the
old data indefinitely. The app deletes any superseded `study-*` key on next load, so
the stale copy does not linger in storage.

### Wide screens

The sheets were laid out for a phone. On a desktop window their contents are capped at
44rem and centred, and the colour swatch grid at 30rem with a 3.6rem column maximum —
otherwise eleven swatches stretch into full-width bars and the note field becomes an
unreadable single line.

### Reference edge cases

A reference that names a chapter or verse that does not exist says so, giving the real
count, rather than quietly answering with something else:

    Gen 1:200   -> "Эхлэл 1 бүлэгт 200-р шүлэг байхгүй (31 шүлэгтэй)" + the chapter
    Ps 151      -> "Дууллууд номд 151-р бүлэг байхгүй (150 бүлэгтэй)"
    Gal 0:1     -> "Галатиачуудад номд 0-р бүлэг байхгүй (6 бүлэгтэй)"

`Gen 1:200` previously displayed Genesis 1:1 as though that were the answer, because
`refCard` fell back to the first verse when the requested one was out of range. In a
Bible app, silently showing a different verse from the one asked for is worse than
showing nothing. `tools/refcheck.mjs` covers these.

### Form fields

Every `input` and `textarea` carries an `id` and a `name`, including the ten colour-name
fields built at runtime. Without them Chrome reports "A form field element should have
an id or name attribute" ten times in DevTools, and cannot reason about the fields for
autofill or accessibility. The colour fields also set `autocomplete="off"`,
`spellcheck="false"` and an `aria-label`, since a browser suggesting an email address
into a highlight label helps nobody.

## Build checks

`build.py` runs three gates and refuses to write output if any fails:

1. **`node --check`** on every JavaScript payload — syntax only.
2. **`idcheck()`** — every `$("#id")` in the script must have a matching `id="..."`
   somewhere in the file. Added after a silent string-replace miss left a settings
   block out entirely and the resulting null dereference hung the boot screen.
3. **`smoke.js`** — loads the built page in jsdom with real Bible data and exercises
   render, word search, reference lookup in both languages, concordance, lexicon,
   Strong's routing, the book list in both testaments and both sort orders, the chapter
   grid, history, topics, bookmarks, the verse editor, that **every header button opens
   its sheet**, and that **every sheet's close button actually closes it**.

Those last two checks exist because one refactor deleted the `[data-close]` handler,
leaving all seven sheets unclosable, and the same refactor deleted the handlers for
Search, Bookmarks and Settings. In both cases the page still loaded, still rendered,
and `node --check` passed — the buttons simply did nothing. Interaction has to be
exercised, not inspected.

Close is handled by one delegated listener on `document`, not by binding each button at
load, so a sheet added later cannot silently lose it.

The smoke test exists because of a worse failure: a refactor of the navigation cut
from `let pendBook=0;` to `const norm=`, and the concordance and reference-lookup
functions happened to sit between those two markers. They were deleted silently.
`node --check` passed — the file was still valid JavaScript — and the build shipped
with `parseRef` and `runConcordance` undefined, which broke *every* search mode.
Nothing short of running the page could have caught it.

Requires `npm install jsdom`. If jsdom is absent the step is skipped with a notice
rather than failing, so the build still works on a clean machine — but do install it.

## Notes for the next developer

- Verse text is stored as runs: `[verseNumber, [{t, c?, i?}]]`.
  `c:"red"` = words of Christ, `c:"sup"` = KJV supplied words (italic in the source).
- The reader has a toggle to switch both distinctions off for plain reading.
- Search is a linear scan over all 31,102 verses — about 20 ms per language on a
  laptop, because the whole text is already in memory. No index is built or needed.
- Navigation is two steps: ☰ opens the book list, tapping a book opens that book's
  chapter grid, ‹ goes back. The header reference (`Эхлэл 6 ▾`) goes **straight to the
  chapter grid for the book you are in**, which is the common case — you are usually
  moving chapter to chapter within a book, not book to book.
- An earlier single-screen accordion was reverted: it made ☰ and the header reference
  open the same thing, and left the reader scrolling to reach a chapter grid that
  should have been one tap away.
- The book list has Хуучин Гэрээ / Шинэ Гэрээ tabs at the top and the sort control at
  the **bottom**, below the list and behind a rule. Stacking two control rows above the
  books made the screen busy and put a rarely-changed setting in the way of the thing
  the reader came for. Sort options:
  **Уламжлалт** (canonical) or **Цагаан толгойн дараалал** (alphabetical by Mongolian
  name, using `localeCompare(…,"mn")`). The choice is remembered in `mnbible.bookSort`.
  Opening the list starts in whichever testament you are reading.
- The book list is a single column. A two-column grid made the eye zig-zag left-right
  down 39 books; one column reads straight down.
- Red means "you are here": the current book in the list and the current chapter in the
  grid. Both scroll themselves into view. There is no "одоо N" counter — the red row
  already says where you are, and the chapter grid says it again one tap later.
- The ↩ Буцах bars were removed once reading history existed — two ways back to the
  same place is one too many, and they cost a row at the top of both screens.

### Reading history

The clock button in the Номууд bar opens the last 30 days of chapters opened, newest first and
grouped by day (Өнөөдөр / Өчигдөр / date). Tap any entry to go straight back.

**Every destructive action confirms first.** Audited and verified: binning a history
row (names the chapter), purging a marker, binning all markers, emptying either bin,
clearing history, deleting the English download, deleting the study pack, and resetting
colour names. Deleting a download names the size and warns that re-downloading needs
internet — in rural Mongolia that is not a given, and it is the only action here that
cannot be undone offline.

Right-click and swipe-left both confirm, naming the chapter. The bin exists
to recover a considered decision, not to undo a slip — a single right-click that
destroys a row and leaves the reader to go hunting for it is too fast, even when it
is recoverable.

**Destructive actions are never adjacent to close.** The clear/empty button sits in the
body, right-aligned, and relabels itself for the view it is in — a bin icon beside ✕ in
the bar was one fat-finger away from wiping a reader's history. Sheet bars also give
the close button 14px clearance and a divider.

Icons in bars are inline SVG using `currentColor`, not emoji. The emoji clock rendered
flat and unreadable at that size on iOS, and emoji styling varies by platform.

Recorded in `go()` and `step()`, which together cover every way the chapter can
change — the book list, prev/next, search results, reference lookup, bookmarks and
concordance. Re-opening a chapter moves it to the top rather than duplicating it, so
the list stays a set of places rather than a log of taps. Capped at 300 entries and
pruned to 30 days on every read.

Kept in `localStorage` under `mnbible.hist` as
`[book, chapter, verse, timestamp, deletedAt]`. Rows written before soft delete
existed have four elements and are normalised on read. It is deliberately not in
IndexedDB: it is small, and losing it costs nothing.

**Removing entries.** Right-click a row on desktop, or swipe it left on mobile — both
soft-delete it into 🗑 Хогийн сав, the second tab. From there each row can be restored
or purged individually, and 🗑 in the bar empties the bin. Nothing is destroyed until
someone explicitly purges, matching how bookmarks behave.

Revisiting a chapter that sits in the bin lifts it back out automatically, so the bin
never contradicts what the reader is actually doing.

The swipe handler only engages past 12px horizontal with under 24px vertical drift, so
it does not fight normal scrolling, and it sets a flag that suppresses the click that
would otherwise follow.

The intent is sermon use — a pastor moving across books can return to any of them in
two taps without remembering references.

### Themed collections

The theme chips sit behind a collapsed 📑 disclosure, so opening the sheet puts the
reading history immediately in reach. **Choosing a theme collapses the chips again**
and the summary changes to name it — `📑 Тайтгарал — солих` — so the passages start at
the top of the screen instead of below eighteen chips. This matters in use: on a home
visit the pastor is switching themes between houses, and scrolling past the full list
each time wastes the visit. The same sheet carries eighteen curated lists as their own tabs — 380 references,
many of them ranges. The tab strip scrolls horizontally:

Номлол (Mission 30) · Христийн Мэндэлсний Баяр (Nativity 18) · Амилалт (Resurrection
19) · Тайтгарал (Comfort 23) · Эдгэрэл (Healing 21) · Эмгэнэл ба найдвар (Condolence
and hope 22) · Эрх чөлөө ба биеэ захирах (Freedom and self-control 31) · Урам зориг
(Encouragement 21) · Мэргэн ухаан (Wisdom 22) · Санхүү ба
өгөөмөр сэтгэл (Money and generosity 22) · Гэрлэлт ба гэр бүл (Marriage and family
24) · Хүүхэд хүмүүжүүлэх
(Parenting 20) · Залбирал (Prayer 22) · Шинэ итгэгч (New believer 17) · Сайнмэдээ
түгээх (Sharing the gospel 12) · Ариун Ёслол (Holy Communion 19) · Аврал (Salvation
20) · Талархал ба магтаал (Thanksgiving 17)

Comfort, healing and bereavement are separate on purpose: a hospital visit, a funeral
and general discouragement call for different passages, and a pastor should not have
to sort one list under pressure. A verse appearing in two lists — Psalm 147:3 in both
healing and condolence — is correct, not duplication.

**Сайнмэдээ түгээх is ordered, not topical.** It runs Rom 3:23 → 6:23 → 5:8 → John
3:16 → Eph 2:8-9 → Rom 10:9-10 → 10:13 → John 1:12 → Rev 3:20 → 2 Cor 5:17 → Acts
16:31 → 1 John 5:13, so a visitor can hand the phone over and walk down it. Keep that
order if you edit it.

**On the freedom list.** Built for the pastoral reality that alcohol is a serious
matter in Mongolia, and a pastor sitting with a family had nothing to turn to quickly.
It deliberately pairs the plain warnings (Prov 20:1, 23:29-32, Isa 5:11, Eph 5:18) with
deliverance and dignity (Ps 40:1-3, Ps 107:13-16, Isa 61:1, Luke 4:18, John 8:36, Rom
8:1-2) and with practical help (1 Cor 10:13, Gal 5:16-23, James 4:7, 1 John 1:9). A
list of warnings alone would shame rather than free; Rom 8:1 "no condemnation" is there
on purpose.

**On the communion list.** It runs from the Passover token (Ex 12:13-14) through the
three institution accounts (Matt 26, Mark 14, Luke 22) and 1 Cor 11:23-26, includes the
self-examination passage 1 Cor 11:27-29 that precedes the table in most traditions, and
ends at Rev 19:9. Ordering is canonical, so a minister can read straight down it.

**On the marriage list.** It leads with Eph 5:21 (mutual submission) and 5:25 (the
husband's sacrificial love) rather than isolating 5:22, and includes Col 3:19 "be not
bitter against them" and 1 Pet 3:7 "giving honour unto the wife". Selection is the
curator's responsibility even when every verse is Scripture; a list assembled from
submission texts alone would be handed to people it could harm.

Money is built on contentment, honest work, generosity and debt (1 Tim 6:6-10, Heb
13:5, Prov 22:7) rather than promises of increase. If the team wants a different
emphasis, that is theirs to decide — edit `tools/topics.py`.

Every reference was validated twice before shipping — that the chapter and verse
exist, and that the text actually says what the theme claims. Add themes by editing
`topics.py` and re-running `build.py`; the validation runs with it.
- The search box also accepts references in either language — `Gal 2:20`, `Galatians 2:20`,
  `gal2:20`, `1 Cor 13`, `Гал 2:20`, `Дууллууд 23:1`. Book names match by prefix, with an
  abbreviation table in `ABBR` for the ones that are not prefixes (Jn, Mt, Jas, Phm …).
  An ambiguous prefix (`Jo`) offers the candidates as buttons. Enter jumps straight there.
- The search sheet has a scope control (Монгол / English / Хоёул) that appears only
  once the English text is present. Searching English and tapping a result jumps to
  the Mongolian chapter — that is the point of it: find the passage by the English
  you know, then read and check the Mongolian.
- No fonts are bundled. Mongolian Cyrillic renders with the system serif stack.
  If field testing shows problems with ө / ү on any device, subset a WOFF2 and add
  it to `ASSETS` in `sw.js`.
