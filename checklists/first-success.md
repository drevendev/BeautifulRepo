# First-success check: from a fresh checkout to a real result

Use this checklist for a README change, executable example or small release-note
update. It checks the reader's route, not a universal quality score.

- [ ] **State one outcome.** Name who it helps, what they do and what they receive.
  Separate a working feature from a proposal or unreleased package.
- [ ] **Start from the documented directory.** Run the exact command in a fresh
  checkout with the stated runtime. Do not rely on files left over from another run.
- [ ] **Observe the result.** Record output or a genuine image of the running code.
  Keep a useful text equivalent. A static rendering is not a browser end-to-end test.
- [ ] **Exercise a failure.** Try invalid input, a missing fixture or an unsupported
  option. Errors should be understandable and should not echo arbitrary input data.
- [ ] **Check the boundary.** Identify files read or written, outbound calls, listener
  addresses, persistence, logs and any required credentials. A loopback demo is not
  production-ready merely because it does not need a login.
- [ ] **Leave a verification route.** Link the guide, sample, template and limitations.
  Run the appropriate tests and distinguish local results from provider CI. Do not
  claim checks that were skipped or blocked.

For example, [Pocket Board](../examples/application-starter/README.md) has a useful
first-success claim: choose Open and see three tasks totaling 12 fictional points.
Its server and JSON fixture demonstrate that interaction, not durability or real
workload performance. [Research/data](../examples/research-data-starter/README.md)
instead exposes a reproducible aggregate (6 fabricated rows, total 60) and fixture digest.

See the broader [repository checklist](repository.md) and the
[maintenance workflow](../guides/maintenance-workflow.md). The checklist is an aid to
judgement, not accessibility, security or scientific certification.
