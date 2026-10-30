/**
 * Conservative structural assessment of one keyboard-opened M4 disclosure.
 * Inputs are live browser observations, not computed accessibility-tree names.
 * This does not measure screen readers, chart exploration or table panning.
 */
export function assessM4Expansion(observation, expected) {
  if (!observation || typeof observation !== "object") {
    return { passed: false, problems: ["missing-observation"] };
  }
  if (!expected || !Number.isInteger(expected.sampleCount) || expected.sampleCount < 1 ||
      !Number.isInteger(expected.lastTick) || !Number.isFinite(expected.lastCapital)) {
    return { passed: false, problems: ["invalid-expected-fixture"] };
  }
  const problems = [];
  if (observation.httpStatus !== 200) problems.push("html-not-200");
  if (!observation.summaryBefore?.matches || !observation.summaryBefore.focusVisible ||
      !observation.summaryBefore.outlined) problems.push("summary-not-keyboard-focused");
  if (observation.openBefore !== false || observation.openAfterEnter !== true) {
    problems.push("enter-did-not-expand");
  }
  if (!observation.summaryAfterEnter?.matches || !observation.summaryAfterEnter.focusVisible) {
    problems.push("focus-lost-on-expand");
  }
  if (observation.openAfterSpace !== false) problems.push("space-did-not-collapse");
  const charts = observation.charts;
  if (!Array.isArray(charts) || charts.length !== 5) {
    problems.push("expected-five-chart-alternatives");
  } else if (charts.some(chart => chart.role !== "img" ||
    typeof chart.name !== "string" || !chart.name.includes("Exact values are in the table below."))) {
    problems.push("chart-missing-text-alternative");
  }
  if (typeof observation.tableCaption !== "string" ||
      !observation.tableCaption.includes("exact artifact value")) {
    problems.push("missing-exact-values-caption");
  }
  if (!Array.isArray(observation.headers) || observation.headers.length !== 7 ||
      observation.headers[0] !== "Tick" ||
      !observation.headers[6]?.startsWith("Installed capital")) {
    problems.push("invalid-table-column-headers");
  }
  if (observation.rowCount !== expected.sampleCount ||
      observation.rowHeaderCount !== expected.sampleCount) {
    problems.push("sampled-row-or-header-count-mismatch");
  }
  if (observation.lastRowTick !== String(expected.lastTick)) problems.push("last-tick-mismatch");
  const lastCapital = observation.lastCapitalCell;
  if (typeof lastCapital !== "string" ||
      !lastCapital.includes(expected.lastCapital.toFixed(2)) ||
      !lastCapital.includes("exact " + String(expected.lastCapital))) {
    problems.push("last-capital-not-readable-and-exact");
  }
  if (!Number.isFinite(observation.documentOverflowCssPx) ||
      observation.documentOverflowCssPx > 0 || observation.documentOverflowCssPx < 0) {
    problems.push("expanded-document-overflow-or-unmeasured");
  }
  return { passed: problems.length === 0, problems };
}
