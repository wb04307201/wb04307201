#!/usr/bin/env python3
"""
校验 note/14.project-management/**/*.md 是否合规。

检查项：
  1. frontmatter 注释块（pm + 缩进字段 topic / audience / summary）
  2. ## 引言 一段（场景开篇）
  3. 文末回链到 README.md
  4. 文章行数 ≥ 50
  5. 中文数字章节编号（跳过 fenced code block）
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PM = ROOT


def is_leaf_pm(path: Path) -> bool:
    return (path.name == "README.md"
            and path.parent.parent == PM
            and path.parent.name not in {"scripts"})


def check_frontmatter(text: str) -> list[str]:
    if "<!--\npm:" not in text[:500]:
        return ["frontmatter: 缺失（应以 '<!--\\npm:' 开头）"]
    # 注意：实际 frontmatter 中字段是缩进的 `  topic:`
    for field in ("  topic:", "  audience:", "  summary:"):
        if field not in text[:600]:
            return [f"frontmatter: 缺字段 '{field.strip()}'"]
    return []


def check_intro(text: str) -> list[str]:
    if not re.search(r"^## 引言[：:]", text, re.MULTILINE):
        return ["## 引言: missing (每篇必须以场景开篇)"]
    return []


def check_back_link(text: str) -> list[str]:
    last_300 = text[-300:]
    if "[" not in last_300 or "README" not in last_300:
        return ["back-link: 文末缺到 README 的回链"]
    return []


def check_chapter_numbering(text: str) -> list[str]:
    errors = []
    in_code = False
    for i, line in enumerate(text.split("\n"), 1):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line.startswith("## "):
            continue
        stripped = line[3:].strip()
        if re.match(r"^\d+\.\s", stripped):
            errors.append(f"L{i}: '## {stripped}' uses Arabic numbers")
        if re.match(r"^Chapter\s+\d+", stripped):
            errors.append(f"L{i}: '## {stripped}' uses 'Chapter N'")
        if re.match(r"^第\s*[0-9]+\s*章", stripped):
            errors.append(f"L{i}: '## {stripped}' uses '## 第 N 章'")
    return errors


def check_min_length(text: str) -> list[str]:
    lines = sum(1 for line in text.split("\n") if line.strip())
    if lines < 50:
        return [f"length: 仅 {lines} 行（建议 ≥ 50）"]
    return []


def validate_file(path: Path) -> tuple[list[str], list[str]]:
    if not is_leaf_pm(path):
        return [], []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"read error: {e}"], []

    errors = []
    errors.extend(check_frontmatter(text))
    errors.extend(check_intro(text))
    errors.extend(check_chapter_numbering(text))
    errors.extend(check_back_link(text))
    errors.extend(check_min_length(text))
    return errors, []


def main() -> int:
    files = sorted(PM.glob("*/README.md"))
    files = [f for f in files if is_leaf_pm(f)]

    total = len(files)
    errors_total = 0
    print(f"== 校验 {total} 个 PM 文章 ==\n")
    for f in files:
        rel = f.relative_to(PM)
        errors, _ = validate_file(f)
        if errors:
            errors_total += len(errors)
            for e in errors:
                print(f"  [ERR] {rel}: {e}")

    print(f"\n== Summary: {total} files, {errors_total} errors ==")
    return 1 if errors_total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
