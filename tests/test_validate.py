"""Mutation tests: each one breaks a temporary copy of the project on purpose
and checks that scripts/validate.py (or build_template.py) catches it.

    python -m unittest discover -s tests -v

Standard library only. The template checks need PyYAML; without it those
tests are skipped, as validate.py itself skips them.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COPY = ("agents", "documents", "scripts", "template", "festcommand.template.yaml")

try:
    import yaml  # noqa: F401
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


class Project:
    """A throwaway copy of the project that a test may break."""

    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        for name in COPY:
            src = REPO / name
            if src.is_dir():
                shutil.copytree(src, self.root / name, ignore=shutil.ignore_patterns("__pycache__"))
            else:
                shutil.copy2(src, self.root / name)

    def close(self) -> None:
        self._tmp.cleanup()

    def run(self, script: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(self.root / "scripts" / script), *args],
                              capture_output=True, text=True, encoding="utf-8", env=ENV)

    def edit(self, rel: str, old: str, new: str) -> None:
        path = self.root / rel
        text = path.read_text(encoding="utf-8")
        assert old in text, f"{old!r} not in {rel}"
        path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")

    def edit_json(self, rel: str, change) -> None:
        path = self.root / rel
        doc = json.loads(path.read_text(encoding="utf-8"))
        change(doc)
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    def rebuild(self) -> None:
        built = self.run("build_template.py")
        assert built.returncode == 0, built.stdout + built.stderr

    def validate(self) -> subprocess.CompletedProcess:
        return self.run("validate.py")


def match(doc: dict, match_id: str) -> dict:
    for t in doc["tournaments"].values():
        for m in t.get("matches", []):
            if m.get("match_id") == match_id:
                return m
    raise KeyError(match_id)


class ValidatorCatches(unittest.TestCase):
    def setUp(self) -> None:
        self.p = Project()
        self.addCleanup(self.p.close)

    def assertFlags(self, result: subprocess.CompletedProcess, *needles: str) -> None:
        self.assertNotEqual(result.returncode, 0, "validator passed a broken project:\n" + result.stdout)
        for needle in needles:
            self.assertIn(needle, result.stdout)

    # ── baseline ──
    def test_clean_project_passes(self):
        result = self.p.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("checks passed", result.stdout)

    def test_runs_without_a_utf8_environment(self):
        # Windows consoles and pipes default to cp1252; the scripts print emoji.
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}
        for script in ("validate.py", "build_template.py"):
            args = [sys.executable, str(self.p.root / "scripts" / script)] + (["--check"] if script.startswith("build") else [])
            result = subprocess.run(args, capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, f"{script}: " + result.stderr.decode("utf-8", "replace")[-1500:])

    # ── documents ──
    def test_schedule_and_bracket_disagree_on_stage(self):
        self.p.edit_json("documents/bracket_state.json", lambda d: match(d, "MATCH-07").update(stage="Arena Beta"))
        self.assertFlags(self.p.validate(), "MATCH-07")

    def test_budget_arithmetic(self):
        self.p.edit_json("documents/sponsor_ledger.json", lambda d: d.update(total_budget=d["total_budget"] + 1))
        self.assertFlags(self.p.validate(), "total_budget")

    def test_illegal_valorant_map_score(self):
        broken = {}

        def break_score(d):
            m = next(m for m in d["tournaments"]["valorant"]["matches"]
                     if m.get("status") == "completed" and (m.get("score") or {}).get("maps"))
            m["score"]["maps"][0].update(score_a=13, score_b=12)  # 13-12 can't end a map
            broken["id"] = m["match_id"]
        self.p.edit_json("documents/bracket_state.json", break_score)
        self.assertFlags(self.p.validate(), broken["id"])

    def test_day_heading_date_drives_the_schedule(self):
        self.p.edit("documents/schedule_and_rules.md", "## Day 1 Schedule — December 14", "## Day 1 Schedule — December 13")
        self.assertFlags(self.p.validate(), "schedule says 2026-12-13")

    def test_a_fest_without_a_game_gets_findings_not_a_crash(self):
        self.p.edit_json("documents/bracket_state.json", lambda d: d["tournaments"].pop("bgmi"))
        result = self.p.validate()
        self.assertNotIn("Traceback", result.stderr)
        self.assertFlags(result, "bracket_state.json has no such match")

    def test_unparseable_prize_cell_is_a_finding_not_a_crash(self):
        self.p.edit("documents/schedule_and_rules.md", "| Valorant 5v5 |", "| Valorant 5v5 | — |", )
        result = self.p.validate()
        self.assertNotIn("Traceback", result.stderr)
        self.assertFlags(result, "prizes for Valorant 5v5")

    def test_zero_allocation_is_a_finding_not_a_crash(self):
        self.p.edit_json("documents/sponsor_ledger.json",
                         lambda d: d["expenses"]["categories"]["catering"].update(allocated=0))
        result = self.p.validate()
        self.assertNotIn("Traceback", result.stderr)
        self.assertFlags(result, "spending but no allocation")

    def test_last_day_table_may_end_the_file(self):
        def move_day2_to_end(text):
            start = text.index("## Day 2 Schedule")
            end = text.index("\n---", start)
            return text[:start] + text[end + 4:] + "\n" + text[start:end].rstrip() + "\n"
        path = self.p.root / "documents" / "schedule_and_rules.md"
        path.write_text(move_day2_to_end(path.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
        result = self.p.validate()
        self.assertNotIn("not in the published schedule", result.stdout)

    def test_rulebook_section_cited_by_an_agent_is_renamed(self):
        self.p.edit("documents/schedule_and_rules.md", "### Tournament Conduct", "### Match Conduct")
        self.assertFlags(self.p.validate(), '"Tournament Conduct"')

    def test_pending_vendor_payment_missing_from_the_queue(self):
        self.p.edit_json("documents/sponsor_ledger.json", lambda d: d["pending_approvals"].clear())
        self.assertFlags(self.p.validate(), "VENDOR-03 awaits approval")

    def test_ledger_loses_its_approval_queue(self):
        self.p.edit_json("documents/sponsor_ledger.json", lambda d: d.pop("pending_approvals"))
        self.assertFlags(self.p.validate(), "pending_approvals")

    # ── template ──
    def test_stale_template(self):
        self.p.edit("agents/concierge/SKILL.md", "## Tone", "## Tone (edited)")
        self.assertFlags(self.p.run("build_template.py", "--check"))
        self.assertFlags(self.p.validate(), "stale")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_placeholder_inside_embedded_document(self):
        self.p.edit_json("documents/bracket_state.json", lambda d: d.update(event=d["event"] + " {concierge.name}"))
        self.p.rebuild()
        self.assertFlags(self.p.validate(), "would substitute")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_room_key_switch_does_not_read(self):
        self.p.edit("template/festcommand.template.src.yaml",
                    "    channel_type: channel_private\n", "    channel_type: channel_private\n    people: [x]\n")
        self.p.rebuild()
        self.assertFlags(self.p.validate(), "people")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_malformed_condition(self):
        self.p.edit("template/festcommand.template.src.yaml", '- if: "{bridge}"', '- if: "{bridge} = slack"')
        self.p.rebuild()
        self.assertFlags(self.p.validate(), "is not a Switch condition")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_kickoff_creates_a_provisioned_name(self):
        self.p.edit("template/festcommand.template.src.yaml",
                    "      - name: sponsor_ledger.json\n", "      - name: ledger_live.json\n")
        self.p.rebuild()
        self.assertFlags(self.p.validate(), "already provisions")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_display_name_too_long_for_switch(self):
        self.p.edit("template/festcommand.template.src.yaml", 'pattern: ".{1,40}"', 'pattern: ".{1,60}"')
        self.p.rebuild()
        self.assertFlags(self.p.validate(), "Switch max 64")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_instructions_name_a_switch_operation_that_does_not_exist(self):
        self.p.edit("agents/concierge/SKILL.md", "`connect_to_room(<that id>)`", "`connect_room_by_id(<that id>)`")
        self.p.rebuild()
        self.assertFlags(self.p.validate(), "connect_room_by_id")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_agent_mentions_an_agent_it_shares_no_room_with(self):
        self.p.edit("agents/bracket-marshal/SKILL.md", "## Boundaries", "## Boundaries\n\nAsk @{concierge.name}.\n", )
        self.p.edit("template/festcommand.template.src.yaml",
                    "agents: [bracket_marshal, concierge, sponsor_tracker]", "agents: [bracket_marshal, sponsor_tracker]")
        self.p.rebuild()
        self.assertFlags(self.p.validate(), "share no room")


class Rehearsal(unittest.TestCase):
    def test_pauses_still_work(self):
        # --fast skips time.sleep, so a shadowed `time` would only break the live demo.
        sys.path.insert(0, str(REPO / "scripts"))
        self.addCleanup(sys.path.remove, str(REPO / "scripts"))
        import rehearse
        self.assertTrue(callable(getattr(rehearse.time, "sleep", None)))

    def test_runs_and_leaves_documents_untouched(self):
        p = Project()
        self.addCleanup(p.close)
        def digest():
            return {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in (p.root / "documents").iterdir()}
        before = digest()
        result = p.run("rehearse.py", "--fast", "--no-color")
        self.assertEqual(result.returncode, 0, result.stdout[-2000:] + result.stderr)
        self.assertEqual(before, digest())


if __name__ == "__main__":
    unittest.main()
