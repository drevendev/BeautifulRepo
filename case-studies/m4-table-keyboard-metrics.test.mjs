import test from "node:test";
import assert from "node:assert/strict";
import { assessM4TableKeyboard } from "./m4-table-keyboard-metrics.mjs";

const good = () => ({
  httpStatus: 200, summaryFocused: true, openedWithEnter: true,
  region: {
    scrollWidth: 760, clientWidth: 137, overflowX: "auto",
    hasExplicitName: true,
  },
  documentOverflowCssPx: 0,
  tabTrace: [{ matches: true, actualTag: "DIV" }],
  focusReached: true, focusVisible: true, outlined: true,
  scrollBefore: 0, scrollAfterRight: 100, scrollAfterLeft: 0,
  leftRegionWithTab: true,
});

test("demonstrates keyboard panning and escape only with real movement", () => {
  assert.deepEqual(assessM4TableKeyboard(good()), {
    instrumentationPassed: true, demonstrated: true, problems: [], findings: [],
  });
});
test("no native Tab route is an honest finding, not a fabricated success", () => {
  const run = good();
  run.focusReached = false;
  run.tabTrace = [{ matches: false }, { matches: false }];
  run.scrollBefore = null; run.scrollAfterRight = null; run.scrollAfterLeft = null;
  run.leftRegionWithTab = null;
  const result = assessM4TableKeyboard(run);
  assert.equal(result.instrumentationPassed, true);
  assert.equal(result.demonstrated, false);
  assert.ok(result.findings.includes("scroll-region-not-reached-by-native-tab"));
});
test("detects unchanged arrows and one-way-only movement", () => {
  for (const [right, left] of [[0, 0], [100, 100]]) {
    const run = good(); run.scrollAfterRight = right; run.scrollAfterLeft = left;
    const result = assessM4TableKeyboard(run);
    assert.equal(result.instrumentationPassed, true);
    assert.equal(result.demonstrated, false);
    assert.ok(result.findings.includes("bidirectional-arrow-pan-not-demonstrated"));
  }
});
test("does not mistake panning for proof that Tab can leave", () => {
  const run = good(); run.leftRegionWithTab = false;
  const result = assessM4TableKeyboard(run);
  assert.equal(result.demonstrated, false);
  assert.ok(result.findings.includes("tab-exit-not-demonstrated"));
});
test("reports missing explicit region name without inferring a screen-reader name", () => {
  const run = good(); run.region.hasExplicitName = false;
  const result = assessM4TableKeyboard(run);
  assert.equal(result.demonstrated, true);
  assert.ok(result.findings.includes("explicit-scroll-region-name-not-observed"));
});
test("rejects invalid horizontal geometry or invented arrow coordinates", () => {
  for (const changes of [
    { region: { scrollWidth: 300, clientWidth: 300, overflowX: "auto", hasExplicitName: true } },
    { region: { scrollWidth: 760, clientWidth: 137, overflowX: "hidden", hasExplicitName: true } },
    { scrollAfterRight: 700 },
    { scrollBefore: NaN },
    { documentOverflowCssPx: 4 },
  ]) {
    const result = assessM4TableKeyboard({ ...good(), ...changes });
    assert.equal(result.instrumentationPassed, false);
    assert.equal(result.demonstrated, false);
  }
});
test("rejects incomplete focus trace and contradictory native focus claims", () => {
  for (const changes of [
    { tabTrace: [] },
    { tabTrace: [{ matches: false }] },
    { tabTrace: Array(17).fill({ matches: false }) },
    { focusReached: false, scrollAfterRight: 100 },
  ]) {
    const result = assessM4TableKeyboard({ ...good(), ...changes });
    assert.equal(result.instrumentationPassed, false);
  }
});
test("rejects absent observation, failed navigation and synthetic opening", () => {
  assert.equal(assessM4TableKeyboard(null).instrumentationPassed, false);
  for (const changes of [
    { httpStatus: 404 }, { summaryFocused: false }, { openedWithEnter: false },
  ]) {
    assert.equal(assessM4TableKeyboard({ ...good(), ...changes }).instrumentationPassed, false);
  }
});
