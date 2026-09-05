/* Verify source provenance and the restricted quote renderer. */
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const {createHash}=require("node:crypto");
const root=path.resolve(__dirname,"..");
const quote=require(path.join(root,"source-quote.js"));
const katex=require(path.join(root,"vendor/katex/katex.min.js"));
const map=JSON.parse(fs.readFileSync(path.join(root,"data/source-map.json"),"utf8"));
const arg=process.argv.indexOf("--originals");
const originals=arg>=0?process.argv[arg+1]:null;
const mainArg=process.argv.indexOf("--main-original");
const mainOriginal=mainArg>=0?process.argv[mainArg+1]:null;
assert(mainArg<0||mainOriginal,"--main-original requires a file path");
let passages=0,cards=0;
const errors=[];
for(const source of ["main","si","note"]){
  const data=JSON.parse(fs.readFileSync(path.join(root,"data/source-excerpts-"+source+".json"),"utf8"));
  assert.equal(data.source,source);
  assert.match(data.sha256,/^[a-f0-9]{64}$/);
  let raw,lines;
  const originalFile=source==="main"&&mainOriginal?mainOriginal:
    originals?path.join(originals,map.sources[source].file):null;
  if(originalFile){
    const bytes=fs.readFileSync(originalFile);
    assert.equal(createHash("sha256").update(bytes).digest("hex"),data.sha256,source+" source version");
    raw=bytes.toString("utf8");lines=raw.split(/\r?\n/);
  }
  const eligible=Object.keys(map.nodes).filter(id=>["direct","partial"].includes(map.nodes[id][source].kind));
  for(const id of eligible){
    assert(data.excerpts[id]?.length||data.unresolved?.[id],source+"/"+id+" needs quote or explicit unresolved reason");
  }
  for(const [id,excerpts] of Object.entries(data.excerpts)){
    assert(eligible.includes(id),source+"/"+id+" not marked as covered");
    assert(excerpts.length>0);cards++;
    for(const e of excerpts){
      passages++;
      assert(Number.isInteger(e.start_line)&&e.start_line>0&&e.end_line>=e.start_line);
      assert(typeof e.tex==="string"&&e.tex.trim());
      assert(!/\\note(?:GG|SHL|SHLeng)\b/.test(e.tex),source+"/"+id+" includes a memo");
      if(originalFile){
        const expected=e.start_offset!==undefined?raw.slice(e.start_offset,e.end_offset):
          lines.slice(e.start_line-1,e.end_line).join("\n");
        assert.equal(e.tex,expected,source+"/"+id+" is not verbatim");
        if(e.start_offset!==undefined){
          assert.equal(raw.slice(0,e.start_offset).split("\n").length,e.start_line,source+"/"+id+" start line");
          assert.equal(raw.slice(0,e.end_offset-1).split("\n").length,e.end_line,source+"/"+id+" end line");
        }
      }
      const out=quote.render(e.tex,source,katex);
      if(out.errors.length||out.unknown.length)errors.push({source,id,line:e.start_line,...out});
    }
  }
}
// Source HTML, including content inside TeX text macros, must remain inert.
const malicious=quote.render("\\textbf{<img src=x onerror=alert(1)>} $\\htmlClass{bad}{x}$","main",katex);
assert(!malicious.html.includes("<img"));
const percent=quote.render("Exact \\% sign. % comment","main",katex);
assert(percent.html.includes("Exact % sign."));
assert(!percent.html.includes("comment"));
if(errors.length){
  console.error(JSON.stringify(errors.map(({html,...e})=>e),null,2));process.exitCode=1;
}else console.log("OK: "+cards+" source cards, "+passages+" verbatim passages; renderer passed"+
  (originals?"; all source hashes and exact ranges matched":mainOriginal?
    "; Main source hash, exact ranges and line numbers matched":"; original-file comparison not requested"));
