#!/usr/bin/env python3
"""
Compile the working project into a Copier template.

This script implements the "reverse compile" approach: the repo root is a fully
functional project using fixed placeholder names, and this script generates
the Copier template directory by replacing those names with Jinja variables.

Usage:
    python admin/compile_template.py

The output is written to template/ and should be committed to git.
"""

import os
import re
import shutil
from pathlib import Path

# Repository root (parent of admin/)
REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "template"

# Placeholder mappings: working value -> Jinja variable
# Ordered longest-first to prevent partial matches
# Using [[ ]] delimiters to avoid conflicts with GitHub Actions ${{ }} syntax
REPLACEMENTS = [
    ("A modern TypeScript package", "[[ package_description ]]"),
    ("author@example.com", "[[ author_email ]]"),
    ("Package Author", "[[ author_name ]]"),
    ("placeholder-workspace", "[[ workspace_name ]]"),
    ("placeholder-package", "[[ package_name ]]"),
    ("placeholder-repo", "[[ repo_name ]]"),
    ("placeholder-org", "[[ github_org ]]"),
]

# Root-level paths to exclude from the template
EXCLUDED_ROOT_PATHS = {
    "admin",
    "template",
    "copier.yml",
    "README.md",
    "LICENSE",
    ".claude",
    ".tbd",
    ".tbd-sync",
    "attic",
    "pnpm-lock.yaml",
    ".git",
    ".gitattributes",
}

# Directory names excluded at ANY depth (build artifacts, dependencies)
EXCLUDED_DIR_NAMES = {
    "node_modules",
    "dist",
}

# Binary file extensions (copy without text replacement)
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".svg",
    ".woff", ".woff2", ".ttf", ".eot",
    ".zip", ".tar", ".gz", ".bz2",
    ".pdf", ".exe", ".dll", ".so", ".dylib",
}


def normalize_text_content(content: str) -> str:
    """Normalize text files to exactly one trailing newline."""
    return content.rstrip("\n") + "\n"


def is_excluded(path: Path) -> bool:
    """Check if a path should be excluded from the template."""
    rel = path.relative_to(REPO_ROOT)
    parts = rel.parts
    # Check root-level exclusions
    if parts and parts[0] in EXCLUDED_ROOT_PATHS:
        return True
    if len(parts) == 1 and parts[0] in EXCLUDED_ROOT_PATHS:
        return True
    # Check directory names excluded at any depth
    for part in parts:
        if part in EXCLUDED_DIR_NAMES:
            return True
    return False


def is_binary(path: Path) -> bool:
    """Check if a file is binary based on extension."""
    return path.suffix.lower() in BINARY_EXTENSIONS


def strip_admin_only(content: str) -> str:
    """Remove lines between ADMIN-ONLY-START and ADMIN-ONLY-END markers."""
    return re.sub(
        r"^[^\n]*ADMIN-ONLY-START.*?^[^\n]*ADMIN-ONLY-END[^\n]*\n?",
        "",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )


def apply_replacements(content: str) -> tuple[str, bool]:
    """Apply placeholder replacements and strip admin-only sections.

    Returns (new_content, was_modified).
    """
    original = content
    content = strip_admin_only(content)
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)
    return content, content != original


def sanitize_generated_content(rel_path: Path, content: str) -> tuple[str, bool]:
    """Remove template-admin-only content from generated files."""
    original = content
    path = rel_path.as_posix()

    if path == ".gitignore":
        content = "\n".join(line for line in content.splitlines() if line != "attic/")
    elif path == "lefthook.yml":
        content = content.replace("        - template/**\n", "")
    elif path == "eslint.config.js":
        content = content.replace("      'template/**',\n", "")
        content = content.replace("      'attic/**',\n", "")
    elif path == "package.json":
        content = re.sub(
            r'\n\s+"compile-template": "python admin/compile_template.py"',
            "",
            content,
        )
        content = re.sub(r",\n(\s*[}\]])", r"\n\1", content)

    return content, content != original


def compile_template() -> None:
    """Generate the Copier template from the working project."""
    # Clean output directory
    if TEMPLATE_DIR.exists():
        shutil.rmtree(TEMPLATE_DIR)
    TEMPLATE_DIR.mkdir(parents=True)

    symlinks: list[tuple[Path, str]] = []

    # Walk the repo root
    for source_path in sorted(REPO_ROOT.rglob("*")):
        # Preserve relative symlinks as symlinks in the template
        if source_path.is_symlink():
            if is_excluded(source_path):
                continue
            target = os.readlink(source_path)
            rel_path = source_path.relative_to(REPO_ROOT)
            symlinks.append((rel_path, target))
            continue

        if not source_path.is_file():
            continue

        if is_excluded(source_path):
            continue

        # Compute relative path from repo root
        rel_path = source_path.relative_to(REPO_ROOT)

        # Apply directory renaming: packages/placeholder-package -> packages/[[ package_name ]]
        parts = list(rel_path.parts)
        for i, part in enumerate(parts):
            if part == "placeholder-package" and i > 0 and parts[i - 1] == "packages":
                parts[i] = "[[ package_name ]]"
        rel_path = Path(*parts)

        # Determine output path
        dest_path = TEMPLATE_DIR / rel_path

        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if is_binary(source_path):
            # Copy binary files without modification
            shutil.copy2(source_path, dest_path)
            continue

        # Read and process text files
        try:
            content = source_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, ValueError):
            # If we can't read as text, treat as binary
            shutil.copy2(source_path, dest_path)
            continue

        new_content, was_modified = apply_replacements(content)
        new_content, was_sanitized = sanitize_generated_content(rel_path, new_content)
        new_content = normalize_text_content(new_content)
        was_modified = was_modified or was_sanitized or new_content != content

        if was_modified:
            # Add .jinja suffix for files that were modified
            dest_path = dest_path.parent / (dest_path.name + ".jinja")

        dest_path.write_text(new_content, encoding="utf-8")

    # Create symlinks in the template output
    for rel_path, target in symlinks:
        dest_path = TEMPLATE_DIR / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(target, dest_path)

    # Create special Copier files

    # 1. Copier answers file (required for `copier update`)
    answers_path = TEMPLATE_DIR / "[[ _copier_conf.answers_file ]].jinja"
    answers_path.write_text(
        normalize_text_content(
            "# Changes here will be overwritten by Copier\n"
            "[[ _copier_answers|to_nice_yaml -]]"
        ),
        encoding="utf-8",
    )

    # 2. Starter README for generated projects
    readme_path = TEMPLATE_DIR / "README.md.jinja"
    readme_path.write_text(
        normalize_text_content(
            "# [[ repo_name ]]\n"
            "\n"
            "[[ package_description ]]\n"
            "\n"
            "This repo was generated from "
            "[simple-modern-pnpm](https://github.com/jlevy/simple-modern-pnpm), "
            "an agent-friendly template for a modern model repo in TypeScript using pnpm.\n"
            "\n"
            "## Bootstrap\n"
            "\n"
            "```bash\n"
            "pnpm install\n"
            "pnpm check\n"
            "```\n"
            "\n"
            "If you created this repo in a scratch directory before `git init`, run:\n"
            "\n"
            "```bash\n"
            "git init -b main\n"
            "pnpm prepare\n"
            "```\n"
            "\n"
            "## Template Updates\n"
            "\n"
            "Keep `.copier-answers.yml` committed. To pull upstream template updates:\n"
            "\n"
            "```bash\n"
            "uvx copier update\n"
            "pnpm install\n"
            "pnpm check\n"
            "```\n"
            "\n"
            "## Docs\n"
            "\n"
            "- [docs/development.md](docs/development.md) - development workflow and Copier guidance\n"
            "- [docs/publishing.md](docs/publishing.md) - release and publishing workflow\n"
            "- `AGENTS.md` and `CLAUDE.md` mirror the development guide for coding agents\n"
            "\n"
            "## License\n"
            "\n"
            "See [LICENSE](LICENSE).\n"
        ),
        encoding="utf-8",
    )

    # 3. MIT LICENSE template for generated projects
    license_path = TEMPLATE_DIR / "LICENSE"
    license_path.write_text(
        normalize_text_content(
            "MIT License\n"
            "\n"
            "Copyright (c) [year] [fullname]\n"
            "\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
            "of this software and associated documentation files (the \"Software\"), to deal\n"
            "in the Software without restriction, including without limitation the rights\n"
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
            "copies of the Software, and to permit persons to whom the Software is\n"
            "furnished to do so, subject to the following conditions:\n"
            "\n"
            "The above copyright notice and this permission notice shall be included in all\n"
            "copies or substantial portions of the Software.\n"
            "\n"
            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
            "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
            "SOFTWARE.\n"
        ),
        encoding="utf-8",
    )

    # Summary
    file_count = sum(1 for _ in TEMPLATE_DIR.rglob("*") if _.is_file())
    jinja_count = sum(1 for _ in TEMPLATE_DIR.rglob("*.jinja") if _.is_file())
    symlink_count = len(symlinks)
    print(f"Compiled template to {TEMPLATE_DIR.relative_to(REPO_ROOT)}/")
    print(f"  {file_count} files total, {jinja_count} with .jinja suffix, {symlink_count} symlinks")


if __name__ == "__main__":
    compile_template()
