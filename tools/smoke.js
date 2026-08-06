/* Runs the built page in a real DOM and exercises the features that a syntax
   check cannot reach. Added after a refactor silently deleted parseRef() and
   runConcordance(), which broke every search mode in a shipped build. */
const { JSDOM } = require('jsdom');
const fs = require('fs'), zlib = require('zlib');

const site = process.argv[2] || 'site';
const html = fs.readFileSync(`${site}/index.html`, 'utf8');
const dataFile = fs.readdirSync(`${site}/data`).find(f => f.startsWith('bible-'));
const B = JSON.parse(zlib.gunzipSync(fs.readFileSync(`${site}/data/${dataFile}`)).toString()).books;

const dom = new JSDOM(html, { runScripts: 'outside-only', url: 'https://example.org/' });
const w = dom.window;
w.indexedDB = undefined;
w.fetch = async () => { throw new Error('offline in test') };
w.__B = B;
// jsdom implements neither of these; the app only uses them cosmetically
w.Element.prototype.scrollIntoView = function(){};
w.scrollTo = function(){};

const script = html.split('<script>')[1].split('</script>')[0].replace('boot();', '');

const probe = `
  B = __B; bi = 0; ci = 0;
  (async () => {
    const out = [];
    const panel = () => {
      const h = $("#hits");
      const n = h.querySelectorAll(".cocc").length;
      if (n) return n + " verses";
      const rc = h.querySelector(".refcard");
      if (rc) return "ref " + rc.querySelector("b").textContent.split("\u00b7")[0].trim();
      const opts = h.querySelectorAll("[data-rb]").length;
      if (opts) return opts + " book options";
      if (h.querySelector(".sent")) return "lexicon entry";
      const t = h.textContent.trim();
      return t ? "note: " + t.slice(0, 40) : "";
    };
    const t = async (name, fn) => {
      try { out.push([name, await fn()]) } catch (e) { out.push([name, "THREW " + e.message]) }
    };
    const ask = async s => { $("#q").value = s; concForm = ""; await runQuery(); return panel() };

    await t("render",       () => { applyPrefs(); buildBooks(); render();
                                    return $$("#text .v").length + " verses" });
    await t("word mn",      () => ask("Шүтээн"));
    await t("word forms",   () => { const f = $$("#hits [data-f]").length;
                                    return f + " forms offered" });
    await t("phrase",       () => ask("бүх үндэстэн"));
    await t("ref mn",       () => ask("Гал 2:20"));
    await t("ref en",       () => ask("Gal 2:20"));
    await t("ref ambiguous",() => ask("Jo 3:16"));
    await t("strong",       () => ask("H127"));
    await t("empty",        () => { $("#q").value = ""; return runQuery().then(() =>
                                    $$("#hits [data-q]").length + " examples") });
    await t("books list",   () => { bookTest="ot"; buildBooks();
                                    return $$("#bookList [data-b]").length + " OT books" });
    await t("books NT",     () => { bookTest="nt"; buildBooks();
                                    return $$("#bookList [data-b]").length + " NT books" });
    await t("books alpha",  () => { bookSort="alpha"; buildBooks();
                                    const f=$("#bookList [data-b] b").textContent;
                                    bookSort="trad"; return "first: "+f });
    await t("chapters",     () => { buildChaps(18);
                                    return $$("#chapList [data-c]").length + " chapters" });
    await t("history",      () => { histPush(0,0,1); buildHist();
                                    return $$("#histList .hrow").length + " rows" });
    await t("topics",       () => { histView="topic"; topicKey=TOPICS[0][0]; buildHist();
                                    return $$("#histList .tpc").length + " refs" });
    await t("bookmarks",    () => { mkInit(); mkUpsert(0,0,1,{col:3}); buildMarks();
                                    return $$("#marks .mrow").length + " markers" });
    await t("verse editor", () => { openVerse(1); return $("#vsRef").textContent });
    await t("header buttons", () => {
      // every top-bar button must open its sheet; three lost their handlers once
      const map = [["btnBooks","shBooks"],["curRef","shChap"],["btnSearch","shSearch"],
                   ["btnMarks","shMarks"],["btnSet","shSet"]];
      const dead = [];
      for (const [btn, sheet] of map) {
        closeAll();
        const b = $("#"+btn);
        if (!b) { dead.push(btn+" missing"); continue }
        b.click();
        if (!$("#"+sheet).classList.contains("open")) dead.push(btn);
      }
      closeAll();
      return dead.length ? "DEAD: "+dead.join(", ") : map.length+" open their sheets";
    });
    await t("close buttons", () => {
      // a deleted [data-close] handler once left every sheet unclosable
      const sheets = $$(".sheet");
      let closed = 0;
      for (const sh of sheets) {
        sh.classList.add("open");
        const btn = sh.querySelector("[data-close]");
        if (!btn) continue;
        btn.click();
        if (!sh.classList.contains("open")) closed++;
      }
      return closed + " of " + sheets.length + " sheets close";
    });
    return JSON.stringify(out);
  })()
`;

let results;
(async () => {
try { results = JSON.parse(await w.eval(script + probe)); }
catch (e) { console.error('SMOKE TEST FAILED to run:', e.message); process.exit(1); }

let bad = 0;
for (const [name, val] of results) {
  const ok = !String(val).startsWith('THREW') && val !== '' && !String(val).startsWith('0 ');
  if (!ok) bad++;
  console.log(`  ${ok ? '.' : '!'} ${name.padEnd(14)} ${val}`);
}
if (bad) { console.error(`SMOKE TEST FAILED: ${bad} of ${results.length} checks`); process.exit(1); }
console.log(`  smoke test: ${results.length} checks passed`);
})();
