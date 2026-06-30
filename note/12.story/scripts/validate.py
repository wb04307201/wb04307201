#!/usr/bin/env python3
"""
校验 note/12.story/*.md 是否符合 STORY-FORMAT-SPEC.md。

检查项：
  1. 每个 leaf 都有 frontmatter（number / type / position / title / audience）
  2. ## 引言（§4.1）或 ### 一、开场（§4.3 戏剧体）至少有一个
  3. H1 必须是 `# NN · 标题` 格式（搜索整文件，兼容 frontmatter 前缀）
  4. 章节用中文数字（一/二/三），禁止 "1./Chapter N/第 N 章"
  5. 文末 `← [返回系列导读](./index.md)`
  6. 文章行数 ≥ 50
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORY = ROOT

ALLOWED_NUMBERS = (
    [f"{i:02d}" for i in range(1, 47) if i not in (17, 23)]
    + ["34a", "34b", "35a", "35b", "36a", "36b"]
)


def is_leaf_story(path: Path) -> bool:
    """是否是正传文章。"""
    return bool(re.match(r"^[0-9]+[a-c]?-\w", path.name))


def check_h1(text: str) -> list[str]:
    """检查 H1 编号格式（搜索整文件，兼容 frontmatter 前缀）。"""
    m = re.search(r"^# (\d+[a-c]?) · ", text, re.MULTILINE)
    if not m:
        return ["H1: 格式不符 '# NN · 标题'（如 '# 01 · 当餐厅长出大脑'）"]
    number = m.group(1)
    if number not in ALLOWED_NUMBERS:
        return [f"H1: 编号 {number} 未在合法清单"]
    return []


def check_frontmatter(text: str) -> list[str]:
    """检查 HTML frontmatter 注释块。"""
    if '<!--\nstory:' not in text[:500]:
        return ["frontmatter: 缺失或格式错（应以 '<!--\\nstory:' 开头）"]
    required = ["number:", "type:", "position:", "title:", "audience:"]
    for f in required:
        if f not in text[:500]:
            return [f"frontmatter: 缺字段 '{f}'"]
    return []


def check_intro(text: str) -> list[str]:
    """检查 ## 引言（§4.1）或 ### 一、开场（§4.3 戏剧体）。"""
    has_main = bool(re.search(r"^## 引言[：:]", text, re.MULTILINE))
    # 兼容"### 一、开场："或"### 一、开场 xxxx"
    has_drama = bool(re.search(r"^### 一、[^,\n]*开场", text, re.MULTILINE))
    if not (has_main or has_drama):
        return ["intro: 没有 ## 引言（§4.1）也没有 ### 一、开场（§4.3 戏剧体）"]
    return []


def check_chapter_numbering(text: str) -> list[str]:
    """检查章节标题用中文数字（跳过 fenced code block 内的 ##）。"""
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
            errors.append(f"L{i}: '## {stripped}' uses Arabic numbers (use 一、二、三)")
        if re.match(r"^Chapter\s+\d+", stripped):
            errors.append(f"L{i}: '## {stripped}' uses 'Chapter N' (use 一、二、三)")
        # spec §4.1 默认是 `## 第一章：xxx`（中文数字 + 第 N 章），所以禁止的
        # 仅仅是阿拉伯数字的"第 N 章"。中文数字 + 第 N 章是 OK 的。
        if re.match(r"^第\s*[0-9]+\s*章", stripped):
            errors.append(f"L{i}: '## {stripped}' uses '## 第 N 章' 阿拉伯数字 (use '## 一、xxx' 或 '## 第一章：xxx')")
    return errors


def check_back_link(text: str) -> list[str]:
    """检查文末回链到 index.md。"""
    last_500 = text[-500:]
    if "← [返回系列导读]" not in last_500:
        return ["back-link: 文末缺 '← [返回系列导读]'"]
    return []


def check_min_length(text: str) -> list[str]:
    lines = sum(1 for line in text.split("\n") if line.strip())
    if lines < 50:
        return [f"length: 仅 {lines} 行（规范建议 50-300 行）"]
    return []


def validate_file(path: Path) -> tuple[list[str], list[str]]:
    if not is_leaf_story(path):
        return [], []

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"read error: {e}"], []

    errors = []
    errors.extend(check_h1(text))
    errors.extend(check_frontmatter(text))
    errors.extend(check_intro(text))
    errors.extend(check_chapter_numbering(text))
    errors.extend(check_back_link(text))
    errors.extend(check_min_length(text))
    return errors, []


def main() -> int:
    md_files = sorted(STORY.glob("[0-9]*.md"))
    md_files = [p for p in md_files if is_leaf_story(p)]

    total = len(md_files)
    errors_total = 0
    print(f"== 校验 {total} 个 story 文章 ==\n")

    for f in md_files:
        rel = f.relative_to(STORY)
        errors, _ = validate_file(f)
        if errors:
            errors_total += len(errors)
            for e in errors:
                print(f"  [ERR] {rel}: {e}")

    print(f"\n== Summary: {total} files, {errors_total} errors ==")
    return 1 if errors_total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
