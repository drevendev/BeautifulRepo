import test from "node:test";
import assert from "node:assert/strict";
import { assessTextContrast, contrastRatio, parseComputedRgb } from "./contrast-metrics.mjs";

const sample = (overrides = {}) => ({
  label: "Sampled annotation",
  selector: ".sample",
  present: true,
  visible: true,
  text: "A real annotation",
  foreground: "rgb(0, 0, 0)",
  fontSizePx: 12,
  fontWeight: 400,
  backgroundChain: [
    { color: "rgba(0, 0, 0, 0)", image: "none", opacity: "1", blend: "normal" },
    { color: "rgb(255, 255, 255)", image: "none", opacity: "1", blend: "normal" },
  ],
  ...overrides,
});

test("opaque RGB parser accepts Chromium values and rejects unsupported formats", () => {
  assert.deepEqual(parseComputedRgb("rgb(255, 0, 20)"), { r: 255, g: 0, b: 20, a: 1 });
  assert.deepEqual(parseComputedRgb("rgba(0, 0, 0, 0)"), { r: 0, g: 0, b: 0, a: 0 });
  assert.equal(parseComputedRgb("var(--ink)"), null);
  assert.equal(parseComputedRgb("rgb(300, 0, 0)"), null);
  assert.equal(parseComputedRgb("rgba(0, 0, 0, 2)"), null);
});

test("reference black/white ratio is 21:1, symmetric", () => {
  const black = parseComputedRgb("rgb(0,0,0)");
  const white = parseComputedRgb("rgb(255,255,255)");
  assert.equal(contrastRatio(black, white), 21);
  assert.equal(contrastRatio(white, black), 21);
});

test("transparent child resolves to first opaque ancestor", () => {
  const got = assessTextContrast(sample());
  assert.equal(got.outcome, "meets-sampled-AA");
  assert.equal(got.ratio, 21);
  assert.equal(got.threshold, 4.5);
  assert.equal(got.background, "rgb(255, 255, 255)");
});

test("insufficient normal-size contrast is evidence, not a failing test harness", () => {
  const got = assessTextContrast(sample({ foreground: "rgb(170, 170, 170)" }));
  assert.equal(got.outcome, "below-sampled-AA");
  assert.ok(got.ratio < 4.5);
});

test("near-threshold decisions never round a failing value into a pass", () => {
  const got = assessTextContrast(sample({ foreground: "rgb(118.7, 118.7, 118.7)" }));
  assert.equal(got.ratio, 4.5); // Display rounds to 2 decimals.
  assert.equal(got.outcome, "below-sampled-AA"); // Actual ratio is < 4.5.
});

test("large bold text uses the 3:1 threshold, regular text does not", () => {
  const foreground = "rgb(130, 130, 130)";
  const normal = assessTextContrast(sample({ foreground, fontSizePx: 18.67, fontWeight: 400 }));
  const bold = assessTextContrast(sample({ foreground, fontSizePx: 18.67, fontWeight: 700 }));
  assert.equal(normal.threshold, 4.5);
  assert.equal(bold.threshold, 3);
  assert.equal(normal.outcome, "below-sampled-AA");
  assert.equal(bold.outcome, "meets-sampled-AA");
});

test("missing or hidden samples never become passes", () => {
  assert.equal(assessTextContrast(sample({ present: false })).outcome, "not-measurable");
  assert.equal(assessTextContrast(sample({ visible: false })).outcome, "not-measurable");
  assert.equal(assessTextContrast(sample({ text: "  " })).outcome, "not-measurable");
});

test("unsupported compositing, alpha and background image remain unknown", () => {
  const unsupported = [
    { color: "rgb(255,255,255)", image: "linear-gradient(red, blue)", opacity: "1", blend: "normal" },
    { color: "rgba(255,255,255,0.5)", image: "none", opacity: "1", blend: "normal" },
    { color: "rgb(255,255,255)", image: "none", opacity: "0.7", blend: "normal" },
    { color: "rgb(255,255,255)", image: "none", opacity: "1", blend: "multiply" },
  ];
  for (const layer of unsupported) {
    assert.equal(assessTextContrast(sample({ backgroundChain: [layer] })).outcome,
      "not-measurable");
  }
  assert.equal(assessTextContrast(sample({ foreground: "rgba(0,0,0,0.5)" })).outcome,
    "not-measurable");
  assert.equal(assessTextContrast(sample({ backgroundChain: [] })).outcome,
    "not-measurable");
});

test("opaque child does not hide ancestor opacity or blending", () => {
  const opaqueChild = { color: "rgb(255,255,255)", image: "none", opacity: "1", blend: "normal" };
  const ancestors = [
    { color: "rgb(20,20,20)", image: "none", opacity: "0.6", blend: "normal" },
    { color: "rgb(20,20,20)", image: "none", opacity: "1", blend: "multiply" },
  ];
  for (const ancestor of ancestors) {
    const got = assessTextContrast(sample({ backgroundChain: [opaqueChild, ancestor] }));
    assert.equal(got.outcome, "not-measurable");
  }
  // A backdrop image hidden behind an opaque descendant cannot change that
  // descendant's background; it should not invalidate a valid measurement.
  const hiddenImage = { color: "rgb(20,20,20)", image: "linear-gradient(black, white)", opacity: "1", blend: "normal" };
  assert.equal(assessTextContrast(sample({ backgroundChain: [opaqueChild, hiddenImage] })).outcome,
    "meets-sampled-AA");
});
