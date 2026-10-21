"""Static contracts for the existing PR Autofix caller's bounded Sentry access."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/autofix.yml").read_text()
PIN_FIXTURE = "c97a2dae96762eb9ffc122c753f0dfb0a7840650"  # public commit SHA, not a secret
EXPECTED = {
    "kody-ai[bot]", "chatgpt-codex-connector[bot]", "cursor[bot]", "claude[bot]", "sentry", "sentry[bot]",
    "swu-ag[bot]", "swu-bf-builder[bot]", "swu-bf-compiler[bot]", "swu-bf-designer[bot]",
    "swu-bf-director[bot]", "swu-bf-fixer[bot]", "swu-bf-housekeeper[bot]", "swu-bf-monitor[bot]", "swu-bf-oracle[bot]",
    "swu-bf-plumber[bot]", "swu-bf-publisher[bot]", "swu-claude[bot]", "swu-clutch[bot]", "swu-codex[bot]", "swu-cursor[bot]",
    "swu-cursor-cloud[bot]", "swu-fx[bot]", "swu-gb-compiler[bot]",
    "swu-gb-designer[bot]", "swu-gb-director[bot]", "swu-gb-engineer[bot]", "swu-gb-fixer[bot]",
    "swu-gb-housekeeper[bot]", "swu-gb-monitor[bot]", "swu-gb-oracle[bot]", "swu-gb-plumber[bot]",
    "swu-gb-publisher[bot]", "swu-grok-build[bot]", "swu-jet[bot]",
    "swu-minimax[bot]", "swu-opencode[bot]", "swu-operator[bot]", "swu-rob[bot]", "swu-wise[bot]",
}

STATUS_ONLY_BOTS = {
    "swu-bf-deployer[bot]", "swu-gb-deployer[bot]", "swu-gb-trader[bot]",
    "swu-grok-web[bot]", "swu-echo[bot]", "swu-mc[bot]",
}

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

    def test_status_only_bots_cannot_steer_the_agent(self):
        matches = re.findall(r'^      allowed_bots: "([^"]+)"$', WORKFLOW, re.M)
        self.assertEqual(set(matches[0].split(",")) & STATUS_ONLY_BOTS, set())

    def test_human_events_still_require_bot_type(self):
        self.assertIn('contains(fromJSON(\'["bot", "Bot"]\')', WORKFLOW)
        self.assertNotIn("pull_request_target:", WORKFLOW)

    def test_issue_comments_require_an_action_request(self):
        self.assertIn("github.event_name != 'issue_comment'", WORKFLOW)
        self.assertIn("contains(github.event.comment.body, '/autofix')", WORKFLOW)

    def test_trusted_policy_pins_model_and_budget(self):
        policy = (ROOT / ".github/pr-autofix-trusted.yml").read_text()
        self.assertIn("model: MiniMax-M3.1-Flash\n", policy)
        self.assertIn("max_turns: 60\n", policy)
        self.assertIn("max_iterations: 5\n", policy)

    def test_existing_serialization_and_permissions(self):
        self.assertIn("cancel-in-progress: false", WORKFLOW)
        self.assertIn("group: pr-autofix-", WORKFLOW)
        self.assertIn("permissions: {}", WORKFLOW)
        self.assertIn("      contents: write\n      pull-requests: read\n      issues: write\n      actions: read", WORKFLOW)

if __name__ == "__main__":
    unittest.main()