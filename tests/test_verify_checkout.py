"""Contract and negative-path tests for the optional local CI command runner."""

import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("verify_checkout", ROOT / "tools" / "verify_checkout.py")
verify_checkout = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify_checkout)


class VerifyCheckoutTests(unittest.TestCase):
    def test_inventory_matches_python_steps_in_quality_catalog_job(self):
        workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
        catalog = workflow.split("\n  catalog:\n", 1)[1].split("\n  lint:\n", 1)[0]
        commands = re.findall(r"^\s+run: python (.+)$", catalog, flags=re.MULTILINE)
        commands = [tuple(text.split()) for text in commands if text != "--version"]
        self.assertEqual(commands, [command for _, command in verify_checkout.CHECKS])
        self.assertEqual(len(commands), len(set(commands)))

    @mock.patch.object(verify_checkout.subprocess, "run")
    def test_list_is_read_only(self, run):
        self.assertEqual(verify_checkout.main(["--list"]), 0)
        run.assert_not_called()

    @mock.patch.object(verify_checkout.subprocess, "run")
    def test_fails_fast_on_first_failed_step(self, run):
        run.side_effect = [subprocess.CompletedProcess([], 0), subprocess.CompletedProcess([], 7)]
        self.assertEqual(verify_checkout.main([]), 1)
        self.assertEqual(run.call_count, 2)
        for args, kwargs in run.call_args_list:
            self.assertEqual(args[0][0], sys.executable)
            self.assertEqual(kwargs["cwd"], ROOT)
            self.assertFalse(kwargs["check"])

    @mock.patch.object(verify_checkout.subprocess, "run")
    def test_keep_going_runs_all_and_still_fails(self, run):
        run.side_effect = [
            subprocess.CompletedProcess([], 3 if i in (0, 5) else 0)
            for i in range(len(verify_checkout.CHECKS))
        ]
        self.assertEqual(verify_checkout.main(["--keep-going"]), 1)
        self.assertEqual(run.call_count, len(verify_checkout.CHECKS))

    @mock.patch.object(verify_checkout.subprocess, "run")
    def test_launch_error_does_not_become_a_pass(self, run):
        run.side_effect = OSError("missing interpreter")
        self.assertEqual(verify_checkout.main([]), 1)
        self.assertEqual(run.call_count, 1)

    @mock.patch.object(verify_checkout.subprocess, "run")
    def test_all_success_is_reported_only_after_every_step(self, run):
        run.return_value = subprocess.CompletedProcess([], 0)
        self.assertEqual(verify_checkout.main([]), 0)
        self.assertEqual(run.call_count, len(verify_checkout.CHECKS))


if __name__ == "__main__":
    unittest.main()
