import { JSDOM } from "jsdom";
import fs from "fs"; import zlib from "zlib";
const html = fs.readFileSync('site/index.html','utf8');
const B = JSON.parse(zlib.gunzipSync(fs.readFileSync('site/data/bible-1.0.1.bin')).toString()).books;
const dom = new JSDOM(html,{runScripts:'outside-only',url:'https://example.org/'});
const w = dom.window;
w.indexedDB=undefined; w.fetch=async()=>{throw new Error('x')};
w.Element.prototype.scrollIntoView=function(){}; w.scrollTo=function(){}; w.__B=B;
const script = html.split('<script>')[1].split('</script>')[0].replace('boot();','');
const probe = `
 B=__B; bi=0; ci=0;
 (async()=>{
   const out=[];
   for(const q of ["Gen 1:200","Gen 1:31","Ps 151","Овадиа 1","Gal 0:1","Иудаас 1:3","Jo 3:16"]){
     $("#q").value=q; await runQuery();
     out.push([q, $("#hits").textContent.replace(/\\s+/g," ").trim().slice(0,95)]);
   }
   return JSON.stringify(out);
 })()
`;
for (const [q,r] of JSON.parse(await w.eval(script+probe)))
  console.log(`  "${q}"`.padEnd(16), r);
