# Keep repository images proportionate to their evidence

A useful screenshot can still make a checkout heavier than necessary. Before adding
hero images, animated demos or multiple theme variants, inventory the **files
actually checked into the repository**. Decide what is worth retaining, and keep
important results available as text even when an image does not load.

GitHub [recommends keeping repositories small](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)
for cloning and maintenance. Its Git file-size restrictions are **not** image
performance budgets. GitHub also [recommends repository-relative image links](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
for Markdown. Both official pages were checked **2026-11-22 UTC**.

## Reproduce an offline inventory

From a Python 3.11+ BeautifulRepo checkout:

```sh
python -I tools/media_budget.py --root .
python -I tools/media_budget.py --root ../my-repo --max-file-kib 512 --max-total-kib 4096 --format json
```

The original, dependency-free inventory uses file metadata only. It looks for
.png, .jpg, .jpeg, .gif, .webp, .svg, .avif and .apng, without
opening or decoding images, following directory/symbolic-link redirects
or calling the network. It also refuses image files with multiple hard links
(`st_nlink > 1`): an alias could point outside the selected checkout and
metadata cannot establish where every link lives. Such a file makes the
inventory **incomplete** (exit 2) and is excluded from totals; this is
conservative, even when all the links happen to be inside the checkout.
Non-image hard links are outside this inventory's scope. The tool skips
.git, node_modules and common local virtual environments; other
nested folders count. The largest five images are listed so a maintainer can
choose what to investigate first. The default advisory budgets (1 MiB per
file, 8 MiB total) are **our example values**, not GitHub requirements,
image-accessibility standards or measured page-load thresholds.

Exit **0** means the chosen size budgets were met for the inventoried files;
**1** means one or both budgets were exceeded; **2** means input or inventory
was incomplete (including a redirect or scan limit). status in JSON
separates ok, findings and incomplete. The total includes unreferenced
assets and both light/dark variants; it is **not** what the README loads in a
browser. The checker neither parses Markdown references nor measures
compression, bandwidth, Git history, render quality or layout shifts.

## Use the findings, not just the numbers

Imagine a fictional README with a 3 MiB hero screenshot and two 1 MiB
light/dark variants. Start by checking whether each image proves a distinct
claim. Crop or re-export a redundant image **without sacrificing legibility**;
use a concise caption and a real text equivalent for essential details.
Compare the replacement visually at the widths and themes readers use. Run
python tools/docs_links.py and python tools/html_navigation.py to check
local destinations after renaming files, then manually verify actual rendering.

Set a budget appropriate to your project and document why. An intentionally
large research figure can deserve an exception; smaller bytes do not imply
better alt text or comprehension. Treat the inventory as **advisory** until
your own repository agrees on thresholds. Do not treat its PASS as a WCAG,
GitHub-rendering or web-performance certification.
