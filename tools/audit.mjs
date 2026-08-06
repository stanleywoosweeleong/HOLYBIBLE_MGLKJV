import { JSDOM } from "jsdom";
import fs from "fs"; import zlib from "zlib";
const html = fs.readFileSync('site/index.html','utf8');
const B = JSON.parse(zlib.gunzipSync(fs.readFileSync('site/data/bible-1.0.1.bin')).toString()).books;
const dom = new JSDOM(html,{runScripts:'outside-only',url:'https://example.org/'});
const w = dom.window;
w.indexedDB=undefined; w.fetch=async()=>{throw new Error('offline')};
w.Element.prototype.scrollIntoView=function(){}; w.scrollTo=function(){};
Object.defineProperty(w,'confirm',{configurable:true,writable:true,value:()=>true});
w.__B=B;
const script = html.split('<script>')[1].split('</script>')[0].replace('boot();','');
const probe = `
 B=__B; bi=0; ci=0;
 (async()=>{
  const out=[]; const t=async(n,f)=>{ try{ out.push([n, await f()]) }
    catch(e){ out.push([n,"THREW "+e.message]) } };

  await t("prev at Genesis 1",  ()=>{ bi=0;ci=0; step(-1); return B[bi].en+" "+(ci+1) });
  await t("next at Rev 22",     ()=>{ bi=65;ci=B[65].ch.length-1; step(1); return B[bi].en+" "+(ci+1) });
  await t("next across books",  ()=>{ bi=0;ci=49; step(1); return B[bi].en+" "+(ci+1) });
  await t("prev across books",  ()=>{ bi=1;ci=0; step(-1); return B[bi].en+" "+(ci+1) });

  const pr=s=>{ const r=parseRef(s); return r? (r.hits.length===1
      ? B[r.hits[0]].en+" "+r.ch+(r.vs?":"+r.vs:"") : r.hits.length+" candidates") : "null" };
  await t("ref Ps 151",         ()=>pr("Ps 151"));
  await t("ref Gal 0:1",        ()=>pr("Gal 0:1"));
  await t("ref Gen 1:200",      ()=>pr("Gen 1:200"));
  await t("ref bare 'Gal'",     ()=>pr("Gal"));
  await t("ref '3 John 1'",     ()=>pr("3 John 1"));
  await t("ref 'Обадиа 1'",     ()=>pr("Обадиа 1"));
  await t("card Gen 1:200",     ()=>{ const c=refCard(0,1,200); return c? "card built":"empty (good)" });
  await t("card Ps 151",        ()=>{ const c=refCard(18,151,1); return c? "card built":"empty (good)" });

  await t("search '('",         async()=>{ $("#q").value="("; await runQuery();
                                   return $("#hits").textContent.trim().slice(0,28) });
  await t("search '.*'",        async()=>{ $("#q").value=".*"; await runQuery();
                                   return $("#hits").textContent.trim().slice(0,28) });
  await t("phrase w/ regex ch", async()=>{ $("#q").value="Шүтээн ("; await runQuery();
                                   return $("#hits").textContent.trim().slice(0,28) });

  await t("import garbage",     ()=>{ try{ JSON.parse("{oops") }catch(e){ return "handled" } });
  await t("import bad rows",    ()=>{ const before=MK.length;
      const items=[{b:"x",c:0,v:1},{b:0,c:0,v:1,col:99},{b:0,c:0}];
      let added=0;
      for(const it of items){ if(typeof it.b!=="number"||typeof it.c!=="number"||typeof it.v!=="number") continue;
        const clean={k:mkKey(it.b,it.c,it.v),b:it.b,c:it.c,v:it.v,bm:!!it.bm,
          col:Math.min(10,Math.max(0,+it.col||0)),note:"",tags:[],del:0,t:1,m:1};
        if(!mkFind(it.b,it.c,it.v)){ MK.push(clean); added++ } }
      return "accepted "+added+" of 3, col clamped to "+(MK[MK.length-1]||{}).col });

  await t("history corrupt row",()=>{ store.set("hist",[null,"x",[0,0,1,Date.now()]]);
      return histLoad().length+" survived" });
  await t("marker on gap verse",()=>{ const x=mkFind(99,0,1); return x?"found?!":"null (good)" });
  await t("mkText missing book", ()=>mkText({b:99,c:0,v:1})===""?"empty (good)":"?");
  await t("colLabel out of range",()=>colLabel(99)===""?"empty (good)":colLabel(99));
  await t("topic ref renders",   ()=>{ histView="topic"; topicKey="communion"; buildHist();
                                   return $$("#histList .tpc").length+" rows" });
  return JSON.stringify(out);
 })()
`;
const res = JSON.parse(await w.eval(script + probe));
for (const [n,v] of res) console.log(`  ${String(v).startsWith('THREW')?'!':'.'} ${n.padEnd(22)} ${v}`);
