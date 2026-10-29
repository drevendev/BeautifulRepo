(() => {
  "use strict";
  // Run only after opening a reviewed, full-SHA GitHub-rendered Markdown page.
  // No network requests, clipboard access, DOM changes, or file writes.
  const pinned = location.hostname === "github.com" &&
    /^\/[^/]+\/[^/]+\/blob\/[0-9a-f]{40}\/.+/i.test(location.pathname);
  if (!pinned) {
    return { status: "NOT RUN", reason: "Open a GitHub-rendered blob page pinned to a full commit SHA." };
  }
  const article = document.querySelector("article.markdown-body, .markdown-body");
  if (!article) {
    return { status: "NOT RUN", reason: "No rendered Markdown body was found on this page." };
  }

  const root = document.documentElement;
  const cssViewportWidth = root.clientWidth;
  const pageScrollWidth = root.scrollWidth;
  // All counts are within the bounded descendant sample, never the whole page
  // when overflowInspection.truncated is true.
  let images = 0;
  let unloadedImages = 0;
  let pictureMatches = 0;
  const pictureSelections = [];
  const localPath = (source) => {
    if (!source) return null;
    try {
      // Do not print query strings (which could contain private tokens).
      const url = new URL(source, location.href);
      if (url.protocol !== "http:" && url.protocol !== "https:") return `[${url.protocol.slice(0, -1)} image]`;
      return `${url.origin}${url.pathname}`;
    } catch {
      return null;
    }
  };

  // Diagnostic geometry leads only; local scrolling code/tables can be valid.
  // Never report text, IDs, classes, attributes or linked URLs.
  // Walk only the bounded sample, never materialize every descendant.
  // TreeWalker begins after article, preserving zero-based descendant indexes.
  const edge = article.getBoundingClientRect();
  const walker = document.createTreeWalker(article, NodeFilter.SHOW_ELEMENT);
  let scannedNodes = 0;
  const samples = [];
  let candidateCount = 0;
  while (scannedNodes < 2000) {
    const node = walker.nextNode();
    if (!node) break;
    const elementIndex = scannedNodes++;
    if (node.tagName.toLowerCase() === "img") {
      images++;
      const rendered = node.complete && node.naturalWidth > 0;
      if (!rendered) unloadedImages++;
      if (node.closest("picture")) {
        pictureMatches++;
        if (pictureSelections.length < 8) pictureSelections.push({
          alt: node.getAttribute("alt"),
          selectedImagePath: localPath(node.currentSrc),
          rendered,
        });
      }
    }
    const rect = node.getBoundingClientRect();
    if (!Number.isFinite(edge.left) || !Number.isFinite(edge.right) ||
        !Number.isFinite(rect.left) || !Number.isFinite(rect.right) ||
        rect.width <= 0 || rect.height <= 0) continue;
    const leftPx = Math.max(0, Math.ceil(edge.left - rect.left));
    const rightPx = Math.max(0, Math.ceil(rect.right - edge.right));
    if (!leftPx && !rightPx) continue;
    candidateCount++;
    if (samples.length < 8) samples.push({
      elementIndex, tag: node.tagName.toLowerCase(),
      leftOverflowPx: leftPx, rightOverflowPx: rightPx,
    });
  }
  // One extra step distinguishes exactly 2,000 nodes from a longer article.
  const truncated = scannedNodes === 2000 && walker.nextNode() !== null;

  return {
    status: "MEASURED (not an accessibility verdict)",
    observedAtUTC: new Date().toISOString(),
    pagePath: `${location.origin}${location.pathname}`,
    cssViewportWidth,
    innerWidth: window.innerWidth,
    pageScrollWidth,
    pageOverflowPx: Math.max(0, pageScrollWidth - cssViewportWidth),
    markdownClientWidth: article.clientWidth,
    markdownScrollWidth: article.scrollWidth,
    markdownOverflowPx: Math.max(0, article.scrollWidth - article.clientWidth),
    overflowInspection: {
      scannedNodes,
      truncated,
      candidateCount,
      samples,
    },
    // The browser media preference can differ from GitHub's selected site theme.
    prefersDark: matchMedia("(prefers-color-scheme: dark)").matches,
    githubAppearance: {
      colorMode: root.getAttribute("data-color-mode"),
      lightTheme: root.getAttribute("data-light-theme"),
      darkTheme: root.getAttribute("data-dark-theme"),
    },
    prefersReducedMotion: matchMedia("(prefers-reduced-motion: reduce)").matches,
    images,
    unloadedImages,
    imageCountsPartial: truncated,
    pictureSelectionsTruncated: pictureMatches > pictureSelections.length || truncated,
    pictureSelections,
    caution: "Overflow samples are geometry leads, not failures; code/tables can scroll locally and some CSS overflow may escape sampling. When imageCountsPartial is true, image counts are lower bounds and pictureSelections may omit images. Browser prefersDark is not necessarily GitHub's selected theme. Check actual appearance, keyboard order, screen-reader speech, zoom, and WCAG conformance manually.",
  };
})()
