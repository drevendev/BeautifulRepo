/** Bounded geometry observation, not visual or WCAG certification. */
export function assessBottomScroll(sample) {
  const keys = ["scrollY", "maxScrollY", "viewportHeight", "viewportWidth",
    "documentWidth", "footerTop", "footerBottom", "footerTextLength"];
  if (keys.some(k => !Number.isFinite(sample?.[k])) ||
      sample.viewportHeight <= 0 || sample.viewportWidth <= 0 ||
      sample.maxScrollY < 0 || sample.scrollY < 0 ||
      sample.documentWidth < 0 || sample.footerTextLength < 0) {
    return { passed: false, reachedBottom: false, footerOnScreen: false,
      reason: "missing or invalid browser geometry" };
  }
  const reachedBottom = sample.maxScrollY > 0 &&
    Math.abs(sample.maxScrollY - sample.scrollY) <= 2;
  const footerOnScreen = Boolean(sample.footerPresent && sample.footerVisible &&
    sample.footerTextLength >= 15 && sample.footerBottom > 0 &&
    sample.footerTop < sample.viewportHeight);
  const horizontalOverflowCssPx = Math.max(0, sample.documentWidth - sample.viewportWidth);
  return {
    passed: reachedBottom && footerOnScreen && horizontalOverflowCssPx <= 1,
    reachedBottom, footerOnScreen, horizontalOverflowCssPx,
  };
}
