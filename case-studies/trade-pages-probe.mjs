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
  method: "Real headless Chromium at 320 CSS px; emulated light/dark preference",
  expectedFixtureSha256: sha256(fixtureBytes),
  expectedLastTick: expected.tick,
  expectedLastCapital: expected.installedCapital,
  themes: {},
  notTested: [
    "physical phone",
    "400% browser zoom",
    "screen reader",
    "complete keyboard navigation",
    "runtime TypeScript or .NET simulation",
    "entire deployed HTML/JS commit provenance",
  ],
};
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
      report.themes[theme] = {
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
      if (!dataExact || !capitalCorrect || !tickCorrect || response?.status() !== 200 || errors.length) {
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
    "This is not a phone, 400% zoom, screen-reader test, or proof of deployed HTML/JS revision.",
    "",
    "| Theme | Live saved JSON matches pinned bytes | Last tick/capital | Page overflow |",
    "| --- | --- | --- | --- |"];
  for (const theme of ["light", "dark"]) {
    const data = report.themes[theme] || {};
    rows.push("| " + theme + " | " + (data.dataExact ?? "NOT OBSERVED") +
      " | " + ((data.tickCorrect && data.capitalCorrect) ?? "NOT OBSERVED") +
      " | " + (data.horizontalOverflowCssPx ?? "NOT OBSERVED") + " CSS px |");
  }
  rows.push("", "Artifacts contain a JSON observation record and full-page screenshots when captured.",
    "Different computed body backgrounds: " + themesDistinct + ".",
    "Failures (network/data/viewer): " + failures + ".",
    "");
  await fs.appendFile(process.env.GITHUB_STEP_SUMMARY, rows.join("\n"));
}
if (failures) process.exitCode = 1;
