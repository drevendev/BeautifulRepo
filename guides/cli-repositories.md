# Make a command-line repository easy to try

A CLI project is judged in the terminal. A striking banner can attract attention, but
readers need to know **what command to run, what it does, and whether it worked**. This
starter kit is for maintainers writing a README for a CLI tool, including one that has
not shipped a distributable package yet.

## The first screen: promise → command → result

Show a specific outcome before a feature inventory. Prefer a deterministic,
copyable command using safe sample data and include representative stdout or an artifact
that can be inspected. State the working directory and prerequisites; commands copied
from a README fail when they silently depend on a maintainer's environment.

Our [working Rowcount example](../examples/cli-starter/README.md) follows this pattern:

```bash
python examples/cli-starter/rowcount.py examples/cli-starter/sample.csv
```

```text
Data rows: 3
```

Those bytes are backed by an actual script, input file and black-box tests in this
repository. The script is a **documentation demo**, not a separately distributed tool.

## A reader's decision path

1. **Can it solve my problem?** Say what goes in, what comes out, and a major limitation.
2. **Can I try it safely?** Give a short offline or sample-data path, prerequisites and
   platform assumptions. Identify commands that write files, access a network, or send data.
3. **How do I install it?** Give only methods you maintain and verify: source checkout,
   package manager or published binaries. A source command is not an installation claim.
4. **How do I operate it?** Show `--help` discovery, exit status conventions and where
   errors go. Document configuration, destructive options and output formats.
5. **Can I trust the instructions?** Test the quickstart against the documented revision,
   label untested platforms, and link issue, contribution, security and license information.

## Installation claims require evidence

A Python command-line application **can** be packaged with a console-script entry point,
then installed in an isolated environment with `pipx`, as shown by the Python Packaging
User Guide. That does not make `pipx install some-name` a valid instruction for an
unpublished project. Similarly, binary downloads, Homebrew and WinGet lines should link
to *real*, maintained distribution artifacts—not hypothetical availability.

Choose one verified happy path before listing every possible installer. Show the
supported Python/runtime version or OS, required external services, and the expected
command name. If this is a source-only project, say so openly and provide the direct
checkout invocation. For platform-specific instructions, indicate which commands were
actually exercised.

## CLI documentation quality review

- [ ] The opening sentence describes a concrete result and intended reader.
- [ ] The first command works from a stated directory and uses non-sensitive input.
- [ ] Input, stdout/stderr, created files and exit statuses are described accurately.
- [ ] The tool's `--help` agrees with the README and includes meaningful flags.
- [ ] Error examples do not leak paths, secrets, tokens or internal stack traces.
- [ ] Install/update/uninstall instructions correspond to available artifacts.
- [ ] Destructive and network behavior is called out *before* the command.
- [ ] Terminal screenshots have equivalent text; color is not the sole status cue.
- [ ] Quickstart tests are run in CI, and unsupported systems are labeled—not inferred.
- [ ] LICENSE, contribution route and maintenance limitations are findable.

The kit's [working README](../examples/cli-starter/README.md) and
[test suite](../tests/test_cli_starter.py) can be adapted without copying brand assets.
The general [repository checklist](../checklists/repository.md) complements this
CLI-specific review.

## Sources and boundaries

Reviewed **2026-10-08**:

- [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) recommends reader-first onboarding and portable relative links.
- [Python Packaging User Guide: Creating and packaging command-line tools](https://packaging.python.org/en/latest/guides/creating-command-line-tools/) distinguishes a source tree, console scripts and installable distributions.
- [Python Packaging User Guide: Installing standalone command-line tools](https://packaging.python.org/en/latest/guides/installing-stand-alone-command-line-tools/) explains isolated `pipx` installs and environment considerations.
- [GitHub CLI](https://github.com/cli/cli) provides a real, mature example separating a short promise, installation options, manual and contributing path. Its particular release channels are **not** assumed for other projects.

This is an original documentation pattern plus a local executable example, not a
cross-platform installer test, software supply-chain audit or endorsement of a CLI
framework. No external commands were executed to create the example.
