import test from "node:test";
import assert from "node:assert/strict";
import { assessFocusOutline } from "./focus-outline-metrics.mjs";

const white = { color: "rgb(255,255,255)", image: "none", opacity: "1",
  blend: "normal", filter: "none", backdropFilter: "none" };
const transparent = { ...white, color: "rgba(0,0,0,0)" };
const sample = (overrides = {}) => ({
  label: "Link", selector: "#link", present: true, matches: true,
  focusVisible: true, inViewport: true, outlineStyle: "solid",
  outlineWidthPx: 2, outlineOffsetPx: 2, outlineColor: "rgb(30,50,90)",
  backgroundChain: [transparent, white], chainTruncated: false,
  ...overrides,
});
test("opaque outline and first opaque ancestor have 3:1+ sampled contrast", () => {
  const got = assessFocusOutline(sample());
  assert.equal(got.outcome, "sampled-3-to-1-or-better");
  assert.ok(got.ratio > 3);
  assert.equal(got.backgroundColor, "rgb(255, 255, 255)");
});
test("low contrast is a finding rather than false success", () => {
  const got = assessFocusOutline(sample({ outlineColor: "rgb(190,190,190)" }));
  assert.equal(got.outcome, "sampled-below-3-to-1");
  assert.ok(got.ratio < 3);
});
test("display rounding cannot turn a failing 2.999 ratio into a pass", () => {
  const got = assessFocusOutline(sample({ outlineColor: "rgb(148.9,148.9,148.9)" }));
  assert.equal(got.outcome, "sampled-below-3-to-1");
  assert.equal(got.ratio, 3);
});
test("missing, wrong or non-visible focus does not become a pass", () => {
  for (const bad of [{ matches: false }, { present: false },
                     { focusVisible: false }, { inViewport: false }]) {
    assert.equal(assessFocusOutline(sample(bad)).outcome, "not-measurable");
  }
});
test("unsupported outline style, offset, width or alpha remains unknown", () => {
  for (const bad of [{ outlineStyle: "dotted" }, { outlineWidthPx: 1 },
                     { outlineOffsetPx: -1 }, { outlineOffsetPx: 0 },
                     { outlineColor: "rgba(0,0,0,0.5)" },
                     { outlineColor: "currentColor" }]) {
    assert.equal(assessFocusOutline(sample(bad)).outcome, "not-measurable");
  }
});
test("unsupported ancestor compositing or missing backdrop is unknown", () => {
  for (const layer of [
    { ...white, image: "linear-gradient(red,blue)" },
    { ...white, color: "rgba(255,255,255,0.5)" },
    { ...white, opacity: "0.7" }, { ...white, blend: "multiply" },
    { ...white, filter: "blur(1px)" },
    { ...white, backdropFilter: "blur(1px)" },
  ]) {
    assert.equal(assessFocusOutline(sample({ backgroundChain: [layer] })).outcome,
      "not-measurable");
  }
  assert.equal(assessFocusOutline(sample({ backgroundChain: [transparent] })).outcome,
    "not-measurable");
  assert.equal(assessFocusOutline(sample({ backgroundChain: [] })).outcome,
    "not-measurable");
  assert.equal(assessFocusOutline(sample({ chainTruncated: true })).outcome,
    "not-measurable");
});
test("opaque child does not hide ancestor opacity, but hides backdrop images", () => {
  for (const bad of [{ opacity: "0.6" }, { blend: "screen" }]) {
    const got = assessFocusOutline(sample({ backgroundChain: [white, { ...white, ...bad }] }));
    assert.equal(got.outcome, "not-measurable");
  }
  const got = assessFocusOutline(sample({
    backgroundChain: [white, { ...white, image: "linear-gradient(red,blue)" }],
  }));
  assert.equal(got.outcome, "sampled-3-to-1-or-better");
});
