"""Static contracts for the existing PR Autofix caller's bounded Sentry access."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/autofix.yml").read_text()
KODY_WORKFLOW = (ROOT / ".github/workflows/kody-fleet-autofix.yml").read_text()
SHARED_GROUP_PREFIX = "group: pr-autofix-${{ github.repository }}-"
AUTOFIX_GROUP_SUFFIX = "${{ github.event.issue.number || github.event.pull_request.number }}"
KODY_GROUP_SUFFIX = "${{ github.event.check_run.pull_requests[0].number || github.event.check_run.id }}"
PIN_FIXTURE = "a4c48f013a2108be517ee933dccb1b37e9403920"  # public commit SHA, not a secret
EXPECTED = {"kody-ai[bot]", "chatgpt-codex-connector[bot]", "cursor[bot]", "claude[bot]", "sentry", "sentry[bot]"}

class AutofixContractTests(unittest.TestCase):
    def test_verified_reusable_pin(self):
        pins = re.findall(r"^    uses: Simple-With-Us/AI-Fleet-Coordinator/\.github/workflows/pr-autofix-reusable\.yml@([0-9a-f]{40})$", WORKFLOW, re.M)
        self.assertEqual(pins, [PIN_FIXTURE])

    def test_only_existing_actors_and_exact_sentry_aliases(self):
        matches = re.findall(r'^      allowed_bots: "([^"]+)"$', WORKFLOW, re.M)
        self.assertEqual(len(matches), 1)
        actors = matches[0].split(",")
        self.assertEqual(set(actors), EXPECTED)
        self.assertEqual(len(actors), len(EXPECTED))
        for unrelated in ("*", "sentry-spoof", "sentry[bot]-spoof", "someone"):
            self.assertNotIn(unrelated, actors)

    def test_human_events_still_require_bot_type(self):
        self.assertIn('contains(fromJSON(\'["bot", "Bot"]\')', WORKFLOW)
        self.assertNotIn("pull_request_target:", WORKFLOW)

    def test_kody_caller_shares_the_pr_autofix_concurrency_group(self):
        expected = SHARED_GROUP_PREFIX + KODY_GROUP_SUFFIX
        self.assertIn(expected, KODY_WORKFLOW)
        self.assertIn("cancel-in-progress: false", KODY_WORKFLOW)
        # Pin the caller side of the shared key too: the PR-number suffix is
        # what makes both groups resolve to the same pull request.
        self.assertIn(SHARED_GROUP_PREFIX + AUTOFIX_GROUP_SUFFIX, WORKFLOW)
        kody_groups = [line.strip() for line in KODY_WORKFLOW.splitlines() if line.strip().startswith("group:")]
        self.assertTrue(kody_groups, "kody-fleet-autofix.yml must declare a concurrency group")
        self.assertEqual(kody_groups[0], expected)
        # The shared group must sit under the job-level concurrency block: a
        # top-level (two-space) group would serialize the whole workflow.
        job_level_groups = [line for line in KODY_WORKFLOW.splitlines() if line.startswith("      group:")]
        self.assertEqual(job_level_groups, ["      " + expected])
        for kody_group in kody_groups:
            self.assertNotIn("kody-caller-", kody_group)
            self.assertNotIn("github.repository_id", kody_group)
        self.assertNotIn("kody-caller-", KODY_WORKFLOW)

    def test_existing_serialization_and_permissions(self):
        self.assertIn("cancel-in-progress: false", WORKFLOW)
        self.assertIn("group: pr-autofix-", WORKFLOW)
        self.assertIn("permissions: {}", WORKFLOW)
        self.assertIn("      contents: write\n      pull-requests: read\n      issues: write\n      actions: read", WORKFLOW)

if __name__ == "__main__":
    unittest.main()