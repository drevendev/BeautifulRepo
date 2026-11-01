/**
 * Conservative, read-only focus-outline color sampling for an observed
 * native keyboard path. Compare computed opaque CSS colors only; an actual
 * pixel, area, screen-reader or WCAG conformance result is not inferred.
 */
import { contrastRatio, parseComputedRgb } from "./contrast-metrics.mjs";

export function assessFocusOutline(sample) {
  const base = { label: sample?.label ?? null, selector: sample?.selector ?? null };
  const unknown = reason => ({ ...base, outcome: "not-measurable", reason });
  if (!sample || sample.present !== true || sample.matches !== true ||
      sample.focusVisible !== true || sample.inViewport !== true) {
    return unknown("missing, mismatched or non-visible keyboard focus");
  }
  // A focused element can have an opaque outline yet be invisible after its own
  // opacity, filter or blend is applied. Treat all non-identity (or missing)
  // focused-element compositing as unknown, not as measured contrast.
  if (Number(sample.focusOpacity) !== 1 || sample.focusFilter !== "none" ||
      sample.focusBackdropFilter !== "none" || sample.focusBlend !== "normal") {
    return unknown("focused-element compositing requires visual assessment");
  }
  if (sample.outlineStyle !== "solid" || !Number.isFinite(sample.outlineWidthPx) ||
      sample.outlineWidthPx < 2) {
    return unknown("requires a solid outline at least two CSS pixels wide");
  }
  if (!Number.isFinite(sample.outlineOffsetPx) || sample.outlineOffsetPx < 1) {
    return unknown("inside or touching component boundary; adjacent colors ambiguous");
  }
  const outline = parseComputedRgb(sample.outlineColor);
  if (!outline || outline.a !== 1) return unknown("unsupported or translucent outline color");
  let background = null;
  const chain = sample.backgroundChain;
  if (!Array.isArray(chain) || chain.length === 0 || chain.length > 24 ||
      sample.chainTruncated === true) {
    return unknown("missing or truncated ancestor background chain");
  }
  for (const layer of chain) {
    if (Number(layer.opacity) !== 1 || layer.blend !== "normal" ||
        layer.filter !== "none" || layer.backdropFilter !== "none") {
      return unknown("ancestor compositing requires visual assessment");
    }
    if (background) continue;
    if (layer.image !== "none") return unknown("background image requires visual assessment");
    const color = parseComputedRgb(layer.color);
    if (!color) return unknown("unsupported background color");
    if (color.a === 0) continue;
    if (color.a !== 1) return unknown("translucent background requires compositing");
    background = color;
  }
  if (!background) return unknown("no opaque adjacent background resolved");
  const ratio = contrastRatio(outline, background);
  return {
    ...base,
    outcome: ratio >= 3 ? "sampled-3-to-1-or-better" : "sampled-below-3-to-1",
    ratio: Number(ratio.toFixed(2)),
    threshold: 3,
    outlineWidthPx: sample.outlineWidthPx,
    outlineOffsetPx: sample.outlineOffsetPx,
    outlineColor: sample.outlineColor,
    backgroundColor: `rgb(${background.r}, ${background.g}, ${background.b})`,
  };
}
