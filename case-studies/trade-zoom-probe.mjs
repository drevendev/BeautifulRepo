#!/usr/bin/env node
/**
 * Real Chromium page-zoom observation for the public saved-run viewer.
 * Run headful under isolated Xvfb. Native X11 key shortcuts change actual
 * browser zoom, not CSS zoom, deviceScaleFactor or CDP pinch scaling.
 */
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
import { assessBottomScroll } from "./zoom-scroll-metrics.mjs";

const targetRoot = process.env.TARGET_ROOT;
const outputDir = process.env.OUTPUT_DIR;
const targetUrl = process.env.TARGET_URL || "https://drevendev.github.io/trade_simulation/";
if (!targetRoot || !outputDir) throw new Error("TARGET_ROOT and OUTPUT_DIR are required");
if (new URL(targetUrl).protocol !== "https:") throw new Error("TARGET_URL must be HTTPS");
if (!process.env.DISPLAY) throw new Error("Run under an isolated Xvfb DISPLAY");
const nativeZoom = path.join(path.dirname(fileURLToPath(import.meta.url)), "native-page-zoom.py");
const x11Capture = path.join(path.dirname(fileURLToPath(import.meta.url)), "native-x11-capture.py");
const requireFromTarget = createRequire(pathToFileURL(path.join(targetRoot, "package.json")));
const { chromium } = requireFromTarget("playwright");
const bytes = await fs.readFile(path.join(targetRoot, "docs/m4-preview.json"));
const fixture = JSON.parse(bytes.toString("utf8"));
const expected = fixture.samples.at(-1);
const sha256 = input => createHash("sha256").update(input).digest("hex");
await fs.mkdir(outputDir, { recursive: true });

const report = {
  observedAt: new Date().toISOString(),
  targetRevision: "36bd70ea399813accf21d350aa5a0067f059757e",
  targetUrl,
  nativeZoomRequested: 4,
  physicalViewportPx: { width: 1280, height: 900 },
  method: "Headful Chromium inside isolated Xvfb, eight real X11 Ctrl+plus shortcuts; verified by DPR ratio and CSS viewport contraction",
  fixtureSha256: sha256(bytes),
  themes: {},
  limitations: [
    "emulated color scheme, not a physical device",
    "Chromium desktop browser zoom only; other browser engines not tested",
    "saved JSON viewer, not an executed TypeScript or .NET simulation",
    "first and bottom physical viewport observations only: middle and expanded chapters remain uninspected",
    "no screen-reader or whole-page WCAG conformance claim",
    "no deployed HTML/JS revision attestation",
  ],
};
let failures = 0;
for (const theme of ["light", "dark"]) {
  const browser = await chromium.launch({ headless: false });
  try {
    const context = await browser.newContext({
      viewport: { width: 1280, height: 900 },
      colorScheme: theme,
      reducedMotion: "reduce",
    });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", err => errors.push(String(err.message)));
    try {
      const response = await page.goto(targetUrl, { waitUntil: "domcontentloaded", timeout: 45000 });
      await page.waitForFunction(
        () => document.querySelector("#spotlight-tick") && !document.querySelector("#spotlight-tick").disabled,
        null,
        { timeout: 30000 },
      );
      await page.locator("#spotlight-tick").evaluate((slider, lastIndex) => {
        slider.value = String(lastIndex);
        slider.dispatchEvent(new Event("input", { bubbles: true }));
      }, fixture.samples.length - 1);
      const metrics = () => page.evaluate(() => ({
        innerWidth: window.innerWidth,
        devicePixelRatio: window.devicePixelRatio,
        visualViewportScale: window.visualViewport.scale,
        bodyZoom: getComputedStyle(document.body).zoom,
        bodyBackground: getComputedStyle(document.body).backgroundColor,
        documentWidth: document.documentElement.scrollWidth,
        viewportWidth: document.documentElement.clientWidth,
        readout: document.querySelector("#spotlight-readout")?.textContent?.trim() || "",
        capital: document.querySelector('[data-spotlight="installedCapital"] dd')?.textContent?.trim() || "",
      }));
      const before = await metrics();
      await page.bringToFront();
      const shortcutLog = execFileSync("python3", [nativeZoom, "8"], {
        encoding: "utf8", timeout: 10000, env: process.env,
      }).trim();
      await page.waitForTimeout(250);
      const after = await metrics();
      const zoomRatio = after.devicePixelRatio / before.devicePixelRatio;
      const native400 = Math.abs(zoomRatio - 4) < 0.03 &&
        Math.abs(after.innerWidth - 320) <= 2 &&
        before.innerWidth === 1280 &&
        Math.abs(after.visualViewportScale - before.visualViewportScale) < 0.01 &&
        before.bodyZoom === after.bodyZoom;
      const liveData = await context.request.get(
        new URL("m4-preview.json", page.url()).toString(),
        { headers: { "Cache-Control": "no-cache" }, timeout: 30000 },
      );
      const liveBytes = liveData.ok() ? await liveData.body() : Buffer.alloc(0);
      const dataExact = liveData.ok() && sha256(liveBytes) === sha256(bytes);
      const lastDataVisible = after.readout.includes("tick " + expected.tick) &&
        after.capital.includes(expected.installedCapital.toFixed(2));
      const overflow = Math.max(0, after.documentWidth - after.viewportWidth);
      // Native zoom may invalidate the compositor surface while metrics are
      // already available. Require two actual paint frames before capturing
      // the physical framebuffer (the capture helper rejects blank pixels).
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(
        () => requestAnimationFrame(resolve)
      )));
      await page.waitForTimeout(900);
      const screenshot = "pages-" + theme + "-native-400-viewport.png";
      // Playwright's full-page screenshot at genuine browser zoom is
      // cropped to the CSS viewport in this Chromium build. Capture the
      // actual Xvfb physical framebuffer instead; this is viewport-only.
      const captureLog = execFileSync("python3", [
        x11Capture, path.join(outputDir, screenshot),
      ], { encoding: "utf8", timeout: 20000, env: process.env }).trim();
      const png = await fs.readFile(path.join(outputDir, screenshot));
      const pngWidth = png.readUInt32BE(16);
      const pngHeight = png.readUInt32BE(20);
      const screenshotCoversViewport = pngWidth === 1440 && pngHeight === 1200;
      for (let index = 0; index < 4; index++) await page.keyboard.press("Tab");
      const keyboard = await page.evaluate(() => ({
        id: document.activeElement?.id || null,
        focusVisible: Boolean(document.activeElement?.matches(":focus-visible")),
      }));
      const keyboardPassed = keyboard.id === "spotlight-tick" && keyboard.focusVisible;
      // A first-screen screenshot cannot establish the reachability of
      // content below the fold. Scroll actual native-zoom Chromium to its
      // document end, inspect footer geometry and capture a second X11 frame.
      await page.evaluate(() => window.scrollTo({
        top: document.documentElement.scrollHeight, left: 0, behavior: "instant",
      }));
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(
        () => requestAnimationFrame(resolve)
      )));
      await page.waitForTimeout(700);
      const bottomMetrics = await page.evaluate(() => {
        const footer = document.querySelector("footer");
        const rect = footer?.getBoundingClientRect();
        const style = footer ? getComputedStyle(footer) : null;
        return {
          scrollY: window.scrollY,
          maxScrollY: Math.max(0, document.documentElement.scrollHeight - window.innerHeight),
          viewportHeight: window.innerHeight,
          viewportWidth: document.documentElement.clientWidth,
          documentWidth: document.documentElement.scrollWidth,
          footerPresent: Boolean(footer),
          footerVisible: Boolean(footer?.getClientRects().length && style &&
            style.display !== "none" && style.visibility === "visible"),
          footerTextLength: (footer?.textContent || "").trim().length,
          footerTop: rect?.top ?? null,
          footerBottom: rect?.bottom ?? null,
        };
      });
      const bottom = assessBottomScroll(bottomMetrics);
      const bottomScreenshot = "pages-" + theme + "-native-400-bottom.png";
      const bottomCaptureLog = execFileSync("python3", [
        x11Capture, path.join(outputDir, bottomScreenshot),
      ], { encoding: "utf8", timeout: 20000, env: process.env }).trim();
      const bottomPng = await fs.readFile(path.join(outputDir, bottomScreenshot));
      const bottomScreenshotCoversViewport =
        bottomPng.readUInt32BE(16) === 1440 && bottomPng.readUInt32BE(20) === 1200;
      const passed = native400 && dataExact && lastDataVisible && overflow <= 1 && screenshotCoversViewport &&
        response?.status() === 200 && keyboardPassed && bottom.passed &&
        bottomScreenshotCoversViewport && errors.length === 0;
      report.themes[theme] = {
        passed, before, after, zoomRatio, native400, shortcutLog,
        htmlHttpStatus: response?.status() ?? null, jsonHttpStatus: liveData.status(),
        dataExact, lastDataVisible, horizontalOverflowCssPx: overflow,
        keyboard, keyboardPassed, screenshot, captureLog, pngWidth, pngHeight, screenshotCoversViewport,
        bottomMetrics, bottom, bottomScreenshot, bottomCaptureLog, bottomScreenshotCoversViewport, errors,
      };
      if (!passed) failures++;
    } catch (error) {
      failures++;
      report.themes[theme] = { passed: false, error: String(error), errors };
      try {
        await page.screenshot({ path: path.join(outputDir, "pages-" + theme + "-failure.png"), fullPage: true, scale: "device" });
      } catch { /* navigation or renderer failure may leave no screenshot */ }
    } finally {
      await context.close();
    }
  } finally {
    await browser.close();
  }
}
const themesDistinct = Boolean(report.themes.light?.after?.bodyBackground &&
  report.themes.dark?.after?.bodyBackground &&
  report.themes.light.after.bodyBackground !== report.themes.dark.after.bodyBackground);
if (!themesDistinct) failures++;
report.themesDistinct = themesDistinct;
report.failures = failures;
await fs.writeFile(path.join(outputDir, "native-zoom-observations.json"), JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify(report, null, 2));
if (process.env.GITHUB_STEP_SUMMARY) {
  const rows = [
    "## Native Chromium 400% page-zoom observation", "",
    "Headful Chromium received OS-level browser zoom shortcuts on an isolated Xvfb screen.",
    "The asserted ratio checks actual devicePixelRatio and CSS viewport contraction, not pinch/device emulation.", "",
    "| Theme | Native 400% verified | CSS viewport | Horizontal overflow | Saved JSON exact | Keyboard tick focus | Footer reached |",
    "| --- | --- | ---: | ---: | --- | --- | --- |",
  ];
  for (const theme of ["light", "dark"]) {
    const row = report.themes[theme] || {};
    rows.push("| " + theme + " | " + (row.native400 ?? "NOT OBSERVED") +
      " | " + (row.after?.innerWidth ?? "NOT OBSERVED") +
      " | " + (row.horizontalOverflowCssPx ?? "NOT OBSERVED") +
      " | " + (row.dataExact ?? "NOT OBSERVED") +
      " | " + (row.keyboardPassed ?? "NOT OBSERVED") +
      " | " + (row.bottom?.passed ?? "NOT OBSERVED") + " |");
  }
  rows.push("", "Only first and bottom physical viewports are sampled; middle and expanded chapters remain uninspected.",
    "No physical phone, screen-reader, whole-page WCAG or deployed-code provenance claim.",
    "Failures: " + failures + ".", "");
  await fs.appendFile(process.env.GITHUB_STEP_SUMMARY, rows.join("\n"));
}
if (failures) process.exitCode = 1;
