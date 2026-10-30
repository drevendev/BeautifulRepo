/**
 * Assess a real keyboard-only attempt to reach and pan a wide M4 table.
 * Negative outcomes are findings, not test-harness failures: the observer
 * must not turn a real accessibility barrier into a green conformance claim.
 * This is one Chromium route, not an accessibility-tree or screen-reader test.
 */
export function assessM4TableKeyboard(run) {
  if (!run || typeof run !== "object") {
    return { instrumentationPassed: false, demonstrated: false, problems: ["missing-observation"], findings: [] };
  }
  const problems = [];
  const findings = [];
  if (run.httpStatus !== 200) problems.push("html-not-200");
  if (run.summaryFocused !== true || run.openedWithEnter !== true) {
    problems.push("chapter-not-keyboard-opened");
  }
  const region = run.region;
  const finite = value => typeof value === "number" && Number.isFinite(value);
  if (!region || !finite(region.scrollWidth) || !finite(region.clientWidth) ||
      region.clientWidth <= 0 || region.scrollWidth - region.clientWidth < 20 ||
      !["auto", "scroll"].includes(region.overflowX)) {
    problems.push("wide-scroll-region-not-measured");
  }
  if (!finite(run.documentOverflowCssPx) || run.documentOverflowCssPx < 0 ||
      run.documentOverflowCssPx > 0) {
    problems.push("document-overflow-or-unmeasured");
  }
  if (!Array.isArray(run.tabTrace) || run.tabTrace.length < 1 ||
      run.tabTrace.length > 16 ||
      run.tabTrace.some(item => typeof item?.matches !== "boolean")) {
    problems.push("invalid-native-tab-trace");
  }
  if (typeof run.focusReached !== "boolean" ||
      (Array.isArray(run.tabTrace) &&
        run.tabTrace.some(item => item?.matches === true) !== run.focusReached)) {
    problems.push("focus-trace-inconsistent");
  }
  const reached = run.focusReached === true;
  let rightPanned = false;
  let leftReversed = false;
  if (reached) {
    if (![run.scrollBefore, run.scrollAfterRight, run.scrollAfterLeft].every(finite) ||
        run.scrollBefore < 0 || run.scrollAfterRight < 0 || run.scrollAfterLeft < 0 ||
        (region && finite(region.scrollWidth) && finite(region.clientWidth) &&
          Math.max(run.scrollBefore, run.scrollAfterRight, run.scrollAfterLeft) >
            region.scrollWidth - region.clientWidth + 1)) {
      problems.push("invalid-arrow-scroll-measurements");
    } else {
      rightPanned = run.scrollAfterRight > run.scrollBefore + 0.5;
      leftReversed = run.scrollAfterLeft < run.scrollAfterRight - 0.5;
    }
    if (run.leftRegionWithTab !== true) findings.push("tab-exit-not-demonstrated");
    if (!run.focusVisible || !run.outlined) findings.push("focus-indicator-not-demonstrated");
    if (!rightPanned || !leftReversed) findings.push("bidirectional-arrow-pan-not-demonstrated");
  } else {
    findings.push("scroll-region-not-reached-by-native-tab");
    if (run.scrollAfterRight !== null || run.scrollAfterLeft !== null) {
      problems.push("arrow-values-without-region-focus");
    }
  }
  if (region && !region.hasExplicitName) {
    findings.push("explicit-scroll-region-name-not-observed");
  }
  return {
    instrumentationPassed: problems.length === 0,
    demonstrated: problems.length === 0 && reached && rightPanned &&
      leftReversed && run.leftRegionWithTab === true,
    problems,
    findings,
  };
}
