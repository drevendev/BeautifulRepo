#!/usr/bin/env node
/**
 * Read-only, bounded comparison of selected served Pages bytes against an
 * immutable source checkout. Byte agreement is not proof of a deployed commit.
 * Runs with Node 22+ and no extra npm dependencies.
 */
import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

export const SOURCE_REVISION = "36bd70ea399813accf21d350aa5a0067f059757e";
export const PUBLIC_ASSETS = Object.freeze(["index.html", "m4.css", "showcase.js", "m4.js"]);
export const MAX_BYTES = 512 * 1024;
const digest = bytes => createHash("sha256").update(bytes).digest("hex");

async function boundedBody(response, limit) {
  const declared = response.headers?.get?.("content-length");
  if (declared !== null && declared !== undefined && Number.isFinite(Number(declared)) &&
      Number(declared) > limit) {
    throw new Error("response exceeds byte limit (declared size)");
  }
  if (!response.body) throw new Error("response has no body");
  const chunks = [];
  let size = 0;
  for await (const chunk of response.body) {
    size += chunk.byteLength;
    if (size > limit) {
      throw new Error("response exceeds byte limit (streamed size)");
    }
    chunks.push(Buffer.from(chunk));
  }
  return Buffer.concat(chunks, size);
}

export async function inspectServedAssets({ sourceRoot, siteUrl, fetcher = fetch, assets = PUBLIC_ASSETS }) {
  const base = new URL(siteUrl);
  if (base.protocol !== "https:" || base.username || base.password ||
      !base.pathname.endsWith("/")) {
    throw new Error("siteUrl must be an HTTPS directory URL without credentials");
  }
  const result = [];
  for (const asset of assets) {
    if (!PUBLIC_ASSETS.includes(asset)) throw new Error("asset not allowlisted: " + asset);
    const expected = await fs.readFile(path.join(sourceRoot, "docs", asset));
    if (expected.byteLength > MAX_BYTES) throw new Error("pinned source exceeds byte limit: " + asset);
    const url = new URL(asset, base).toString();
    const row = {
      asset, url, sourceSha256: digest(expected), sourceBytes: expected.byteLength,
      httpStatus: null, servedSha256: null, servedBytes: null, outcome: "UNAVAILABLE",
    };
    try {
      const response = await fetcher(url, {
        redirect: "manual", headers: { "Cache-Control": "no-cache" },
        signal: AbortSignal.timeout(20000),
      });
      row.httpStatus = response.status;
      if (response.status !== 200 || response.redirected) {
        row.reason = "HTTP status not 200 or unexpected redirect";
      } else {
        const served = await boundedBody(response, MAX_BYTES);
        row.servedBytes = served.byteLength;
        row.servedSha256 = digest(served);
        row.outcome = served.equals(expected) ? "MATCH" : "DIFFERENT";
      }
    } catch (error) {
      row.reason = String(error?.message || error).slice(0, 200);
    }
    result.push(row);
  }
  return {
    observedAt: new Date().toISOString(), sourceRevision: SOURCE_REVISION, siteUrl: base.toString(),
    method: "Exact served byte comparison of four named public HTML/CSS/JS resources with the pinned source checkout; redirects refused; each body capped at 512 KiB",
    assets: result,
    summary: {
      matched: result.filter(x => x.outcome === "MATCH").length,
      different: result.filter(x => x.outcome === "DIFFERENT").length,
      unavailable: result.filter(x => x.outcome === "UNAVAILABLE").length,
    },
    limits: [
      "matching file bytes do not identify a deployed commit SHA or the Pages build configuration",
      "only four named resources are sampled, not imported images, data or all deployment files",
      "the observation is time-specific; a later deployment may differ",
      "the comparison does not exercise JavaScript behavior, accessibility or simulation correctness",
    ],
  };
}

async function main() {
  const sourceRoot = process.env.TARGET_ROOT;
  const outputDir = process.env.OUTPUT_DIR;
  if (!sourceRoot || !outputDir) throw new Error("TARGET_ROOT and OUTPUT_DIR are required");
  const report = await inspectServedAssets({
    sourceRoot,
    siteUrl: process.env.TARGET_URL || "https://drevendev.github.io/trade_simulation/",
  });
  await fs.mkdir(outputDir, { recursive: true });
  await fs.writeFile(path.join(outputDir, "served-assets.json"), JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report, null, 2));
  if (process.env.GITHUB_STEP_SUMMARY) {
    const lines = [
      "## Served asset fingerprints (read-only)", "",
      "Four selected served resources are compared byte-for-byte against pinned source " + SOURCE_REVISION + ".",
      "Byte agreement does NOT establish the deployed commit SHA.", "",
      "| Resource | Outcome | HTTP | Source SHA-256 | Served SHA-256 |",
      "| --- | --- | ---: | --- | --- |",
      ...report.assets.map(x => "| " + x.asset + " | " + x.outcome + " | " +
        (x.httpStatus ?? "—") + " | " + x.sourceSha256 + " | " +
        (x.servedSha256 ?? "unavailable") + " |"),
      "", "Matches: " + report.summary.matched + "; different: " + report.summary.different +
      "; unavailable: " + report.summary.unavailable + ".", "",
      "The JSON artifact records byte lengths, errors and scope limitations.", "",
    ];
    await fs.appendFile(process.env.GITHUB_STEP_SUMMARY, lines.join("\n"));
  }
  // Differences are measured findings, not a reason to invalidate existing
  // browser tests; inability to inspect all four files is inconclusive.
  if (report.summary.unavailable) process.exitCode = 1;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  await main();
}
