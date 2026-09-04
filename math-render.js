/* Render explicit SVG formula hosts and ordinary inline math before the
   data-driven app starts. Local KaTeX assets keep this path valid via file://. */
(function renderStaticDocumentMath() {
  if (window.katex?.render) {
    document.querySelectorAll("[data-tex]").forEach(element => {
      try {
        window.katex.render(element.dataset.tex, element, {
          throwOnError: true,
          displayMode: element.dataset.display === "true"
        });
      } catch {
        /* Keep the human-readable fallback already present in the element. */
      }
    });
  }

  if (typeof window.renderMathInElement !== "function") return;

  window.renderMathInElement(document.body, {
    delimiters: [{ left: "$", right: "$", display: false }],
    throwOnError: false,
    ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"]
  });
})();
