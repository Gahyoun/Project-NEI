/* Render the static document before the data-driven ES module starts.
   This keeps equations visible when index.html is opened through file://,
   where browsers may block module imports and JSON fetches. */
(function renderStaticDocumentMath() {
  if (typeof window.renderMathInElement !== "function") return;

  window.renderMathInElement(document.body, {
    delimiters: [{ left: "$", right: "$", display: false }],
    throwOnError: false,
    ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"]
  });
})();
