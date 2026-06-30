#!/usr/bin/env python3
"""
校验 note/ 全部 14 个主模块 README 是否符合基础规范。

校验项：
  1. 主模块 README 末尾是否含 '← 返回笔记目录' 回链
     （仅 14.project-management 已在更早时自带回链时豁免——本规范 2026 落地）
  2. H1 标题不应带数字前缀（'# 五、' 或 '# 07'）
  3. H1 标题后第一行应是一句话定位（blockquote 或简短一句）

依据：note/CONTRIBUTING.md §2（模块 README 模板）

用法：
    python note/scripts/validate.py            # 校验全部
    python note/scripts/validate.py 01.java    # 只校验某个
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTE = ROOT

MAIN_MODULES = {
    "01.java",
    "02.computer-basics",
    "03.database",
    "04.system-design",
    "05.tools",
    "06.spring",
    "07.workflow",
    "08.application-systems",
    "09.front-end",
    "10.big-data",
    "11.ai",
    "12.story",
    "13.split-hairs",
    "14.project-management",
}


def check_back_link(path: Path) -> list[str]:
    last_300 = path.read_text(encoding="utf-8")[-300:]
    if "返回笔记目录" not in last_300:
        return ["back-link: 文末缺 '← [返回笔记目录]'"]
    return []


def check_h1_title(path: Path) -> list[str]:
    """H1 不应以 '## 数字' / '# 数字、' 开头。"""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^# (\d+[\.\s、：:])", text)
    if m:
        return [f"H1: 标题含数字编号 '{m.group(0).strip()}'（统一不带）"]
    return []


def check_one_line_pitch(path: Path) -> list[str]:
    """H1 后应有一句话定位（blockquote 或单段）。"""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    for i, line in enumerate(lines[:10]):
        if line.startswith("# "):
            # 找 H1 之后到下一个 ---- / ## 之间的内容
            block = []
            for j in range(i + 1, min(i + 8, len(lines))):
                l = lines[j].strip()
                if l.startswith("---") or l.startswith("##"):
                    break
                if l:
                    block.append(l)
            if not block:
                return [f"H1: 后无一句话定位（建议加 blockquote）"]
            return []
    return []


def validate_module(name: str) -> list[str]:
    path = NOTE / name / "README.md"
    if not path.exists():
        return [f"missing: {path.relative_to(NOTE)}"]
    errors = []
    errors.extend(check_back_link(path))
    errors.extend(check_h1_title(path))
    errors.extend(check_one_line_pitch(path))
    return errors


def main(only: str | None = None) -> int:
    modules = MAIN_MODULES
    if only:
        modules = {only} if only in MAIN_MODULES else set()
        if not modules:
            print(f"未知模块: {only}")
            return 1

    total = len(modules)
    errors_total = 0
    print(f"== 校验 {total} 个主模块 README ==\n")

    for name in sorted(modules):
        rel = name + "/README.md"
        errors = validate_module(name)
        if errors:
            errors_total += len(errors)
            for e in errors:
                print(f"  [ERR] {rel}: {e}")
        else:
            print(f"  [OK]  {rel}")

    print(f"\n== Summary: {total} files, {errors_total} errors ==")
    return 1 if errors_total > 0 else 0


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    sys.exit(main(only))
