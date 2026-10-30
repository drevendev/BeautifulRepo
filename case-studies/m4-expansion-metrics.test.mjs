import test from "node:test";
import assert from "node:assert/strict";
import { assessM4Expansion } from "./m4-expansion-metrics.mjs";

const expected = { sampleCount: 13, lastTick: 59, lastCapital: 78.03677092437883 };
const good = () => ({
  httpStatus: 200,
  summaryBefore: { matches: true, focusVisible: true, outlined: true },
  openBefore: false, openAfterEnter: true,
  summaryAfterEnter: { matches: true, focusVisible: true }, openAfterSpace: false,
  charts: [
    "Realized output", "Employment", "Essential-need coverage",
    "Food inventory", "Installed capital",
  ].map(title => ({
    role: "img",
    name: title + ", units, sampled from tick 0 through tick 59. Exact values are in the table below.",
  })),
  tableCaption: "Readable rounded values are paired with the exact artifact value.",
  headers: ["Tick", "Output", "Employment", "Gross wages", "Essential coverage", "Food stock", "Installed capital (units)"],
  rowCount: 13, rowHeaderCount: 13, lastRowTick: "59",
  lastCapitalCell: "78.04 exact 78.03677092437883",
  documentOverflowCssPx: 0,
});

test("accepts the bounded keyboard and table evidence", () => {
  assert.deepEqual(assessM4Expansion(good(), expected), { passed: true, problems: [] });
});
test("rejects no observation or invalid fixture", () => {
  assert.equal(assessM4Expansion(null, expected).passed, false);
  assert.equal(assessM4Expansion(good(), { ...expected, sampleCount: 0 }).passed, false);
});
test("rejects an unopened or unclosable native disclosure", () => {
  for (const [key, value] of [["openAfterEnter", false], ["openAfterSpace", true]]) {
    const run = good(); run[key] = value;
    assert.equal(assessM4Expansion(run, expected).passed, false);
  }
});
test("rejects missing focus-visible on keyboard-opened summary", () => {
  const run = good(); run.summaryAfterEnter.focusVisible = false;
  assert.match(assessM4Expansion(run, expected).problems.join(" "), /focus-lost/);
});
test("rejects incomplete or unlabelled chart alternatives", () => {
  const run = good(); run.charts[1].name = "";
  assert.match(assessM4Expansion(run, expected).problems.join(" "), /chart-missing/);
  run.charts.pop();
  assert.match(assessM4Expansion(run, expected).problems.join(" "), /five-chart/);
});
test("rejects a table without exact-values caption or final column header", () => {
  const run = good(); run.tableCaption = "";
  run.headers.pop();
  assert.match(assessM4Expansion(run, expected).problems.join(" "), /caption/);
  assert.match(assessM4Expansion(run, expected).problems.join(" "), /column-headers/);
});
test("rejects fewer semantic row headers than saved samples", () => {
  const run = good(); run.rowHeaderCount = 12;
  assert.match(assessM4Expansion(run, expected).problems.join(" "), /row-or-header/);
});
test("rejects wrong last tick or fabricated rounded/exact capital", () => {
  const run = good(); run.lastRowTick = "55"; run.lastCapitalCell = "78.04";
  const issues = assessM4Expansion(run, expected).problems.join(" ");
  assert.match(issues, /last-tick/);
  assert.match(issues, /last-capital/);
});
test("rejects document horizontal overflow instead of mistaking table scroll for success", () => {
  const run = good(); run.documentOverflowCssPx = 12;
  assert.match(assessM4Expansion(run, expected).problems.join(" "), /document-overflow/);
});

test("rejects five identical generic chart labels with the shared table suffix", () => {
  const run = good();
  run.charts.forEach(chart => {
    chart.name = "Exact values are in the table below.";
  });
  assert.match(assessM4Expansion(run, expected).problems.join(" "), /chart-missing/);
});
test("rejects duplicated chart-specific names even when the labels look descriptive", () => {
  const run = good();
  run.charts[3].name = run.charts[0].name;
  assert.match(assessM4Expansion(run, expected).problems.join(" "), /chart-missing/);
});
test("rejects any blank intermediate column header", () => {
  for (const index of [1, 2, 3, 4, 5]) {
    const run = good();
    run.headers[index] = "  ";
    assert.match(assessM4Expansion(run, expected).problems.join(" "), /column-headers/);
  }
});
