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
  const pictures = [...article.querySelectorAll("picture img")];
  const images = [...article.querySelectorAll("img")];
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
  const descendants = article.querySelectorAll("*");
  const edge = article.getBoundingClientRect();
  const scannedNodes = Math.min(descendants.length, 2000);
  const samples = [];
  let candidateCount = 0;
  if (Number.isFinite(edge.left) && Number.isFinite(edge.right)) {
    for (let i = 0; i < scannedNodes; i++) {
      const node = descendants[i];
      const rect = node.getBoundingClientRect();
      if (!Number.isFinite(rect.left) || !Number.isFinite(rect.right) ||
          rect.width <= 0 || rect.height <= 0) continue;
      const leftPx = Math.max(0, Math.ceil(edge.left - rect.left));
      const rightPx = Math.max(0, Math.ceil(rect.right - edge.right));
      if (!leftPx && !rightPx) continue;
      candidateCount++;
      if (samples.length < 8) samples.push({
        elementIndex: i, tag: node.tagName.toLowerCase(),
        leftOverflowPx: leftPx, rightOverflowPx: rightPx,
      });
    }
  }

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
      truncated: descendants.length > scannedNodes,
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
    images: images.length,
    unloadedImages: images.filter((img) => !img.complete || img.naturalWidth === 0).length,
    pictureSelections: pictures.map((img) => ({
      alt: img.getAttribute("alt"),
      selectedImagePath: localPath(img.currentSrc),
      rendered: img.complete && img.naturalWidth > 0,
    })),
    caution: "Overflow samples are geometry leads, not failures; code/tables can scroll locally and some CSS overflow may escape sampling. Browser prefersDark is not necessarily GitHub's selected theme. Check actual appearance, keyboard order, screen-reader speech, zoom, and WCAG conformance manually.",
  };
})()
