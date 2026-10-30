/**
 * Conservative, offline WCAG 2.2 text-contrast calculations for a bounded
 * browser sample. This is not an accessibility-conformance checker.
 *
 * Browser-side code supplies computed foreground, typography and an ordered
 * element-to-root background chain. Unsupported compositing is NOT a pass.
 */
export function parseComputedRgb(value) {
  if (typeof value !== "string") return null;
  const match = /^rgba?\((.*)\)$/i.exec(value.trim());
  if (!match) return null;
  const pieces = match[1].replace(/[,/]/g, " ").trim().split(/\s+/);
  if (pieces.length !== 3 && pieces.length !== 4) return null;
  const numbers = pieces.map(Number);
  if (numbers.some(n => !Number.isFinite(n))) return null;
  const [r, g, b] = numbers;
  const a = numbers.length === 4 ? numbers[3] : 1;
  if ([r, g, b].some(n => n < 0 || n > 255) || a < 0 || a > 1) return null;
  return { r, g, b, a };
}

function luminance(color) {
  const linear = value => {
    const n = value / 255;
    return n <= 0.04045 ? n / 12.92 : ((n + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * linear(color.r) +
    0.7152 * linear(color.g) +
    0.0722 * linear(color.b);
}

export function contrastRatio(a, b) {
  const la = luminance(a), lb = luminance(b);
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
}

/**
 * Return measured contrast or an explicit unknown. Never treat alpha,
 * gradients, image backgrounds, inherited opacity or missing content as PASS.
 * Text-size thresholds follow WCAG 2.2 SC 1.4.3 AA (3:1 large / 4.5:1 normal).
 */
export function assessTextContrast(sample) {
  const base = { label: sample.label, selector: sample.selector, text: sample.text ?? "" };
  const unknown = reason => ({ ...base, outcome: "not-measurable", reason });
  if (!sample.present) return unknown("selector absent");
  if (!sample.visible || !String(sample.text || "").trim()) return unknown("not visible or no text");
  const foreground = parseComputedRgb(sample.foreground);
  if (!foreground || foreground.a !== 1) return unknown("non-opaque or unsupported foreground");
  let background = null;
  for (const layer of sample.backgroundChain || []) {
    if (layer.image !== "none" ||
        Number(layer.opacity) !== 1 ||
        layer.blend !== "normal") {
      return unknown("background image, opacity or blending requires manual assessment");
    }
    const color = parseComputedRgb(layer.color);
    if (!color) return unknown("unsupported background color");
    if (color.a === 0) continue;
    if (color.a !== 1) return unknown("translucent background requires compositing");
    background = color;
    break;
  }
  if (!background) return unknown("no opaque background found");
  const size = Number(sample.fontSizePx);
  const weight = Number(sample.fontWeight);
  if (!Number.isFinite(size) || size <= 0 || !Number.isFinite(weight)) {
    return unknown("unsupported font measurement");
  }
  const large = size >= 24 || (size >= 18.6667 && weight >= 700);
  const threshold = large ? 3 : 4.5;
  const ratio = contrastRatio(foreground, background);
  return {
    ...base,
    outcome: ratio >= threshold ? "meets-sampled-AA" : "below-sampled-AA",
    ratio: Number(ratio.toFixed(2)),
    threshold,
    largeText: large,
    fontSizePx: size,
    fontWeight: weight,
    foreground: sample.foreground,
    background: "rgb(" + [background.r, background.g, background.b].join(", ") + ")",
  };
}
