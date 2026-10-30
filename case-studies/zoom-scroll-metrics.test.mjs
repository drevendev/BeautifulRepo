import assert from "node:assert/strict";
import test from "node:test";
import { assessBottomScroll } from "./zoom-scroll-metrics.mjs";

const data = { scrollY: 1800, maxScrollY: 1800, viewportHeight: 225,
  viewportWidth: 320, documentWidth: 320, footerPresent: true,
  footerVisible: true, footerTextLength: 140, footerTop: 90, footerBottom: 190 };

test("valid reached bottom and footer", () => {
  assert.deepEqual(assessBottomScroll(data), { passed: true,
    reachedBottom: true, footerOnScreen: true, horizontalOverflowCssPx: 0 });
});
test("first screen is not bottom", () => {
  assert.equal(assessBottomScroll({ ...data, scrollY: 0 }).passed, false);
});
test("footer must intersect viewport", () => {
  assert.equal(assessBottomScroll({ ...data, footerPresent: false }).passed, false);
  assert.equal(assessBottomScroll({ ...data, footerTop: 240, footerBottom: 300 }).passed, false);
  assert.equal(assessBottomScroll({ ...data, footerTextLength: 0 }).passed, false);
});
test("horizontal overflow is a finding", () => {
  const result = assessBottomScroll({ ...data, documentWidth: 326 });
  assert.equal(result.horizontalOverflowCssPx, 6);
  assert.equal(result.passed, false);
});
test("missing values and unscrollable pages do not pass", () => {
  assert.equal(assessBottomScroll({ ...data, footerBottom: undefined }).passed, false);
  assert.equal(assessBottomScroll({ ...data, scrollY: 0, maxScrollY: 0 }).passed, false);
});
