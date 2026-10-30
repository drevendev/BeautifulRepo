import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";
import { inspectServedAssets, MAX_BYTES } from "./trade-served-assets.mjs";

async function fixture(t, content = "published-source\n") {
  const root = await mkdtemp(path.join(os.tmpdir(), "br-served-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  await mkdir(path.join(root, "docs"));
  await writeFile(path.join(root, "docs/index.html"), content);
  return root;
}
const args = root => ({ sourceRoot: root, siteUrl: "https://example.org/sample/", assets: ["index.html"] });

test("matching served bytes have a reproducible source/served digest", async t => {
  const root = await fixture(t);
  const fetched = [];
  const report = await inspectServedAssets({ ...args(root), fetcher: async (url, options) => {
    fetched.push({ url, options });
    return new Response("published-source\n", { status: 200 });
  } });
  assert.equal(report.assets[0].outcome, "MATCH");
  assert.equal(report.assets[0].sourceSha256, report.assets[0].servedSha256);
  assert.deepEqual(report.summary, { matched: 1, different: 0, unavailable: 0 });
  assert.equal(fetched[0].url, "https://example.org/sample/index.html");
  assert.equal(fetched[0].options.redirect, "manual");
});

test("different served bytes are a finding, not assumed deployment identity", async t => {
  const root = await fixture(t);
  const report = await inspectServedAssets({ ...args(root), fetcher: async () =>
    new Response("different", { status: 200 }) });
  assert.equal(report.assets[0].outcome, "DIFFERENT");
  assert.notEqual(report.assets[0].servedSha256, report.assets[0].sourceSha256);
  assert.deepEqual(report.summary, { matched: 0, different: 1, unavailable: 0 });
});

test("404 and redirect are unavailable, never equal", async t => {
  const root = await fixture(t);
  for (const status of [301, 404]) {
    const report = await inspectServedAssets({ ...args(root), fetcher: async () =>
      new Response(null, { status }) });
    assert.equal(report.assets[0].outcome, "UNAVAILABLE");
    assert.equal(report.assets[0].httpStatus, status);
    assert.equal(report.assets[0].servedSha256, null);
  }
});

test("oversize declared or streamed bodies are rejected before hashing", async t => {
  const root = await fixture(t);
  for (const response of [
    () => new Response("x", { headers: { "Content-Length": String(MAX_BYTES + 1) } }),
    () => new Response(Buffer.alloc(MAX_BYTES + 1, 1)),
  ]) {
    const report = await inspectServedAssets({ ...args(root), fetcher: async () => response() });
    assert.equal(report.assets[0].outcome, "UNAVAILABLE");
    assert.match(report.assets[0].reason, /exceeds byte limit/);
  }
});

test("non-HTTPS URLs, malformed bases and unlisted files are refused", async t => {
  const root = await fixture(t);
  for (const siteUrl of ["http://example.org/", "https://example.org/path", "https://user:pass@example.org/"]) {
    await assert.rejects(() => inspectServedAssets({ ...args(root), siteUrl }), /HTTPS directory/);
  }
  await assert.rejects(() => inspectServedAssets({ ...args(root), assets: ["../../private"] }), /not allowlisted/);
});
