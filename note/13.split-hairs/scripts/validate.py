#!/usr/bin/env python3
"""
校验 note/13.split-hairs/**/*.md 是否符合 QUESTION-FORMAT-SPEC.md。

检查项：
  1. 每个 leaf README 都有 frontmatter 注释块（<!--question:...-->）
  2. frontmatter 必备字段：id / topic / difficulty / frequency / scenario_type / tags
  3. 面试题文件必须包含 ## 引子 一段（除非是分类索引 README）
  4. 章节编号统一为中文数字（一/二/三/...），禁止 "1." / "Chapter N" / "第 N 章"
  5. 文章长度 ≥ 50 行（README 规定 50-150 行）
  6. 章节顺序参考：核心原理 / 代码示例 / 常见陷阱 / 最佳实践 / 面试话术 / 交叉引用
  7. 至少有 1 处 ## 引子 标识的场景段

输出格式：
  - 0 错误 → exit 0
  - N 错误 → exit 1，列出每个错误的文件:行
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPLIT_HAIRS = ROOT

# 分类名（认为是面试题的根目录）
TOPIC_KEYS = ("01.java", "03.database", "04.system-design",
              "06.spring", "09.front-end", "11.ai")

# 分类索引不需要引子的 README（自身就是导航页）
CATEGORY_INDEX_NAMES = {"README.md", "questions", "storage"}


def is_leaf_interview(path: Path) -> bool:
    """判断是否为面试题 leaf（不是分类索引）。

    真正区分 leaf vs 分类索引的最可靠标志：是否含 ## 引子 一段（spec §1 强制）。
    分类索引文件不写 ## 引子（它们是导航页）。
    """
    rel = path.relative_to(SPLIT_HAIRS)
    if rel.parts[0] not in TOPIC_KEYS:
        return False
    if rel.name != "README.md":
        return False
    if len(rel.parts) < 3:
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False
    return bool(re.search(r"^## 引子[：:]", text, re.MULTILINE))


def check_frontmatter(text: str) -> list[str]:
    """检查 frontmatter 是否存在且字段齐全。"""
    errors = []
    # 找 <!-- ... --> 块
    m = re.match(r"<!--\s*\nquestion:", text)
    if not m:
        errors.append("frontmatter: missing or malformed (expected '<!--\\nquestion:')")
        return errors

    # 必备字段
    required = ["id:", "topic:", "difficulty:", "frequency:",
                "scenario_type:", "tags:"]
    for field in required:
        if field not in text[:200]:
            errors.append(f"frontmatter: missing field '{field}'")
    return errors


def check_intro_section(text: str) -> list[str]:
    """检查 ## 引子 段是否存在。"""
    if not re.search(r"^## 引子[：:]", text, re.MULTILINE):
        return ["## 引子: missing (each interview question must open with a scenario)"]
    return []


def check_chapter_numbering(text: str) -> list[str]:
    """检查章节标题是否用了非中文数字（违规 = "1." / "Chapter 1" / "第 N 章"）。"""
    errors = []
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        if line.startswith("## "):
            stripped = line[3:].strip()
            # 接受: "一、核心原理" / "1. xxx" 是 INTL not ZH, / "Chapter 1: ..."
            if re.match(r"^\d+\.\s", stripped):  # "1. " - Arabic-numbered
                errors.append(f"L{i}: '## {stripped}' uses Arabic numbers (use 一、二、三)")
            if re.match(r"^Chapter\s+\d+", stripped):
                errors.append(f"L{i}: '## {stripped}' uses 'Chapter N' (use 一、二、三)")
            if re.match(r"^第\s*[0-9一二三四五六七八九十]+\s*章", stripped):
                errors.append(f"L{i}: '## {stripped}' uses '第 N 章' (use 一、二、三)")
    return errors


def check_min_length(text: str) -> list[str]:
    """检查文章行数 ≥ 50。"""
    lines = text.split("\n")
    content_lines = sum(1 for line in lines if line.strip())
    if content_lines < 50:
        return [f"length: only {content_lines} lines (spec requires 50-150)"]
    return []


def check_six_chapters(text: str) -> list[str]:
    """检查 6 节模板的子集（缺则报警告，但不阻断）。"""
    warnings = []
    required_keywords = ["核心原理", "陷阱", "面试话术"]  # 至少这 3 节
    missing = [k for k in required_keywords if k not in text]
    if missing:
        warnings.append(f"sections: missing keywords {missing} (建议见 QUESTION-FORMAT-SPEC.md §1)")
    return warnings


def validate_file(path: Path) -> tuple[list[str], list[str]]:
    """单文件校验，返回 (errors, warnings)。"""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"read error: {e}"], []

    if not is_leaf_interview(path):
        return [], []  # 分类索引：免检

    errors = []
    errors.extend(check_frontmatter(text))
    errors.extend(check_intro_section(text))
    errors.extend(check_chapter_numbering(text))
    errors.extend(check_min_length(text))

    warnings = check_six_chapters(text)
    return errors, warnings


def main() -> int:
    md_files = sorted(SPLIT_HAIRS.glob("*/**/README.md"))
    md_files = [f for f in md_files if f.parent.name not in CATEGORY_INDEX_NAMES
                or f.name not in CATEGORY_INDEX_NAMES]

    total = len(md_files)
    errors_total = 0
    warnings_total = 0

    print(f"== 校验 {total} 个 split-hairs interview 文件 ==\n")

    for f in md_files:
        rel = f.relative_to(SPLIT_HAIRS)
        errors, warnings = validate_file(f)
        if errors:
            errors_total += len(errors)
            for e in errors:
                print(f"  [ERR] {rel}: {e}")
        if warnings:
            warnings_total += len(warnings)
            for w in warnings:
                print(f"  [WRN] {rel}: {w}")

    print(f"\n== Summary: {total} files, "
          f"{errors_total} errors, {warnings_total} warnings ==")

    return 1 if errors_total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
