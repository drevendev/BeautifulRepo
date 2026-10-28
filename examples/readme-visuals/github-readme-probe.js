(() => {
  "use strict";
  // Run only after opening a reviewed, full-SHA GitHub-rendered Markdown page.
  // No network requests, clipboard access, DOM changes, or file writes.
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
    prefersDark: matchMedia("(prefers-color-scheme: dark)").matches,
    prefersReducedMotion: matchMedia("(prefers-reduced-motion: reduce)").matches,
    images: images.length,
    unloadedImages: images.filter((img) => !img.complete || img.naturalWidth === 0).length,
    pictureSelections: pictures.map((img) => ({
      alt: img.getAttribute("alt"),
      selectedImagePath: localPath(img.currentSrc),
      rendered: img.complete && img.naturalWidth > 0,
    })),
    caution: "Check any overflow manually. This cannot test keyboard order, screen-reader speech, zoom setting, or WCAG conformance.",
  };
})()
