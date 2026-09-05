/* Static formula regression; not a browser layout or scientific-result certificate. */
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const katex = require(path.join(root, 'vendor/katex/katex.min.js'));
const errors = [];
let count = 0;
function formula(math, source) {
  count++;
  try { katex.renderToString(math, {throwOnError: true, strict: 'ignore'}); }
  catch (error) { errors.push({source, math, error: error.message}); }
}
function inline(text, source) {
  for (const match of text.matchAll(/\$([^$]+)\$/g)) formula(match[1], source);
}
function visit(value, source, key) {
  if(key === 'tex') return; // Exact LaTeX excerpts use source-specific macros; tested separately.
  if (typeof value === 'string') {
    if (key === 'formula' || /\.kernel\.eq\.\d+$/.test(source)) formula(value, source);
    else inline(value, source);
  } else if (value && typeof value === 'object') {
    for (const [k, child] of Object.entries(value)) visit(child, source + '.' + k, k);
  }
}
for (const file of fs.readdirSync(path.join(root, 'data')).filter(x => x.endsWith('.json'))) {
  visit(JSON.parse(fs.readFileSync(path.join(root, 'data', file), 'utf8')), file, '');
}
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const decode = s => s.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').replace(/&quot;/g, '"');
inline(decode(html), 'index.html');
for (const match of html.matchAll(/data-tex="([^"]*)"/g)) formula(decode(match[1]), 'index.html:data-tex');
if (errors.length) {
  console.error(JSON.stringify(errors, null, 2));
  process.exitCode = 1;
} else console.log('OK: ' + count + ' static/data formulas accepted by bundled KaTeX');
