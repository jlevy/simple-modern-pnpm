#!/usr/bin/env python3
"""
Compile the working project into a Copier template.

This script implements the "reverse compile" approach: the repo root is a fully
functional project using fixed placeholder names, and this script generates
the Copier template directory by replacing those names with Jinja variables.

Usage:
    python admin/compile_template.py

The output is written to admin/template/ and should be committed to git.
"""

import re
import shutil
from pathlib import Path

# Repository root (parent of admin/)
REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "admin" / "template"

# Placeholder mappings: working value -> Jinja variable
# Ordered longest-first to prevent partial matches
REPLACEMENTS = [
    ("A modern TypeScript package", "{{ package_description }}"),
    ("author@example.com", "{{ author_email }}"),
    ("Package Author", "{{ author_name }}"),
    ("my-workspace", "{{ workspace_name }}"),
    ("my-package", "{{ package_name }}"),
    ("my-repo", "{{ repo_name }}"),
    ("my-org", "{{ github_org }}"),
]

# Root-level paths to exclude from the template
EXCLUDED_ROOT_PATHS = {
    "admin",
    "copier.yml",
    "README.md",
    "LICENSE",
    "CLAUDE.md",
    "AGENTS.md",
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


def compile_template() -> None:
    """Generate the Copier template from the working project."""
    # Clean output directory
    if TEMPLATE_DIR.exists():
        shutil.rmtree(TEMPLATE_DIR)
    TEMPLATE_DIR.mkdir(parents=True)

    # Walk the repo root
    for source_path in sorted(REPO_ROOT.rglob("*")):
        if not source_path.is_file():
            continue

        if is_excluded(source_path):
            continue

        # Compute relative path from repo root
        rel_path = source_path.relative_to(REPO_ROOT)

        # Apply directory renaming: packages/my-package -> packages/{{ package_name }}
        parts = list(rel_path.parts)
        for i, part in enumerate(parts):
            if part == "my-package" and i > 0 and parts[i - 1] == "packages":
                parts[i] = "{{ package_name }}"
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

        if was_modified:
            # Add .jinja suffix for files that were modified
            dest_path = dest_path.parent / (dest_path.name + ".jinja")

        dest_path.write_text(new_content, encoding="utf-8")

    # Create special Copier files

    # 1. Copier answers file (for copier update support)
    answers_path = TEMPLATE_DIR / "{{ _copier_conf.answers_file }}.jinja"
    answers_path.write_text(
        "# This file was generated by Copier. Do not edit manually.\n"
        "{{ _copier_conf | to_yaml }}\n",
        encoding="utf-8",
    )

    # 2. Starter README for generated projects
    readme_path = TEMPLATE_DIR / "README.md.jinja"
    readme_path.write_text(
        "# {{ repo_name }}\n"
        "\n"
        "{{ package_description }}\n"
        "\n"
        "## Development\n"
        "\n"
        "```bash\n"
        "pnpm install\n"
        "pnpm build\n"
        "pnpm test\n"
        "```\n"
        "\n"
        "## License\n"
        "\n"
        "MIT\n",
        encoding="utf-8",
    )

    # 3. Placeholder LICENSE for generated projects
    license_path = TEMPLATE_DIR / "LICENSE"
    license_path.write_text(
        "TODO: Add your license here.\n"
        "\n"
        "Choose a license at https://choosealicense.com/\n"
        "Common choices: MIT, Apache-2.0, ISC\n",
        encoding="utf-8",
    )

    # Summary
    file_count = sum(1 for _ in TEMPLATE_DIR.rglob("*") if _.is_file())
    jinja_count = sum(1 for _ in TEMPLATE_DIR.rglob("*.jinja") if _.is_file())
    print(f"Compiled template to {TEMPLATE_DIR.relative_to(REPO_ROOT)}/")
    print(f"  {file_count} files total, {jinja_count} with .jinja suffix")


if __name__ == "__main__":
    compile_template()
