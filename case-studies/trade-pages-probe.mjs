#!/usr/bin/env node
/**
 * Read-only evidence capture for the live trade_simulation GitHub Pages viewer.
 *
 * This is a case study probe, not an accessibility audit or deployment attestation.
 * Run from BeautifulRepo with TARGET_ROOT pointing to a pinned target checkout
 * whose lockfile supplies Playwright, and OUTPUT_DIR pointing outside both trees.
 */
import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";
import { assessTextContrast } from "./contrast-metrics.mjs";
import { COLLAPSED_TABS, assessCollapsedTabs, assessM3Keyboard } from "./keyboard-path-metrics.mjs";

const target = process.env.TARGET_ROOT;
const output = process.env.OUTPUT_DIR;
const site = process.env.TARGET_URL || "https://drevendev.github.io/trade_simulation/";
if (!target || !output) {
  throw new Error("TARGET_ROOT and OUTPUT_DIR must be provided");
}
if (new URL(site).protocol !== "https:") {
  throw new Error("TARGET_URL must be HTTPS");
}
const requireFromTarget = createRequire(pathToFileURL(path.join(target, "package.json")));
const { chromium } = requireFromTarget("playwright");
const fixtureBytes = await fs.readFile(path.join(target, "docs/m4-preview.json"));
const fixture = JSON.parse(fixtureBytes.toString("utf8"));
const expected = fixture.samples.at(-1);
const sha256 = bytes => createHash("sha256").update(bytes).digest("hex");
await fs.mkdir(output, { recursive: true });

const report = {
  observedAt: new Date().toISOString(),
  sourceRevision: "36bd70ea399813accf21d350aa5a0067f059757e",
  targetUrl: site,
  viewportCssPx: { width: 320, height: 900 },
  method: "Headless Chromium at 320 CSS px; light/dark, five-stop entrance, ten-stop collapsed Tab path, native M3 tick interaction and bounded text contrast",
  expectedFixtureSha256: sha256(fixtureBytes),
  expectedLastTick: expected.tick,
  expectedLastCapital: expected.installedCapital,
  themes: {},
  notTested: [
    "physical phone",
    "400% browser zoom",
    "screen reader",
    "focus-indicator contrast, full WCAG conformance, alpha/image compositing and visually verified typography",
    "expanded M4 and legacy controls beyond the sampled collapsed-page/M3 route",
    "runtime TypeScript or .NET simulation",
    "entire deployed HTML/JS commit provenance",
  ],
};

/**
 * Sample the first keyboard path from the landing page, not an exhaustive
 * accessibility audit. Preserve actual Tab order and browser focus styles.
 * Keyboard-driven slider changes and native disclosure are observed without
 * dispatching synthetic events. This does not model a screen reader.
 */
async function observeKeyboardEntrance(page, samples) {
  const result = { tabStops: [], slider: {}, chapter: {}, passed: false };
  const stops = [
    ["M4 entrance link", 'a[href="#chapter-m4"]'],
    ["M3 entrance link", 'a[href="#chapter-m3"]'],
    ["Saved milestone selector", "#showcase-milestone"],
    ["Observed tick slider", "#spotlight-tick"],
    ["M4 chapter disclosure", "#chapter-m4 > summary"],
  ];
  for (const [label, selector] of stops) {
    await page.keyboard.press("Tab");
    const focus = await page.evaluate(wanted => {
      const node = document.activeElement;
      const style = node ? getComputedStyle(node) : null;
      return {
        matches: Boolean(node?.matches(wanted)),
        focusVisible: Boolean(node?.matches(":focus-visible")),
        outline: style ? style.outlineStyle + " " + style.outlineWidth : null,
        outlined: Boolean(style && style.outlineStyle !== "none" &&
          parseFloat(style.outlineWidth) > 0),
        actualTag: node?.tagName || null,
        actualId: node?.id || null,
      };
    }, selector);
    result.tabStops.push({ label, selector, ...focus });
    if (selector === "#spotlight-tick") {
      await page.keyboard.press("ArrowLeft");
      result.slider.previous = await page.evaluate(() => ({
        index: Number(document.querySelector("#spotlight-tick").value),
        readout: document.querySelector("#spotlight-readout").textContent.trim(),
      }));
      await page.keyboard.press("ArrowRight");
      result.slider.restored = await page.evaluate(() => ({
        index: Number(document.querySelector("#spotlight-tick").value),
        readout: document.querySelector("#spotlight-readout").textContent.trim(),
      }));
    }
  }
  result.chapter.wasOpen = await page.locator("#chapter-m4").evaluate(node => node.open);
  await page.keyboard.press("Enter");
  result.chapter.openAfterEnter = await page.locator("#chapter-m4").evaluate(node => node.open);
  const previous = samples.at(-2), last = samples.at(-1);
  result.slider.previousCorrect = result.slider.previous?.index === samples.length - 2 &&
    result.slider.previous?.readout.includes("tick " + previous.tick);
  result.slider.restoredCorrect = result.slider.restored?.index === samples.length - 1 &&
    result.slider.restored?.readout.includes("tick " + last.tick);
  result.passed = result.tabStops.every(step =>
    step.matches && step.focusVisible && step.outlined) &&
    result.slider.previousCorrect && result.slider.restoredCorrect &&
    !result.chapter.wasOpen && result.chapter.openAfterEnter;
  return result;
}


/**
 * Collect a few real rendered text/background pairs. This samples the saved
 * viewer, not every text node, hidden chapter, SVG label or focus state.
 * Complex layers are reported as not-measurable by the pure metric module.
 */
async function observeTextContrast(page) {
  const samples = await page.evaluate(() => {
    const targets = [
      ["Eyebrow", ".showcase-eyebrow"],
      ["Lead", ".showcase-lead"],
      ["Primary entrance", ".showcase-cta"],
      ["Provenance", ".showcase-provenance"],
      ["Tick label", 'label[for="spotlight-tick"]'],
      ["Metric label", "#spotlight-metrics dt"],
      ["Metric unit", "#spotlight-metrics dd small"],
      ["Chapter hint", "#chapter-m4 > summary small"],
      ["Footer", "footer"],
    ];
    return targets.map(([label, selector]) => {
      const node = document.querySelector(selector);
      if (!node) return { label, selector, present: false };
      const style = getComputedStyle(node);
      const backgroundChain = [];
      for (let current = node, depth = 0; current && depth < 24; current = current.parentElement, depth++) {
        const css = getComputedStyle(current);
        backgroundChain.push({
          color: css.backgroundColor,
          image: css.backgroundImage,
          opacity: css.opacity,
          blend: css.mixBlendMode,
        });
      }
      return {
        label, selector, present: true,
        visible: node.getClientRects().length > 0 &&
          style.visibility === "visible" && style.display !== "none",
        text: (node.textContent || "").trim().slice(0, 140),
        foreground: style.color,
        fontSizePx: Number.parseFloat(style.fontSize),
        fontWeight: style.fontWeight,
        backgroundChain,
      };
    });
  });
  return samples.map(assessTextContrast);
}

/**
 * Independently traverse the collapsed chapter surface via actual keyboard
 * presses and Enter-opened M3 tick input. Name candidates are DOM evidence,
 * not computed assistive-tech names or a screen-reader test.
 */
async function observeChapterKeyboard(context, theme) {
  const tabPage = await context.newPage();
  const result = { tabStops: [], passed: false };
  try {
    const response = await tabPage.goto(site, { waitUntil: "domcontentloaded", timeout: 45000 });
    await tabPage.waitForFunction(
      () => document.querySelector("#spotlight-tick") && !document.querySelector("#spotlight-tick").disabled,
      null, { timeout: 30000 },
    );
    const focus = wanted => tabPage.evaluate(selector => {
      const node = document.activeElement;
      const style = node ? getComputedStyle(node) : null;
      const rect = node?.getBoundingClientRect();
      const label = (node?.getAttribute("aria-label") ||
        [...(node?.labels || [])].map(item => item.textContent || "").join(" ") ||
        node?.textContent || "").trim();
      return {
        selector, matches: Boolean(node?.matches(selector)),
        actualTag: node?.tagName || null, actualId: node?.id || null,
        focusVisible: Boolean(node?.matches(":focus-visible")),
        outlined: Boolean(style && style.outlineStyle !== "none" &&
          parseFloat(style.outlineWidth) > 0),
        hasNameCandidate: label.length > 0, nameCandidate: label.slice(0, 120),
        descriptionTarget: node?.getAttribute("aria-describedby") || null,
        inViewport: Boolean(rect && rect.width > 0 && rect.height > 0 &&
          rect.top < innerHeight && rect.bottom > 0 &&
          rect.left < innerWidth && rect.right > 0),
      };
    }, wanted);
    for (const step of COLLAPSED_TABS) {
      await tabPage.keyboard.press("Tab");
      result.tabStops.push({ label: step.label, ...await focus(step.selector) });
    }
    result.collapsed = assessCollapsedTabs(result.tabStops);
    // From the last (Legacy) summary, return to the fourth-from-last (M3).
    for (let i = 0; i < 4; i++) await tabPage.keyboard.press("Shift+Tab");
    const summaryFocus = await focus("#chapter-m3 > summary");
    const openBefore = await tabPage.locator("#chapter-m3").evaluate(node => node.open);
    await tabPage.keyboard.press("Enter");
    const openAfterEnter = await tabPage.locator("#chapter-m3").evaluate(node => node.open);
    await tabPage.waitForFunction(() => {
      const input = document.querySelector("#m3-tick");
      return input && Number(input.max) >= 2 && !input.disabled;
    }, null, { timeout: 30000 });
    await tabPage.keyboard.press("Tab");
    const tickFocus = await focus("#m3-tick");
    const sample = () => tabPage.evaluate(() => {
      const input = document.querySelector("#m3-tick");
      return {
        value: Number(input?.value), max: Number(input?.max),
        readout: (document.querySelector("#m3-tick-readout")?.textContent || "").trim(),
      };
    });
    const before = await sample();
    await tabPage.keyboard.press("ArrowLeft");
    const left = await sample();
    await tabPage.keyboard.press("ArrowRight");
    const restored = await sample();
    const observed = { summaryFocus, openBefore, openAfterEnter, tickFocus, before, left, restored };
    result.m3 = { ...observed, ...assessM3Keyboard(observed) };
    const screenshot = "pages-" + theme + "-m3-keyboard.png";
    await tabPage.screenshot({ path: path.join(output, screenshot) });
    result.screenshot = screenshot;
    result.httpStatus = response?.status() ?? null;
    result.passed = result.httpStatus === 200 && result.collapsed.passed && result.m3.passed;
    return result;
  } finally {
    await tabPage.close();
  }
}

let failures = 0;
const browser = await chromium.launch({ headless: true });
try {
  for (const theme of ["light", "dark"]) {
    const context = await browser.newContext({
      viewport: { width: 320, height: 900 },
      colorScheme: theme,
      reducedMotion: "reduce",
    });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", error => errors.push(String(error.message)));
    try {
      const response = await page.goto(site, {
        waitUntil: "domcontentloaded",
        timeout: 45000,
      });
      await page.waitForFunction(
        () => {
          const slider = document.querySelector("#spotlight-tick");
          return slider && !slider.disabled;
        },
        null,
        { timeout: 30000 },
      );
      const liveData = await context.request.get(
        new URL("m4-preview.json", page.url()).toString(),
        { headers: { "Cache-Control": "no-cache" }, timeout: 30000 },
      );
      const liveBytes = liveData.ok() ? await liveData.body() : Buffer.alloc(0);
      const dataExact = liveData.ok() && sha256(liveBytes) === sha256(fixtureBytes);
      await page.locator("#spotlight-tick").evaluate((slider, index) => {
        slider.value = String(index);
        slider.dispatchEvent(new Event("input", { bubbles: true }));
      }, fixture.samples.length - 1);
      const observed = await page.evaluate(() => ({
        title: document.title,
        heading: document.querySelector("#showcase-title")?.textContent?.trim() || "",
        runSummary: document.querySelector("#m4-run-summary")?.textContent?.trim() || "",
        readout: document.querySelector("#spotlight-readout")?.textContent?.trim() || "",
        capital: document.querySelector('[data-spotlight="installedCapital"] dd')?.textContent?.trim() || "",
        bodyBackground: getComputedStyle(document.body).backgroundColor,
        documentWidth: document.documentElement.scrollWidth,
        viewportWidth: document.documentElement.clientWidth,
      }));
      const capitalCorrect = observed.capital.includes(expected.installedCapital.toFixed(2));
      const tickCorrect = observed.readout.includes("tick " + expected.tick);
      const screenshot = "pages-" + theme + "-320.png";
      await page.screenshot({ path: path.join(output, screenshot), fullPage: true });
      const keyboard = await observeKeyboardEntrance(page, fixture.samples);
      const textContrast = await observeTextContrast(page);
      const chapterKeyboard = await observeChapterKeyboard(context, theme);
      const measuredTextCount = textContrast.filter(row => row.outcome !== "not-measurable").length;
      report.themes[theme] = {
        keyboard,
        chapterKeyboard,
        textContrast,
        measuredTextCount,
        htmlHttpStatus: response?.status() ?? null,
        jsonHttpStatus: liveData.status(),
        liveFixtureSha256: liveData.ok() ? sha256(liveBytes) : null,
        dataExact,
        capitalCorrect,
        tickCorrect,
        horizontalOverflowCssPx: Math.max(0, observed.documentWidth - observed.viewportWidth),
        screenshot,
        ...observed,
        errors,
      };
      if (!dataExact || !capitalCorrect || !tickCorrect || !keyboard.passed || !chapterKeyboard.passed || measuredTextCount < 6 || response?.status() !== 200 || errors.length) {
        failures++;
      }
    } catch (error) {
      failures++;
      report.themes[theme] = { failed: true, message: String(error), errors };
      try {
        await page.screenshot({ path: path.join(output, "pages-" + theme + "-failure.png"), fullPage: true });
      } catch {
        // A navigation failure may have no page to capture.
      }
    } finally {
      await context.close();
    }
  }
} finally {
  await browser.close();
  await fs.writeFile(path.join(output, "observations.json"), JSON.stringify(report, null, 2) + "\n");
}
const light = report.themes.light;
const dark = report.themes.dark;
const themesDistinct = Boolean(light?.bodyBackground && dark?.bodyBackground &&
  light.bodyBackground !== dark.bodyBackground);
if (!themesDistinct) failures++;
console.log(JSON.stringify({
  sourceRevision: report.sourceRevision,
  expectedFixtureSha256: report.expectedFixtureSha256,
  themes: report.themes,
  distinctBodyBackgrounds: themesDistinct,
  failures,
  notTested: report.notTested,
}, null, 2));
if (process.env.GITHUB_STEP_SUMMARY) {
  const rows = ["## Live trade_simulation Pages: browser observations",
    "",
    "Observed Chromium at **320 CSS px** in both emulated color schemes.",
    "Computed text contrast uses WCAG 2.2 SC 1.4.3 AA thresholds only for nine named rendered samples; complex layers remain NOT MEASURABLE.",
    "This is not a phone, 400% zoom, screen-reader test, focus contrast audit, exhaustive expanded-chart traversal or proof of deployed HTML/JS revision.",
    "",
    "| Theme | Saved JSON exact | Last tick/capital | Overflow | Five-stop entrance | Collapsed chapters | M3 tick |",
    "| --- | --- | --- | --- | --- | --- |"];
  for (const theme of ["light", "dark"]) {
    const data = report.themes[theme] || {};
    rows.push("| " + theme + " | " + (data.dataExact ?? "NOT OBSERVED") +
      " | " + ((data.tickCorrect && data.capitalCorrect) ?? "NOT OBSERVED") +
      " | " + (data.horizontalOverflowCssPx ?? "NOT OBSERVED") + " CSS px" +
      " | " + (data.keyboard?.passed ?? "NOT OBSERVED") +
      " | " + (data.chapterKeyboard?.collapsed?.passed ?? "NOT OBSERVED") +
      " | " + (data.chapterKeyboard?.m3?.passed ?? "NOT OBSERVED") + " |");
  }
  rows.push("", "### Bounded rendered text contrast", "",
    "| Theme | Sample | Contrast ratio | AA threshold | Observation |",
    "| --- | --- | ---: | ---: | --- |");
  for (const theme of ["light", "dark"]) {
    for (const row of report.themes[theme]?.textContrast || []) {
      rows.push("| " + theme + " | " + row.label +
        " | " + (row.ratio ?? "NOT MEASURABLE") +
        " | " + (row.threshold ?? "—") +
        " | " + row.outcome + " |");
    }
  }
  rows.push("", "These are selected computed-style values, not full-page WCAG conformance or observed visual focus contrast.",
    "", "Artifacts contain a JSON observation record and full-page screenshots when captured.",
    "Different computed body backgrounds: " + themesDistinct + ".",
    "Failures (network/data/viewer/selected keyboard path): " + failures + ".",
    "");
  await fs.appendFile(process.env.GITHUB_STEP_SUMMARY, rows.join("\n"));
}
if (failures) process.exitCode = 1;
