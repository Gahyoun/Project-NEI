/* Inert rendering of exact source excerpts. No TeX or HTML source is executed. */
(function(root) {
  "use strict";
  const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const common={"\\R":"\\mathbb{R}","\\one":"\\bm{1}","\\rank":"\\operatorname{rank}",
    "\\diag":"\\operatorname{diag}","\\NEI":"\\mathcal{I}","\\Pplus":"\\mathcal{P}_{+}"};
  const macros={
    main:{...common},
    si:{...common,"\\D":"\\bm{D}","\\B":"\\bm{B}","\\Hc":"\\bm{H}","\\X":"\\bm{X}",
      "\\E":"\\bm{E}","\\Tr":"\\operatorname{Tr}","\\Span":"\\operatorname{span}",
      "\\cH":"c^{\\mathrm H}","\\eps":"\\varepsilon","\\Ord":"\\mathcal O","\\Bmat":"\\bm{B}"},
    note:{...common,"\\Euc":"\\mathrm{E}","\\SE":"\\mathrm{SE}","\\tr":"\\operatorname{tr}",
      "\\vecop":"\\operatorname{vec}","\\vecrow":"\\operatorname{vec}_{r}","\\med":"\\operatorname{median}",
      "\\Gram":"\\mathbf{G}_{\\mathrm{cMDS}}","\\Var":"\\operatorname{Var}","\\stress":"\\mathcal{F}",
      "\\disp":"\\mathcal{S}","\\Dmat":"\\mathbf{D}","\\Hess":"\\mathbf{H}","\\Id":"\\mathbf{I}",
      "\\grad":"\\nabla","\\zerovec":"\\bm{0}"}
  };
  function group(s,start,left="{",right="}") {
    let i=start;while(i<s.length&&/\s/.test(s[i])) i++;
    if(s[i]!==left) return null;
    const begin=++i;let depth=1;
    for(;i<s.length;i++) {
      if(s[i]==="\\"){i++;continue;}
      if(s[i]===left) depth++;
      if(s[i]===right&&--depth===0) return {text:s.slice(begin,i),end:i+1};
    }
    return null;
  }
  function stripComments(s) {
    return s.split("\n").map(line=>{
      for(let i=0;i<line.length;i++) {
        if(line[i]==="\\"){i++;continue;}
        if(line[i]==="%") return line.slice(0,i);
      } return line;
    }).join("\n");
  }
  function endAt(s,marker,start) {
    for(let i=start;i<s.length;i++) {
      if(s.startsWith(marker,i)) return i;
      if(s[i]==="\\") i++;
    } return -1;
  }
  function render(input,source,katex=root.katex) {
    const errors=[],unknown=new Set();
    function math(content,display,env) {
      let m=content.replace(/\\label\s*\{[^}]*\}/g,"").trim();
      if(env&&/^(align|gather|multline|eqnarray)/.test(env)) {
        const wrapper=env.startsWith("gather")?"gathered":"aligned";
        m="\\begin{"+wrapper+"}"+m+"\\end{"+wrapper+"}";
      }
      try {return katex.renderToString(m,{displayMode:display,throwOnError:true,
        strict:"ignore",trust:false,macros:{...macros[source]}});}
      catch(e){errors.push({math:m,error:e.message});return '<code class="source-math-fallback">'+esc(content)+'</code>';}
    }
    function prose(s) {
      let html="",i=0;
      while(i<s.length) {
        if(s[i]==="$") {
          const mark=s[i+1]==="$"?"$$":"$",end=endAt(s,mark,i+mark.length);
          if(end>=0){html+=math(s.slice(i+mark.length,end),mark==="$$");i=end+mark.length;continue;}
        }
        if(s.startsWith("\\(",i)||s.startsWith("\\[",i)) {
          const display=s[i+1]==="[",close=display?"\\]":"\\)",end=endAt(s,close,i+2);
          if(end>=0){html+=math(s.slice(i+2,end),display);i=end+2;continue;}
        }
        if(s[i]==="\\") {
          const match=s.slice(i).match(/^\\([A-Za-z]+\*?|[^A-Za-z])/);
          if(!match){html+="\\";i++;continue;}
          const cmd=match[1];i+=match[0].length;const g=group(s,i);
          if((cmd==="begin"||cmd==="end")&&g) {
            const env=g.text;i=g.end;
            if(cmd==="begin"&&/^(equation|align|gather|multline|eqnarray)\*?$/.test(env)) {
              const marker="\\end{"+env+"}",end=s.indexOf(marker,i);
              if(end>=0){html+=math(s.slice(i,end),true,env);i=end+marker.length;continue;}
            }
            html+="<br>";const opt=group(s,i,"[","]");
            if(cmd==="begin"&&opt){html+="<strong>"+prose(opt.text)+"</strong> ";i=opt.end;}
            continue;
          }
          if(cmd==="label"&&g){i=g.end;continue;}
          if(cmd==="renewcommand"&&g){const a=group(s,g.end);if(a){i=a.end;continue;}}
          if(/^(eqref|ref|autoref|cref|Cref|cite|citep|citet|citealt|citealp)\*?$/.test(cmd)) {
            let cursor=i,opt;while((opt=group(s,cursor,"[","]"))) cursor=opt.end;
            const a=group(s,cursor);
            if(a){const cite=cmd.startsWith("cite"),eq=cmd==="eqref";
              html+='<span class="source-crossref" title="'+(cite?"원문 citation key":"원문 cross-reference key")+'">'+
                esc((cite?"[":eq?"(":"")+a.text+(cite?"]":eq?")":""))+"</span>";
              i=a.end;continue;}
          }
          const tags={textbf:"strong",emph:"em",textit:"em",textsl:"em",texttt:"code",
            underline:"u",textrm:"span",textnormal:"span",mbox:"span",text:"span",footnote:"span",caption:"span"};
          if(tags[cmd]&&g){const t=tags[cmd];html+="<"+t+">"+prose(g.text)+"</"+t+">";i=g.end;continue;}
          if(/^(section|subsection|subsubsection|paragraph|subparagraph)\*?$/.test(cmd)&&g){
            html+="<strong>"+prose(g.text)+"</strong> ";i=g.end;continue;}
          if(cmd==="href"&&g){const a=group(s,g.end);if(a){html+=prose(a.text);i=a.end;continue;}}
          if(cmd==="url"&&g){html+=esc(g.text);i=g.end;continue;}
          if(cmd==="textcolor"&&g){const a=group(s,g.end);if(a){html+=prose(a.text);i=a.end;continue;}}
          if(cmd==="item"){const a=group(s,i,"[","]");
            html+='<br><span class="quote-item">'+(a?prose(a.text):"•")+"</span> ";if(a)i=a.end;continue;}
          if(["noindent","small","footnotesize","scriptsize","normalsize","centering","raggedright","sloppy"].includes(cmd))continue;
          if(["par","newline","\\","smallskip","medskip","bigskip"].includes(cmd)){html+="<br>";continue;}
          if([",",";",":","!"," ","quad","qquad"].includes(cmd)){html+=" ";continue;}
          if(["%","&","#","_","{","}","$"].includes(cmd)){html+=esc(cmd);continue;}
          if(cmd==="LaTeX"){html+="LaTeX";continue;}
          if(cmd==="ERname"){html+="Erdős–Rényi";continue;}
          const accents={"H":"\u030b","'":"\u0301",'"':"\u0308","\x60":"\u0300","^":"\u0302","~":"\u0303","c":"\u0327","v":"\u030c"};
          if(accents[cmd]){const a=g?g.text:s[i];if(a){html+=esc((a+accents[cmd]).normalize("NFC"));i=g?g.end:i+1;continue;}}
          if(["ldots","dots"].includes(cmd)){html+="…";continue;}
          unknown.add(cmd);html+=esc("\\"+cmd);continue;
        }
        if(s.startsWith("\n\n",i)){html+="<br><br>";i+=2;continue;}
        if(s.startsWith("---",i)){html+="—";i+=3;continue;}
        if(s.startsWith("--",i)){html+="–";i+=2;continue;}
        if(s.startsWith("\x60\x60",i)){html+="“";i+=2;continue;}
        if(s.startsWith("''",i)){html+="”";i+=2;continue;}
        if(s[i]==="{"||s[i]==="}"){i++;continue;}
        html+=s[i]==="~"?"&nbsp;":esc(s[i]);i++;
      } return html;
    }
    return {html:prose(stripComments(input)),errors,unknown:[...unknown]};
  }
  const api={render,macros};
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
  else root.NEISourceQuote=api;
})(typeof window!=="undefined"?window:globalThis);
