/* Lineage contracts, finite identities, and optional Chromium rendering.
   NODE_PATH must include the installed playwright package for --browser.
   These checks do not certify every scientific claim in the linked literature. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const http = require("node:http");
const {pathToFileURL} = require("node:url");
const root = path.resolve(__dirname, "..");
const read = name => fs.readFileSync(path.join(root, name), "utf8");
const db = JSON.parse(read("data/lineage.json"));
const ids = new Set(db.nodes.map(n=>n.id));
assert.equal(ids.size,db.nodes.length);
const typeIds = new Set(db.relation_types.map(t=>t.id));
assert.deepEqual([...typeIds].sort(),["analogy","documented","foundation","transfer"]);
const pairs = new Set();
for (const n of db.nodes) {
  for (const field of ["title","authors","venue","object","randomness","inherited","boundary","source_url","source_note"])
    assert.ok(n[field],n.id+":"+field);
  assert.match(n.source_url,/^(https:\/\/|#)/);
}
for (const e of db.links) {
  assert.ok(ids.has(e.from)&&ids.has(e.to));
  assert.ok(typeIds.has(e.type));
  const key=e.from+"→"+e.to; assert.ok(!pairs.has(key));pairs.add(key);
  assert.ok(e.text&&e.boundary&&e.evidence.length);
  e.evidence.forEach(s=>assert.ok(ids.has(s.node)&&s.locator));
  if(e.type==="documented")assert.match(e.evidence.map(s=>s.locator).join(" "),/Ref\.|Methods|introduction/);
}
const schultz=db.nodes.find(n=>n.id==="schultz");
assert.equal(schultz.shl,false);
assert.equal(schultz.authors,"Paul Schultz, Peter J. Menck, Jobst Heitzig, Jürgen Kurths");
assert.equal(schultz.doi,"10.1088/1367-2630/aa5a7b");
assert.match(db.nodes.find(n=>n.id==="ibi").authors,/Mi Jin Lee/);
const html=read("index.html");
const lineageHTML=html.slice(html.indexOf('<section id="lineage">'),html.indexOf('<section id="map">'));
const text=JSON.stringify(db)+lineageHTML+read("data/refs.json");
assert.ok(!/10\.1103\/physreve\.111\.014312/i.test(text),"Excluded work must not be reintroduced");
assert.ok(!/Kaleidoscopic reorganization/i.test(text));
for(const obsolete of ["전역 지표에서 국소 지표로","Descent dynamics가 gradient flow","표본 증가가 아니라 rare-event","같은 사상, 다른 질문"])
  assert.ok(!text.includes(obsolete),obsolete);
const bundled={window:{}};
vm.runInNewContext(read("data/offline-data.js"),bundled);
assert.deepEqual(JSON.parse(JSON.stringify(bundled.window.NEI_DATA.lineage)),db);
assert.deepEqual(JSON.parse(JSON.stringify(bundled.window.NEI_DATA.refs)),JSON.parse(read("data/refs.json")));
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-12,JSON.stringify({a,b}));
// CoI = 4 average Bernoulli variance; endpoints and finite samples.
for(const p of [0,.01,.2,.5,.9,1])close(1-(1-2*p)**2,4*p*(1-p));
const runs=[[0,0,1,1],[0,1,0,1],[0,0,0,1],[0,1,1,1],[0,0,0,0]];
for(let i=0;i<4;i++){
  const phis=[];
  for(let j=0;j<4;j++)if(j!==i){
    const b=runs.map(g=>Number(g[i]===g[j]));
    const mean=b.reduce((a,x)=>a+x,0)/b.length;
    const variance=b.reduce((a,x)=>a+(x-mean)**2,0)/b.length;
    close(variance,mean*(1-mean));phis.push(mean);
  }
  close(1-phis.reduce((s,p)=>s+(1-2*p)**2,0)/3,4*phis.reduce((s,p)=>s+p*(1-p),0)/3);
}
// Complete-pair node aggregation preserves the graph average.
const r=[[0,.2,.7],[.2,0,.5],[.7,.5,0]];
close(r.flat().reduce((a,x)=>a+x,0)/6,(r[0][1]+r[0][2]+r[1][2])/3);
const p=1/500;
close((1-p)**500,0.3675112548571586);
assert.equal(Math.ceil(Math.log(.05)/Math.log1p(-p)),1497);
assert.ok((1-p)**1497<=.05 && (1-p)**1496>.05);
console.log("OK: "+db.nodes.length+" papers, "+db.links.length+" typed links, authorship, scope, offline parity, finite identities");

async function browserChecks(){
  const {chromium}=require("playwright");
  const mime={".html":"text/html; charset=utf-8",".js":"application/javascript",".json":"application/json",
    ".css":"text/css",".woff2":"font/woff2",".woff":"font/woff",".ttf":"font/ttf"};
  const server=http.createServer((req,res)=>{
    const raw=decodeURIComponent(new URL(req.url,"http://localhost").pathname);
    const file=path.resolve(root,"."+raw+(raw.endsWith("/")?"index.html":""));
    if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}
    fs.readFile(file,(error,body)=>{
      if(error){res.writeHead(404);res.end();return;}
      res.writeHead(200,{"Content-Type":mime[path.extname(file)]||"application/octet-stream"});res.end(body);
    });
  });
  await new Promise(resolve=>server.listen(0,"127.0.0.1",resolve));
  let browser;
  try{
    browser=await chromium.launch({headless:true,
      ...(process.env.NEI_BROWSER_CHANNEL?{channel:process.env.NEI_BROWSER_CHANNEL}:{})});
    const page=await browser.newPage({viewport:{width:1440,height:1100}});
    const errors=[];
    page.on("pageerror",error=>errors.push(error.message));
    await page.route("https://cdn.jsdelivr.net/**",route=>route.abort());
    const output=path.join(root,"..","output","lineage-review");
    fs.mkdirSync(output,{recursive:true});
    for(const [mode,url] of [
      ["http","http://127.0.0.1:"+server.address().port+"/index.html#lineage"],
      ["file",pathToFileURL(path.join(root,"index.html")).href+"#lineage"]
    ]){
      await page.goto(url,{waitUntil:"load"});
      await page.locator("#lineagec .lin-node").first().waitFor();
      assert.equal(await page.locator("#lineagec .lin-node").count(),db.nodes.length);
      assert.equal(await page.locator("#lineagec .lin-edge-group").count(),db.links.length);
      assert.equal(await page.locator("#lineage .katex-error").count(),0);
      assert.ok(await page.locator("[data-lineage-formula=coi] .katex").count()>=2);
      // Exercise every node and every edge via accessible activation.
      for(const n of db.nodes){
        const button=page.locator('[data-node-id="'+n.id+'"]');
        await button.focus();await button.press("Enter");
        assert.ok((await page.locator("#lineage-panel").innerText()).includes(n.title));
        assert.equal(await page.locator("#lineage-panel .lin-profile dt").count(),4);
        assert.equal(await page.locator("#lineage-panel .katex-error").count(),0);
      }
      for(const e of db.links){
        const button=page.locator('.lin-edge-group[data-from="'+e.from+'"][data-to="'+e.to+'"]');
        await button.focus();await button.press("Enter");
        assert.ok((await page.locator("#lineage-panel").innerText()).includes("Boundary of transfer"));
      }
      for(const type of db.relation_types){
        await page.locator("#lineage-reset").click();
        await page.locator('[data-lineage-type="'+type.id+'"]').click();
        assert.equal(await page.locator("#lineagec .lin-edge-group:not(.filtered)").count(),
          db.links.filter(e=>e.type===type.id).length);
      }
      await page.locator("#lineage-reset").click();
      await page.locator('[data-node-id="schultz"]').focus();
      await page.locator('[data-node-id="schultz"]').press("Enter");
      const schultzText=await page.locator("#lineage-panel").innerText();
      assert.ok(schultzText.includes("Paul Schultz, Peter J. Menck, Jobst Heitzig, Jürgen Kurths"));
      assert.ok(schultzText.includes("Heetae Kim은 공저자가 아니다"));
      await page.locator("#lineage-panel").screenshot({path:path.join(output,"schultz-"+mode+".png")});
      assert.equal(await page.locator("#lineage-panel .lin-type").count()>0,true);
      console.log("OK: "+mode+" rendering, all nodes/edges, four filters, math and author separation");
    }
    await page.locator("#lineage-focus-nei").click();
    await page.locator("#lineagec").screenshot({path:path.join(output,"map-desktop.png")});
    await page.setViewportSize({width:390,height:844});
    await page.locator('[data-node-id="rf"]').focus();
    await page.locator('[data-node-id="rf"]').press("Enter");
    await page.locator("#lineage-panel").screenshot({path:path.join(output,"panel-mobile.png"),style:".gnb{visibility:hidden}"});
    const mobile=await page.locator("#lineage").evaluate(element=>({
      client:element.clientWidth,scroll:element.scrollWidth,right:element.getBoundingClientRect().right,viewport:innerWidth
    }));
    assert.ok(mobile.scroll<=mobile.client+2 && mobile.right<=mobile.viewport+2,
      "Lineage section mobile overflow: "+JSON.stringify(mobile));
    assert.deepEqual(errors,[]);
    console.log("OK: mobile layout and no uncaught browser errors. Screenshots: "+output);
  }finally{
    if(browser)await browser.close();
    await new Promise(resolve=>server.close(resolve));
  }
}
if(process.argv.includes("--browser"))browserChecks().catch(error=>{console.error(error);process.exitCode=1;});
