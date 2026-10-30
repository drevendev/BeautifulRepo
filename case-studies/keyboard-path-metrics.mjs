/**
 * Conservative, read-only assessment of an observed keyboard route.
 * The browser probe supplies real focus, computed styles and native input changes.
 * These checks do not model a screen reader or establish WCAG conformance.
 */
export const COLLAPSED_TABS = Object.freeze([
  { label: "M4 entrance", selector: 'a[href="#chapter-m4"]' },
  { label: "M3 entrance", selector: 'a[href="#chapter-m3"]' },
  { label: "Milestone selector", selector: "#showcase-milestone" },
  { label: "Saved tick slider", selector: "#spotlight-tick" },
  { label: "M4 summary", selector: "#chapter-m4 > summary" },
  { label: "M3 summary", selector: "#chapter-m3 > summary" },
  { label: "M2 summary", selector: "#chapter-m2 > summary" },
  { label: "M1 summary", selector: "#chapter-m1 > summary" },
  { label: "M0 summary", selector: "#chapter-m0 > summary" },
  { label: "Legacy summary", selector: "#chapter-legacy > summary" },
].map(Object.freeze));

function focusIssues(sample, selector) {
  if (!sample || sample.selector !== selector || sample.matches !== true) return ["wrong-focus"];
  const failures = [];
  if (sample.focusVisible !== true) failures.push("no-focus-visible");
  if (sample.outlined !== true) failures.push("no-outline");
  if (sample.inViewport !== true) failures.push("outside-viewport");
  if (sample.hasNameCandidate !== true) failures.push("no-dom-label-candidate");
  return failures;
}

/** Validate the known collapsed-page sequence exactly; no silent omissions. */
export function assessCollapsedTabs(samples) {
  if (!Array.isArray(samples)) return { passed: false, problems: ["not-an-array"] };
  const problems = [];
  if (samples.length !== COLLAPSED_TABS.length) {
    problems.push("tab-count:" + samples.length + "/" + COLLAPSED_TABS.length);
  }
  for (const [index, expected] of COLLAPSED_TABS.entries()) {
    for (const issue of focusIssues(samples[index], expected.selector)) {
      problems.push(expected.label + ":" + issue);
    }
  }
  return { passed: problems.length === 0, problems };
}

/**
 * Require native Enter on the M3 summary, a Tab into its live range input,
 * and real ArrowLeft/Right changing/restoring the rendered sample tick.
 */
export function assessM3Keyboard(observation) {
  if (!observation || typeof observation !== "object") {
    return { passed: false, problems: ["missing-observation"] };
  }
  const problems = [];
  for (const issue of focusIssues(observation.summaryFocus, "#chapter-m3 > summary")) {
    problems.push("summary:" + issue);
  }
  if (observation.openBefore !== false || observation.openAfterEnter !== true) {
    problems.push("enter-did-not-open-closed-summary");
  }
  for (const issue of focusIssues(observation.tickFocus, "#m3-tick")) {
    problems.push("range:" + issue);
  }
  if (observation.tickFocus?.descriptionTarget !== "m3-tick-readout") {
    problems.push("range-description-not-linked");
  }
  const { before, left, restored } = observation;
  if (![before, left, restored].every(x =>
    x && Number.isInteger(x.value) && Number.isInteger(x.max) &&
    typeof x.readout === "string" && x.readout.length > 0
  )) {
    problems.push("missing-tick-observation");
  } else {
    if (before.max < 2 || before.value !== before.max) problems.push("unexpected-initial-tick");
    if (left.value !== before.value - 1 || left.readout === before.readout) {
      problems.push("left-arrow-no-rendered-change");
    }
    if (restored.value !== before.value || restored.readout !== before.readout) {
      problems.push("right-arrow-did-not-restore");
    }
  }
  return { passed: problems.length === 0, problems };
}
