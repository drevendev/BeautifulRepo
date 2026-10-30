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
  // This case pins a single fixture and the five distinct chart identities.
  // A shared generic suffix is not evidence of five descriptive alternatives.
  const chartTitles = [
    "Realized output", "Employment", "Essential-need coverage",
    "Food inventory", "Installed capital",
  ];
  const charts = observation.charts;
  if (!Array.isArray(charts) || charts.length !== chartTitles.length) {
    problems.push("expected-five-chart-alternatives");
  } else if (charts.some((chart, index) => {
    const name = chart?.name;
    const prefix = chartTitles[index] + ", ";
    return chart?.role !== "img" || typeof name !== "string" ||
      !name.startsWith(prefix) ||
      !/^.+, sampled from tick [0-9]+ through tick [0-9]+\. Exact values are in the table below\.$/
        .test(name.slice(prefix.length));
  })) {
    problems.push("chart-missing-text-alternative");
  }
  if (typeof observation.tableCaption !== "string" ||
      !observation.tableCaption.includes("exact artifact value")) {
    problems.push("missing-exact-values-caption");
  }
  // Require all seven pinned column identities, not just the first and last.
  const headerTitles = [
    ["Tick", false], ["Output", true], ["Employment", true],
    ["Gross wages", true], ["Essential coverage", false],
    ["Food stock", true], ["Installed capital", true],
  ];
  const validHeader = (value, [title, hasUnit]) => {
    if (typeof value !== "string") return false;
    const label = value.trim();
    if (!hasUnit) return label === title;
    const prefix = title + " (";
    return label.startsWith(prefix) && label.endsWith(")") &&
      label.slice(prefix.length, -1).trim().length > 0;
  };
  if (!Array.isArray(observation.headers) ||
      observation.headers.length !== headerTitles.length ||
      observation.headers.some((header, index) => !validHeader(header, headerTitles[index]))) {
    problems.push("invalid-table-column-headers");
  }
  if (observation.rowCount !== expected.sampleCount ||
      observation.rowHeaderCount !== expected.sampleCount) {
    problems.push("sampled-row-or-header-count-mismatch");
  }
  if (observation.lastRowTick !== String(expected.lastTick)) problems.push("last-tick-mismatch");
  // Check both complete values in the rendered cell, not substrings: 178.04
  // must not pass for an expected rounded value of 78.04.
  const lastCapital = observation.lastCapitalCell;
  const parsedCapital = typeof lastCapital === "string"
    ? lastCapital.match(/^(-?\d+\.\d{2}) exact (-?\d+(?:\.\d+)?)$/)
    : null;
  if (!parsedCapital ||
      parsedCapital[1] !== expected.lastCapital.toFixed(2) ||
      parsedCapital[2] !== String(expected.lastCapital)) {
    problems.push("last-capital-not-readable-and-exact");
  }
  if (!Number.isFinite(observation.documentOverflowCssPx) ||
      observation.documentOverflowCssPx > 0 || observation.documentOverflowCssPx < 0) {
    problems.push("expanded-document-overflow-or-unmeasured");
  }
  return { passed: problems.length === 0, problems };
}
