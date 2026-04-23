"""Unit tests for helpers/init_inquiry.py (BQ-010).

Stdlib-only. Subprocess-based: the helper is a CLI bootstrap and the subprocess
contract is what callers actually use. Each test gets its own TemporaryDirectory.

Integration-style: tests assume memex is installed at ``~/Development/memex``.
Tests that need it call ``_require_memex()`` in setUp, which ``skipTest``s with
a clear message if the harness is missing.

Run from repo root: ``python3 -m unittest discover tests/``
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "helpers" / "init_inquiry.py"
ADDENDUM_PATH = REPO_ROOT / "schema.inquiry.example.md"
SKILLS_ROOT = REPO_ROOT / "skills"

# Idempotency marker — matches ADDENDUM_MARKER in init_inquiry.py. Note the
# em-dash (U+2014), not a hyphen. (BQ-008's report said en-dash; source uses em-dash.)
ADDENDUM_MARKER = "<!-- Inquiry domain addendum — appends to memex/schema.example.md -->"

# Default memex location (the helper's own default expands to this).
DEFAULT_MEMEX_PATH = Path(os.path.expanduser("~/Development/memex"))

# A sentinel string from memex's base schema.example.md — used to confirm
# the file actually got seeded from memex rather than being empty or
# containing only the inquiry addendum. (em-dash, U+2014)
MEMEX_BASE_SENTINEL = "# SCHEMA.md — Starter Template"


def _run_init_inquiry(target, memex_path=None, force=False):
    """Invoke helpers/init_inquiry.py as a subprocess and return CompletedProcess."""
    cmd = [sys.executable, str(SCRIPT_PATH), "--path", str(target)]
    if memex_path is not None:
        cmd.extend(["--memex-path", str(memex_path)])
    if force:
        cmd.append("--force")
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))


def _require_memex(test_case):
    """Skip the calling test if the memex harness isn't installed."""
    init_wiki = DEFAULT_MEMEX_PATH / "helpers" / "init_wiki.py"
    if not init_wiki.is_file():
        test_case.skipTest(
            f"memex not installed at {DEFAULT_MEMEX_PATH} "
            f"(expected helpers/init_wiki.py); "
            f"integration tests need a real memex install."
        )


class InitInquiryHappyPathTests(unittest.TestCase):
    """Fresh-target initialization: memex base seeded + inquiry layer applied."""

    def setUp(self):
        _require_memex(self)

    def test_fresh_target_exits_zero(self):
        """Running against a fresh temp dir exits 0."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "inquiry_instance"
            result = _run_init_inquiry(target)
            self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")

    def test_fresh_target_schema_has_base_plus_addendum(self):
        """SCHEMA.md contains both the memex base content and the addendum marker,
        and the marker appears exactly once."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "inquiry_instance"
            result = _run_init_inquiry(target)
            self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")

            schema_dst = target / "SCHEMA.md"
            self.assertTrue(schema_dst.is_file(), "SCHEMA.md not created at target")
            content = schema_dst.read_text(encoding="utf-8")
            self.assertIn(
                MEMEX_BASE_SENTINEL,
                content,
                "SCHEMA.md missing memex base sentinel — memex init_wiki may not have run",
            )
            self.assertIn(
                ADDENDUM_MARKER,
                content,
                "SCHEMA.md missing inquiry addendum marker — addendum step did not apply",
            )
            self.assertEqual(
                content.count(ADDENDUM_MARKER),
                1,
                "addendum marker should appear exactly once after fresh init",
            )

    def test_fresh_target_uses_questions_pages_dir(self):
        """wiki/questions/ exists and wiki/pages/ does not (inquiry uses --pages-dir questions)."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "inquiry_instance"
            result = _run_init_inquiry(target)
            self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")
            self.assertTrue(
                (target / "wiki" / "questions").is_dir(),
                "wiki/questions/ not created",
            )
            self.assertFalse(
                (target / "wiki" / "pages").exists(),
                "wiki/pages/ should not exist when pages-dir=questions",
            )

    def test_fresh_target_symlinks_resolve_correctly(self):
        """Both inquiry skills are symlinked into .claude/skills/ and resolve to repo sources."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "inquiry_instance"
            result = _run_init_inquiry(target)
            self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")

            for skill in ("inquiry-elicit", "inquiry-gap"):
                link = target / ".claude" / "skills" / skill
                self.assertTrue(
                    link.is_symlink(),
                    f".claude/skills/{skill} is not a symlink",
                )
                expected = (SKILLS_ROOT / skill).resolve()
                self.assertEqual(
                    link.resolve(),
                    expected,
                    f"{skill} symlink does not resolve to {expected}",
                )


class InitInquiryIdempotencyTests(unittest.TestCase):
    """Plain re-run without --force is safe (short-circuits; does not duplicate addendum)."""

    def setUp(self):
        _require_memex(self)

    def test_plain_rerun_is_safe(self):
        """Second run (no --force) exits 0, signals short-circuit, keeps marker count at 1,
        and leaves skill symlinks intact."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "inquiry_instance"
            first = _run_init_inquiry(target)
            self.assertEqual(first.returncode, 0, msg=f"stderr: {first.stderr}")

            second = _run_init_inquiry(target)
            self.assertEqual(
                second.returncode, 0,
                msg=f"expected exit 0 on safe re-run; stderr: {second.stderr}",
            )

            # Short-circuit signal.
            combined = second.stdout + second.stderr
            self.assertTrue(
                "already initialized" in combined or "sub-call skipped" in combined,
                f"expected short-circuit signal; stdout={second.stdout!r} stderr={second.stderr!r}",
            )

            # Addendum not duplicated.
            content = (target / "SCHEMA.md").read_text(encoding="utf-8")
            self.assertEqual(
                content.count(ADDENDUM_MARKER), 1,
                "addendum marker count should stay at 1 after plain re-run",
            )

            # Symlinks preserved.
            for skill in ("inquiry-elicit", "inquiry-gap"):
                link = target / ".claude" / "skills" / skill
                self.assertTrue(link.is_symlink(), f"{skill} symlink missing")
                self.assertEqual(
                    link.resolve(), (SKILLS_ROOT / skill).resolve(),
                    f"{skill} symlink no longer resolves to repo source",
                )


class InitInquiryForceReseedTests(unittest.TestCase):
    """--force reseeds SCHEMA.md from memex base, then re-applies addendum ONCE."""

    def setUp(self):
        _require_memex(self)

    def test_force_reseed_restores_base_and_applies_addendum_once(self):
        """--force wipes garbage, restores memex base, and keeps marker count at 1
        (NOT 2 — init_wiki reseeds SCHEMA.md to bare memex base before re-append)."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "inquiry_instance"
            first = _run_init_inquiry(target)
            self.assertEqual(first.returncode, 0, msg=f"stderr: {first.stderr}")

            schema_dst = target / "SCHEMA.md"
            garbage = "### GARBAGE_LINE_DO_NOT_KEEP_ME ###"
            with schema_dst.open("a", encoding="utf-8") as fh:
                fh.write(f"\n{garbage}\n")
            self.assertIn(garbage, schema_dst.read_text(encoding="utf-8"))

            second = _run_init_inquiry(target, force=True)
            self.assertEqual(
                second.returncode, 0,
                msg=f"expected exit 0 on --force; stderr: {second.stderr}",
            )

            content = schema_dst.read_text(encoding="utf-8")
            self.assertNotIn(garbage, content, "--force did not reseed SCHEMA.md")
            self.assertIn(
                MEMEX_BASE_SENTINEL, content,
                "--force re-run left SCHEMA.md missing memex base content",
            )
            self.assertEqual(
                content.count(ADDENDUM_MARKER), 1,
                "after --force: marker count must be exactly 1, not 2",
            )

    def test_force_reseed_symlinks_still_correct(self):
        """--force re-run preserves the skill symlinks."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "inquiry_instance"
            first = _run_init_inquiry(target)
            self.assertEqual(first.returncode, 0, msg=f"stderr: {first.stderr}")

            second = _run_init_inquiry(target, force=True)
            self.assertEqual(second.returncode, 0, msg=f"stderr: {second.stderr}")

            for skill in ("inquiry-elicit", "inquiry-gap"):
                link = target / ".claude" / "skills" / skill
                self.assertTrue(link.is_symlink(), f"{skill} symlink missing after --force")
                self.assertEqual(
                    link.resolve(), (SKILLS_ROOT / skill).resolve(),
                    f"{skill} symlink no longer resolves to repo source",
                )


class InitInquiryUserContentPreservationTests(unittest.TestCase):
    """--force reseeds SCHEMA.md but leaves user-authored content alone."""

    def setUp(self):
        _require_memex(self)

    def test_user_questions_and_raw_preserved_on_force(self):
        """User-authored files under wiki/questions/ and raw/ survive --force."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "inquiry_instance"
            first = _run_init_inquiry(target)
            self.assertEqual(first.returncode, 0, msg=f"stderr: {first.stderr}")

            question = target / "wiki" / "questions" / "foo.md"
            question_content = "# Foo?\n\nUser-authored question.\n"
            question.write_text(question_content, encoding="utf-8")

            raw = target / "raw" / "sample.md"
            raw_content = "raw source snapshot\n"
            raw.write_text(raw_content, encoding="utf-8")

            second = _run_init_inquiry(target, force=True)
            self.assertEqual(
                second.returncode,
                0,
                msg=f"expected exit 0; stderr: {second.stderr}",
            )

            self.assertEqual(
                question.read_text(encoding="utf-8"),
                question_content,
                "user-authored wiki/questions/foo.md was clobbered by --force",
            )
            self.assertEqual(
                raw.read_text(encoding="utf-8"),
                raw_content,
                "user-authored raw/sample.md was clobbered by --force",
            )

            # Symlinks still correct too.
            for skill in ("inquiry-elicit", "inquiry-gap"):
                link = target / ".claude" / "skills" / skill
                self.assertTrue(link.is_symlink(), f"{skill} symlink missing")
                self.assertEqual(
                    link.resolve(),
                    (SKILLS_ROOT / skill).resolve(),
                    f"{skill} symlink no longer resolves to repo source",
                )


class InitInquiryPreconditionFailureTests(unittest.TestCase):
    """Precondition failures: memex harness missing at --memex-path."""

    def test_missing_memex_exits_one_with_clear_message(self):
        """--memex-path pointing at a nonexistent path exits 1 with 'memex harness not found'."""
        with tempfile.TemporaryDirectory() as td:
            # Build a path that definitely does not exist. Use the temp dir
            # and append a subdir we know wasn't created.
            bogus_memex = Path(td) / "nonexistent_memex_install"
            self.assertFalse(bogus_memex.exists(), "test precondition: path should not exist")

            target = Path(td) / "inquiry_instance"
            result = _run_init_inquiry(target, memex_path=bogus_memex)

            self.assertEqual(
                result.returncode,
                1,
                msg=f"expected exit 1; got {result.returncode}; stderr: {result.stderr}",
            )
            self.assertIn(
                "memex harness not found",
                result.stderr,
                f"expected 'memex harness not found' in stderr; got: {result.stderr!r}",
            )
            self.assertFalse(
                target.exists(),
                "target directory was created despite precondition failure (no half-init state allowed)",
            )


class InitInquirySymlinkConflictTests(unittest.TestCase):
    """Pre-existing symlink pointing elsewhere must cause exit 1, not silent overwrite."""

    def setUp(self):
        _require_memex(self)

    def test_conflicting_symlink_exits_one(self):
        """A symlink at .claude/skills/inquiry-elicit pointing at /tmp triggers exit 1."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "inquiry_instance"
            first = _run_init_inquiry(target)
            self.assertEqual(first.returncode, 0, msg=f"stderr: {first.stderr}")

            # Replace the correct symlink with one pointing elsewhere.
            link = target / ".claude" / "skills" / "inquiry-elicit"
            self.assertTrue(link.is_symlink(), "precondition: original symlink should exist")
            link.unlink()
            # Point at /tmp — a real dir that's clearly not the expected target.
            os.symlink("/tmp", link)
            self.assertTrue(link.is_symlink())
            self.assertEqual(link.resolve(), Path("/tmp").resolve())

            result = _run_init_inquiry(target)

            self.assertEqual(
                result.returncode,
                1,
                msg=f"expected exit 1 on conflict; got {result.returncode}; stderr: {result.stderr}",
            )
            self.assertIn(
                "conflicting",
                result.stderr,
                f"expected 'conflicting' substring in stderr; got: {result.stderr!r}",
            )

    def test_conflicting_symlink_shows_partial_state_summary(self):
        """Stderr should surface the partial-state report (init_wiki ok, addendum ok, skill FAILED)."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "inquiry_instance"
            first = _run_init_inquiry(target)
            self.assertEqual(first.returncode, 0, msg=f"stderr: {first.stderr}")

            link = target / ".claude" / "skills" / "inquiry-elicit"
            link.unlink()
            os.symlink("/tmp", link)

            result = _run_init_inquiry(target)
            self.assertEqual(result.returncode, 1, msg=f"stderr: {result.stderr}")

            self.assertIn(
                "Partial init summary",
                result.stderr,
                f"expected partial-state summary in stderr; got: {result.stderr!r}",
            )
            self.assertIn(
                "FAILED",
                result.stderr,
                f"expected 'FAILED' marker for the broken skill step; got: {result.stderr!r}",
            )


class InitInquiryArgparseTests(unittest.TestCase):
    """argparse wiring: required args are enforced."""

    def test_missing_path_arg_exits_nonzero(self):
        """Omitting --path causes argparse to exit non-zero with a usage message."""
        # No need for memex to exist — argparse fails before any precondition check.
        cmd = [sys.executable, str(SCRIPT_PATH)]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
        self.assertNotEqual(
            result.returncode,
            0,
            msg=f"expected non-zero exit; stderr: {result.stderr}",
        )
        # argparse writes usage/error to stderr on missing required args.
        self.assertIn("--path", result.stderr)


if __name__ == "__main__":
    unittest.main()
