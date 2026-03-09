#!/usr/bin/env python3
"""Render the Copier template and verify the supported workflows end-to-end."""

from __future__ import annotations

import json
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FRESH_DATA = {
    "workspace_name": "smoke-workspace",
    "package_name": "smoke-package",
    "package_description": "Smoke test package",
    "author_name": "Smoke Tester",
    "author_email": "smoke@example.com",
    "github_org": "smoke-org",
    "repo_name": "smoke-repo",
}
OVERLAY_DATA = {
    "workspace_name": "overlay-workspace",
    "package_name": "overlay-package",
    "package_description": "Overlay smoke package",
    "author_name": "Overlay Tester",
    "author_email": "overlay@example.com",
    "github_org": "overlay-org",
    "repo_name": "overlay-repo",
}
GIT_USER_EMAIL = "smoke@example.com"
GIT_USER_NAME = "Smoke Tester"


def copier_command() -> list[str]:
    if shutil.which("copier"):
        return ["copier"]
    if shutil.which("uvx"):
        return ["uvx", "copier"]
    raise SystemExit("Missing Copier. Install `copier` or `uv` before running the smoke test.")


def run(command: list[str], cwd: Path) -> None:
    print(f"+ {shlex.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def configure_git_repo(path: Path) -> None:
    run(["git", "init", "-b", "main"], path)
    run(["git", "config", "user.email", GIT_USER_EMAIL], path)
    run(["git", "config", "user.name", GIT_USER_NAME], path)


def commit_all(path: Path, message: str) -> None:
    run(["git", "add", "."], path)
    run(["git", "commit", "-m", message], path)


def create_template_snapshot(root: Path) -> Path:
    source_repo = root / "template-source"
    shutil.copytree(
        REPO_ROOT,
        source_repo,
        symlinks=True,
        ignore=shutil.ignore_patterns(".git", "node_modules", ".tbd", ".claude", "dist", "__pycache__"),
    )
    configure_git_repo(source_repo)
    commit_all(source_repo, "Initial template snapshot")
    return source_repo


def render_template(source_repo: Path, destination: Path, data: dict[str, str], *, overwrite: bool = False) -> None:
    command = copier_command() + ["copy", "--trust"]
    if overwrite:
        command.append("--overwrite")
    for key, value in data.items():
        command.extend(["--data", f"{key}={value}"])
    command.extend([str(source_repo), str(destination)])
    run(command, source_repo)


def assert_exists(path: Path, message: str) -> None:
    if not path.exists():
        raise SystemExit(message)


def assert_not_contains(path: Path, needle: str) -> None:
    if needle in path.read_text(encoding="utf-8"):
        raise SystemExit(f"{path} unexpectedly contains {needle!r}")


def validate_rendered_repo(destination: Path) -> None:
    answers_file = destination / ".copier-answers.yml"
    assert_exists(answers_file, "Rendered template is missing .copier-answers.yml")

    package_json = json.loads((destination / "package.json").read_text(encoding="utf-8"))
    scripts = package_json.get("scripts", {})
    if "compile-template" in scripts:
        raise SystemExit("Rendered package.json still includes compile-template")
    if "check" not in scripts:
        raise SystemExit("Rendered package.json is missing the check script")

    assert_not_contains(destination / "lefthook.yml", "template/**")
    assert_not_contains(destination / "eslint.config.js", "template/**")
    assert_not_contains(destination / "eslint.config.js", "attic/**")

    gitignore_lines = (destination / ".gitignore").read_text(encoding="utf-8").splitlines()
    if "attic/" in gitignore_lines:
        raise SystemExit("Rendered .gitignore still contains attic/")


def migrate_flat_repo_into_workspace(destination: Path, package_name: str) -> None:
    package_dir = destination / "packages" / package_name
    target_src = package_dir / "src"
    target_tests = package_dir / "tests"
    legacy_src = destination / "src"
    legacy_tests = destination / "tests"

    assert_exists(legacy_src, "Overlay workflow is missing the legacy root src directory")
    assert_exists(legacy_tests, "Overlay workflow is missing the legacy root tests directory")

    shutil.rmtree(target_src)
    shutil.rmtree(target_tests)
    shutil.move(str(legacy_src), str(target_src))
    shutil.move(str(legacy_tests), str(target_tests))


def exercise_fresh_render_workflow(source_repo: Path, root: Path) -> Path:
    destination = root / "fresh-render"
    render_template(source_repo, destination, FRESH_DATA)
    validate_rendered_repo(destination)

    run(["pnpm", "install"], destination)
    run(["pnpm", "build"], destination)
    run(["pnpm", "test"], destination)
    run(["pnpm", "check"], destination)

    configure_git_repo(destination)
    run(["pnpm", "prepare"], destination)

    hook_path = destination / ".git" / "hooks" / "pre-commit"
    assert_exists(hook_path, "lefthook pre-commit hook was not installed after git init")

    commit_all(destination, "Initial render")
    return destination


def exercise_update_workflow(source_repo: Path, rendered_repo: Path) -> None:
    local_note = rendered_repo / "LOCAL.md"
    local_note.write_text("Local change preserved across copier update.\n", encoding="utf-8")
    commit_all(rendered_repo, "Local project change")

    readme_template = source_repo / "template" / "README.md.jinja"
    readme_template.write_text(
        readme_template.read_text(encoding="utf-8")
        + "\nUpdate marker: pulled from copier update smoke test.\n",
        encoding="utf-8",
    )
    commit_all(source_repo, "Template update for copier smoke test")

    run(copier_command() + ["update", "--trust", "--defaults"], rendered_repo)

    assert_exists(local_note, "copier update removed a local non-template file")
    readme_text = (rendered_repo / "README.md").read_text(encoding="utf-8")
    if "Update marker: pulled from copier update smoke test." not in readme_text:
        raise SystemExit("copier update did not apply the upstream template change")

    run(["pnpm", "check"], rendered_repo)


def exercise_overlay_workflow(source_repo: Path, root: Path) -> None:
    destination = root / "overlay-repo"
    destination.mkdir(parents=True)
    configure_git_repo(destination)

    legacy_file = destination / "src" / "index.ts"
    legacy_file.parent.mkdir(parents=True)
    legacy_file.write_text("export const legacy = true;\n", encoding="utf-8")
    legacy_test = destination / "tests" / "index.test.ts"
    legacy_test.parent.mkdir(parents=True)
    legacy_test.write_text(
        "import { describe, expect, it } from 'vitest';\n"
        "import { legacy } from '../src/index';\n"
        "\n"
        "describe('legacy retrofit smoke test', () => {\n"
        "  it('preserves the migrated implementation', () => {\n"
        "    expect(legacy).toBe(true);\n"
        "  });\n"
        "});\n",
        encoding="utf-8",
    )
    notes_file = destination / "EXISTING.md"
    notes_file.write_text("Existing repo marker.\n", encoding="utf-8")
    commit_all(destination, "Existing repo baseline")

    render_template(source_repo, destination, OVERLAY_DATA, overwrite=True)
    validate_rendered_repo(destination)
    migrate_flat_repo_into_workspace(destination, OVERLAY_DATA["package_name"])

    migrated_src = destination / "packages" / OVERLAY_DATA["package_name"] / "src" / "index.ts"
    migrated_test = destination / "packages" / OVERLAY_DATA["package_name"] / "tests" / "index.test.ts"
    assert_exists(migrated_src, "Overlay workflow did not preserve the legacy source file")
    assert_exists(migrated_test, "Overlay workflow did not preserve the legacy test file")
    assert_exists(notes_file, "Overlay workflow removed an existing top-level file")
    if (destination / "src").exists() or (destination / "tests").exists():
        raise SystemExit("Overlay workflow left legacy root TypeScript directories unmigrated")

    run(["pnpm", "install"], destination)
    run(["pnpm", "check"], destination)

    hook_path = destination / ".git" / "hooks" / "pre-commit"
    assert_exists(hook_path, "Overlay workflow did not install Git hooks during pnpm install")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="simple-modern-pnpm-smoke-") as temp_dir:
        root = Path(temp_dir)
        source_repo = create_template_snapshot(root)
        rendered_repo = exercise_fresh_render_workflow(source_repo, root)
        exercise_update_workflow(source_repo, rendered_repo)
        exercise_overlay_workflow(source_repo, root)
        print("Template smoke test passed.")


if __name__ == "__main__":
    main()
