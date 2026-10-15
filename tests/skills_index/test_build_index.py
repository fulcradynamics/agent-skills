"""Offline checks for scripts/build-skills-index.py, the discovery index the
skills-index workflow publishes at /.well-known/agent-skills/index.json."""

import hashlib
import importlib.util
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("build_skills_index", ROOT / "scripts/build-skills-index.py")
build_skills_index = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_skills_index)


def git(*args: str) -> bytes:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True).stdout


def front_matter(description_line: str) -> bytes:
    return f"---\nname: x\n{description_line}\n---\n\n# X\n".encode()


class TestIndexOfHead(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.commit = git("rev-parse", "HEAD").decode().strip()
        cls.index = build_skills_index.build(cls.commit)
        cls.by_name = {s["name"]: s for s in cls.index["skills"]}

    def test_every_entry_pins_its_skill_md_to_the_commit(self):
        for entry in self.index["skills"]:
            path = f"skills/{entry['name']}/SKILL.md"
            self.assertEqual(
                entry["url"],
                f"https://raw.githubusercontent.com/fulcradynamics/agent-skills/{self.commit}/{path}",
            )
            committed = git("show", f"{self.commit}:{path}")
            self.assertEqual(entry["digest"], "sha256:" + hashlib.sha256(committed).hexdigest())
            self.assertEqual(entry["type"], "skill-md")
            self.assertTrue(entry["description"])

    def test_lists_every_skill_except_rename_pointers(self):
        listed = set(self.by_name)
        for name in build_skills_index.skill_names(self.commit):
            skill_md = git("show", f"{self.commit}:skills/{name}/SKILL.md")
            pointer = build_skills_index.description(skill_md, name).startswith(
                build_skills_index.POINTER_PREFIX
            )
            self.assertEqual(name in listed, not pointer, name)

    def test_known_pointers_are_left_out_and_deprecated_skills_kept(self):
        for pointer in ("connect-agents-with-anyone", "fulcra-agent-teams", "fulcra-onboarding"):
            if pointer in build_skills_index.skill_names(self.commit):
                self.assertNotIn(pointer, self.by_name)
        if "fulcra-mesh" in build_skills_index.skill_names(self.commit):
            self.assertIn("fulcra-mesh", self.by_name)

    def test_index_is_sorted_and_rendered_stably(self):
        names = [s["name"] for s in self.index["skills"]]
        self.assertEqual(names, sorted(names))
        text = build_skills_index.render(self.index)
        self.assertTrue(text.endswith("}\n"))
        self.assertEqual(json.loads(text), self.index)
        self.assertEqual(self.index["$schema"], build_skills_index.SCHEMA)


class TestDescription(unittest.TestCase):
    def test_reads_the_one_line_forms(self):
        cases = {
            'description: "Say \\"hi\\" — then go"': 'Say "hi" — then go',
            "description: 'It''s here'": "It's here",
            "description: Plain text, with: colons": "Plain text, with: colons",
        }
        for line, expected in cases.items():
            self.assertEqual(build_skills_index.description(front_matter(line), "x"), expected, line)

    def test_refuses_what_it_cannot_read(self):
        for skill_md in (
            front_matter("description: >\n  folded"),
            front_matter("description: |\n  literal"),
            front_matter("description:"),
            front_matter("name_only: true"),
            b"# no front matter\n",
        ):
            with self.assertRaises(ValueError, msg=skill_md):
                build_skills_index.description(skill_md, "x")


class TestSkillNames(unittest.TestCase):
    def test_only_folders_with_a_skill_md(self):
        commit = git("rev-parse", "HEAD").decode().strip()
        names = build_skills_index.skill_names(commit)
        self.assertTrue(names)
        for name in names:
            self.assertTrue(re.fullmatch(r"[^/]+", name))
            git("cat-file", "-e", f"{commit}:skills/{name}/SKILL.md")


if __name__ == "__main__":
    unittest.main()
