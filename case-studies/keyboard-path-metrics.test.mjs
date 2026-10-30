import test from "node:test";
import assert from "node:assert/strict";
import {
  COLLAPSED_TABS,
  assessCollapsedTabs,
  assessM3Keyboard,
} from "./keyboard-path-metrics.mjs";

const good = selector => ({
  selector, matches: true, focusVisible: true, outlined: true,
  inViewport: true, hasNameCandidate: true,
});
const sweep = () => COLLAPSED_TABS.map(row => good(row.selector));
const m3 = () => ({
  summaryFocus: good("#chapter-m3 > summary"),
  openBefore: false,
  openAfterEnter: true,
  tickFocus: { ...good("#m3-tick"), descriptionTarget: "m3-tick-readout" },
  before: { value: 60, max: 60, readout: "tick 59" },
  left: { value: 59, max: 60, readout: "tick 58" },
  restored: { value: 60, max: 60, readout: "tick 59" },
});

test("accepts ten observed collapsed-page Tab stops in exact order", () => {
  assert.equal(assessCollapsedTabs(sweep()).passed, true);
});
test("rejects missing last summary", () => {
  assert.equal(assessCollapsedTabs(sweep().slice(0, -1)).passed, false);
});
test("rejects reordered middle summaries", () => {
  const rows = sweep();
  [rows[6], rows[7]] = [rows[7], rows[6]];
  assert.equal(assessCollapsedTabs(rows).passed, false);
});
test("rejects missing visible outline", () => {
  const rows = sweep();
  rows[7].outlined = false;
  assert.match(assessCollapsedTabs(rows).problems.join(" "), /no-outline/);
});
test("rejects focus not visible in the physical CSS viewport", () => {
  const rows = sweep();
  rows[8].inViewport = false;
  assert.match(assessCollapsedTabs(rows).problems.join(" "), /outside-viewport/);
});
test("rejects elements without a DOM label candidate", () => {
  const rows = sweep();
  rows[3].hasNameCandidate = false;
  assert.match(assessCollapsedTabs(rows).problems.join(" "), /no-dom-label-candidate/);
});
test("accepts keyboard-opened M3 and restored native tick", () => {
  assert.equal(assessM3Keyboard(m3()).passed, true);
});
test("rejects a summary opened before Enter", () => {
  const run = m3(); run.openBefore = true;
  assert.match(assessM3Keyboard(run).problems.join(" "), /enter-did-not-open/);
});
test("rejects a missing range description relationship", () => {
  const run = m3(); run.tickFocus.descriptionTarget = null;
  assert.match(assessM3Keyboard(run).problems.join(" "), /description-not-linked/);
});
test("rejects a slider moved in the DOM without changed readout", () => {
  const run = m3(); run.left.readout = run.before.readout;
  assert.match(assessM3Keyboard(run).problems.join(" "), /no-rendered-change/);
});
test("rejects a right-arrow action that did not restore the original sample", () => {
  const run = m3(); run.restored.value = 59;
  assert.match(assessM3Keyboard(run).problems.join(" "), /did-not-restore/);
});
