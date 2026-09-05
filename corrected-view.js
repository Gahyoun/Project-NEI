"use strict";

function renderCorrectedStudy(data,gateData){
  const host=document.getElementById("corrected-study-content");
  if(!host || !data) return;

  const protocol=data.protocol||{};
  const sources=Array.isArray(data.sources)?data.sources:[];
  const contrasts=Array.isArray(data.graph_contrasts)?data.graph_contrasts:[];
  const text=v=>esc(v===null || v===undefined ? "—" : String(v));
  const number=v=>{
    if(v===null || v===undefined || v==="") return "withheld";
    const n=Number(v);
    if(!Number.isFinite(n)) return "withheld";
    if(n===0) return "0";
    return Math.abs(n)<.001 || Math.abs(n)>=1e4 ? n.toExponential(3) : n.toFixed(4);
  };
  const interval=v=>Array.isArray(v) && v.length===2 ?
    "["+v.map(number).join(", ")+"]" : "interval unavailable";
  const ratio=v=>Array.isArray(v) ? v.map(x=>{
    const n=Number(x);
    return Number.isFinite(n)?(100*n).toFixed(0)+"%":"—";
  }).join(" / ") : "—";
  const count=(a,b)=>a===null || a===undefined || b===null || b===undefined ?
    "—" : text(a)+"/"+text(b);
  const texNumber=v=>{
    const n=Number(v);
    if(!Number.isFinite(n) || n===0) return Number.isFinite(n)?"0":"\\text{undeclared}";
    const parts=n.toExponential(3).split("e");
    const mantissa=Number(parts[0]);
    const exponent=Number(parts[1]);
    return mantissa===1 ? "10^{"+exponent+"}" : mantissa+"\\times10^{"+exponent+"}";
  };
  const list=v=>Array.isArray(v)?v:(v===null || v===undefined?[]:[v]);
  const byNumericKey=(object,target)=>{
    if(!object || typeof object!=="object") return {};
    const key=Object.keys(object).find(k=>Number(k)===Number(target));
    return key===undefined?{}:object[key];
  };
  const recurrenceFor=g=>byNumericKey(g.recurrence,protocol.epsilon_D);
  const relationLabel=g=>g.kind==="metric_control"?"pairs="+text(g.m):"E="+text(g.m);

  const rows=sources.map(g=>{
    const primary=g.rungs?.primary||{};
    const selected=g.published_primary||{};
    const rec=recurrenceFor(g);
    const control=g.exact_control && selected.selection==="exact_target_control"?selected:null;
    const controlCell=!g.exact_control ? "not applicable" : control ?
      count(control.M_accepted,control.M_attempted)+"<br><span class=\"fine\">"+
      tex("$\\mathcal I_{\\rm ctrl}$")+"="+number(control.nei)+" · "+
      interval(control.bootstrap_percentile95)+"</span>" :
      "withheld<br><span class=\"fine\">A_ctrl summary unavailable</span>";
    const recurrenceCell=rec.classes===null || rec.classes===undefined ? "undefined" :
      text(rec.recurrent_classes)+" / "+text(rec.classes);
    return '<tr><th scope="row">'+text(g.label)+'<br><span class="fine">N='+text(g.n)+
      ', '+relationLabel(g)+' · '+text(g.kind)+'</span></th>'+
      '<td>'+count(primary.M_accepted,primary.M_attempted)+
      '<br><span class="fine">'+tex('$\\alpha_{\\rm num}$')+'='+number(primary.alpha)+'</span></td>'+
      '<td>'+number(primary.nei)+'<br><span class="fine">'+interval(primary.bootstrap_percentile95)+'</span></td>'+
      '<td>'+controlCell+'</td>'+
      '<td>'+number(primary.d_eff_pair_standardized)+'</td>'+
      '<td>'+recurrenceCell+'</td></tr>';
  }).join("");

  const anchorSections=sources.filter(g=>g.null_anchor).map(g=>{
    const rowsForAnchor=contrasts.filter(c=>c.anchor_id===g.id);
    const table=rowsForAnchor.map(c=>{
      const reported=c.publication_status==="reported";
      const status=reported ? "reported · finite-protocol contrast" :
        "withheld · "+text(c.withheld_reason||"requested ensemble incomplete or estimand undefined");
      return '<tr><th scope="row">'+text(c.ensemble)+'</th>'+
        '<td>'+count(c.estimable_graphs,c.requested_graphs)+'</td>'+
        '<td>'+number(c.anchor_nei)+'</td>'+
        '<td>'+(reported?number(c.null_nei_mean):"withheld")+'</td>'+
        '<td>'+(reported?number(c.contrast):"withheld")+'</td>'+
        '<td>'+(reported?interval(c.outer_graph_percentile95):"withheld")+'</td>'+
        '<td>'+(reported?interval(c.nested_resampling95_sensitivity):"withheld")+'</td>'+
        '<td>'+ratio(c.null_acceptance_min_median_max)+'</td>'+
        '<td>'+status+'</td></tr>';
    }).join("")||'<tr><td colspan="9">No declared contrast.</td></tr>';
    const gateRows=(gateData?.rows||[]).filter(r=>r.anchor_id===g.id).map(r=>
      '<tr><th scope="row">'+text(r.ensemble)+'</th><td>'+number(r.tau_g)+'</td>'+
      '<td>'+count(r.anchor_accepted,r.M_attempted_per_graph)+'</td>'+
      '<td>'+count(r.estimable_graphs,r.requested_graphs)+'</td>'+
      '<td>'+ratio(r.null_acceptance_rate_min_median_max)+'</td>'+
      '<td>'+number(r.point_contrast_anchor_minus_null_mean)+'</td></tr>').join('');
    return '<li><details class="proof-note"><summary>'+text(g.label)+' · graph-null contrast</summary>'+
      '<div class="tablewrap"><table><thead><tr><th>Null ensemble</th><th>Estimable / requested</th>'+
      '<th>Anchor NEI</th><th>Mean null NEI</th><th>Anchor − null mean</th>'+
      '<th>Outer null-graph interval</th><th>Nested joint sensitivity</th>'+
      '<th>Null acceptance min / median / max</th><th>Publication status</th>'+
      '</tr></thead><tbody>'+table+'</tbody></table></div>'+
      '<ul class="note-tree fine">'+
      '<li><b>Outer null-graph interval:</b> fixed anchor point estimate − bootstrap null-graph mean. '+
      'Between-null-realization uncertainty only; anchor finite-M uncertainty excluded.</li>'+
      '<li><b>Nested joint sensitivity:</b> anchor run vector, null-graph realization, and within-null run vector의 joint resampling. Primary interval이 아닌 broader sensitivity summary.</li>'+
      '<li>Degree와 degree_long: 각각 100E, 500E attempted-switch finite-time kernels. '+
      'Finite-time uniformity 또는 mixing certificate 없음. Interval은 approximate percentile summary이며 p-value 아님.</li>'+
      '</ul><h4>Prespecified gate sensitivity · descriptive point contrasts</h4>'+
      '<div class="tablewrap"><table><thead><tr><th>Null</th><th>Stationarity gate</th><th>Anchor accepted</th>'+
      '<th>Estimable / requested nulls</th><th>Null acceptance min / median / max</th><th>Anchor − null mean</th>'+
      '</tr></thead><tbody>'+gateRows+'</tbody></table></div>'+
      '<p class="fine">서로 다른 gate의 conditional estimands. 이 sensitivity table에는 CI·p-value 없음. '+
      'Primary gate의 미해결 결과를 느슨한 gate의 결과로 대체하지 않음. '+
      '<a href="data/corrected-gate-sensitivity.json">84-row sensitivity artifact</a>.</p></details></li>';
  }).join("")||'<li>No graph-null anchor in the bounded source set.</li>';

  const tolerance=sources.map(g=>{
    const rungEntries=Object.entries(g.rungs||{});
    const paired=g.paired_rung_contrasts||{};
    const rs=rungEntries.map(([name,r])=>{
      const p=protocol.rungs?.[name]||{};
      const contrast=paired[name];
      return '<tr><th scope="row">'+text(name)+'</th><td>'+number(p.gtol)+' / '+number(p.ftol)+'</td>'+
        '<td>'+count(r.M_accepted,r.M_attempted)+'</td><td>'+number(r.nei)+'</td>'+
        '<td>'+text(JSON.stringify(r.failures||{}))+'</td>'+
        '<td>'+(contrast?interval(contrast.paired_bootstrap_percentile95):'reference')+'</td></tr>';
    }).join("");
    const rec=recurrenceFor(g);
    const sensitivity=Object.entries(g.gate_sensitivity||{}).map(([tau,v])=>
      '<li>Stationarity gate '+text(tau)+': '+count(v.accepted,protocol.M)+' accepted · '+
      tex('$\\mathcal I_{\\rm adm}$')+'='+number(v.nei)+'</li>').join("")||'<li>Unavailable.</li>';
    const rarefaction=Object.entries(g.rarefaction||{}).sort((a,b)=>Number(a[0])-Number(b[0])).map(([m,v])=>
      '<li>M='+text(m)+': '+count(v.accepted,v.attempted)+' accepted · '+
      tex('$\\mathcal I_{\\rm adm}$')+'='+number(v.nei)+'</li>').join("")||'<li>Unavailable.</li>';
    const exactNote=g.exact_control ?
      '<li><b>Exact-control scope:</b> 이 panel의 rung, gate sensitivity, recurrence, '+
      'rarefaction 및 paired-rung contrast는 모두 A_num auxiliary summaries. '+
      'Target calibration은 source table의 A_ctrl만 사용.</li>' : '';
    return '<li><details class="proof-note"><summary>'+text(g.label)+' · tolerance / sampling audit</summary>'+
      '<div class="tablewrap"><table><thead><tr><th>Rung</th><th>gtol / ftol</th><th>A_num</th>'+
      '<th>Conditional NEI | A_num</th><th>Failures (overlap allowed)</th>'+
      '<th>Rung − primary interval | A_num</th></tr></thead><tbody>'+rs+'</tbody></table></div>'+
      '<h4>Prespecified gate sensitivity · A_num</h4><ul class="note-tree">'+sensitivity+'</ul>'+
      '<h4>M-rarefaction · primary rung, A_num</h4><ul class="note-tree">'+rarefaction+'</ul>'+
      '<h4>Independent-batch recurrence · primary rung, A_num</h4>'+
      '<ul class="note-tree"><li>Discovery/validation accepted: '+text(rec.discovery_accepted)+' / '+
      text(rec.validation_accepted)+'. Recurrent/discovery classes: '+text(rec.recurrent_classes)+' / '+
      text(rec.classes)+'. Validation unmatched: '+text(rec.unmatched)+', ambiguous: '+text(rec.ambiguous)+'.</li>'+
      '<li>Frozen complete-link discovery classes. Validation의 unique all-member match만 recurrence로 집계. '+
      'Basin certificate 또는 complete-support census 아님.</li>'+exactNote+'</ul>'+
      '<p class="fine">Gate 변경은 서로 다른 conditional law의 sensitivity analysis. '+
      'Same-start rung pairing은 각 accepted law의 별도 renormalization. Paired interval은 두 arm의 accepted count가 모두 2 이상인 bootstrap replicate에 조건부이며 valid fraction 95% 미만이면 withheld. Primary estimand의 대체 없음.</p>'+
      '</details></li>';
  }).join("");

  const audit=data.artifact_audit||{};
  const auditPass=audit.status==="pass" && audit.config_sha256===data.config_sha256;
  const auditText=auditPass ?
    'pass · protocol hash match · '+text(audit.graphs)+' instances, '+text(audit.attempts)+
    ' attempted run artifacts, '+text(audit.terminals)+' terminal optimizations' :
    (audit.status?text(audit.status)+' · protocol-hash match not established':'not included in public payload');
  const nullDiagnostics=data.null_diagnostics_summary||{};
  const mixing=nullDiagnostics.finite_time_degree_mixing_certified===true?"certified":"not certified";
  const gnmIncomplete=nullDiagnostics.gnm_incomplete_any_anchor===true?"yes":
    (nullDiagnostics.gnm_incomplete_any_anchor===false?"no":"unavailable");
  const failures=Array.isArray(data.null_generation_failures)?data.null_generation_failures.length:0;
  const batchSize=protocol.batch_size;
  const bootstrap=protocol.bootstrap_repetitions;
  const fixedGate=tex('$\\eta_g\\le '+texNumber(protocol.tau_g)+
    ',\\;\\chi_{\\rm coll}\\ge '+texNumber(protocol.tau_c)+
    ',\\;\\tau_H^{\\rm rel}='+texNumber(protocol.tau_h_rel)+'$');
  const controlGate=tex('$\\phi\\le '+texNumber(protocol.tau_phi)+'$');
  const epsilon=tex('$\\varepsilon_D='+texNumber(protocol.epsilon_D)+'$');
  const limitItems=list(data.interpretation_limits).concat(list(data.outstanding));

  host.innerHTML=
    '<p class="lede"><b>'+text(data.status)+'</b></p>'+
    '<ol class="note-tree lede"><li><b>Executed scope:</b> '+text(data.counts?.graphs)+
    ' graph/metric instances · '+text(data.counts?.attempted_runs)+' attempted initialization vectors · '+
    text(data.counts?.terminal_optimizations)+' rung-level terminal optimizations. Instance당 M='+
    text(protocol.M)+', independent batches='+text(protocol.independent_batches)+
    (batchSize===undefined?'':', batch size='+text(batchSize))+'.</li>'+
    '<li><b>Fixed numerical gate:</b> '+fixedGate+'. '+text(protocol.policy)+
    '. Exact-target calibration에만 '+controlGate+' 추가.</li>'+
    '<li><b>Interpretation:</b> acceptance와 conditional NEI의 joint report. '+
    'Low acceptance 또는 미생성 null의 사후 제외에 의한 unconditional ensemble claim 금지.</li>'+
    '<li><b>Provenance:</b> protocol SHA-256 <code>'+text(data.config_sha256)+'</code>. '+
    'Artifact audit: <b>'+auditText+'</b>. '+
    '<a href="data/corrected-study.json">Machine-readable summary</a> · '+
    '<a href="notes/09-input-audit.md">Input audit</a>.</li></ol>'+
    '<h3>3A.1 Corrected terminal-law measurements</h3>'+
    '<p class="fine">NEI interval: whole-run percentile bootstrap '+text(bootstrap)+' replicates. '+
    'A_num은 numerical admissibility 조건부 law. Exact-target instance의 calibration primary는 '+
    'target-fit gate까지 통과한 A_ctrl; A_num-only NEI와 교체 불가. '+
    'd_eff와 recurrence는 primary-rung A_num auxiliary summaries.</p>'+
    '<div class="tablewrap"><table><thead><tr><th>Graph / metric instance</th><th>A_num</th>'+
    '<th>NEI | A_num [interval]</th><th>A_ctrl / NEI | A_ctrl [interval]</th>'+
    '<th>d_eff | A_num</th><th>Recurrent / discovery classes | A_num</th>'+
    '</tr></thead><tbody>'+rows+'</tbody></table></div>'+
    '<p class="fine">Class resolution: '+epsilon+'. Independent validation에서 재관측된 discovery class 수. '+
    'Finite M에서 미관측 class의 부재를 뜻하지 않음.</p>'+
    '<h3>3A.2 Graph-null comparisons</h3><ol class="note-tree">'+anchorSections+'</ol>'+
    '<p class="fine">Publication status는 각 contrast row의 <code>publication_status</code>에 따름. '+
    'Degree-null finite-time mixing: '+mixing+'. Connected G(n,m) incomplete anchor: '+gnmIncomplete+
    '. Recorded null-generation failures: '+text(failures)+'.</p>'+
    '<h3>3A.3 One-factor tolerance and sampling checks</h3><ol class="note-tree">'+tolerance+'</ol>'+
    '<h3>3A.4 Evidence limits</h3><ul class="note-tree">'+
    limitItems.map(x=>'<li>'+text(x)+'</li>').join("")+'</ul>';
}
