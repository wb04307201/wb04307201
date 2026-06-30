#!/usr/bin/env python3
"""
给 note/01-11 主模块 README 加 frontmatter。

frontmatter 模板（HTML 注释）：
    <!--
    module:
      number: 01
      slug: java
      topic: Java 知识体系
      audience: 工程师 / 架构师
      category: 主模块
      summary: <一句话核心内容，从 README L3-5 提取>
    -->

中包含"summary"的推断：从 README L3-7 中第一个非标题段落提取，截前 80 字。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTE = ROOT


def extract_summary(text: str, max_chars: int = 80) -> str:
    """从 README 中 H1 后第一个有效的非空段落提取摘要。

    跳过 "最后更新: YYYY-MM-DD" / "Updated: ..." 这类时间戳元行。
    """
    lines = text.split("\n")
    in_body = False
    skip_pattern = re.compile(r"^最后更新\s*[:：]|^更新\s*[:：]|^\s*Updated\s*[:：]")
    for line in lines:
        if line.startswith("# "):
            in_body = True
            continue
        if not in_body:
            continue
        s = line.strip()
        if not s:
            continue
        if s.startswith(">"):
            s = s.lstrip(">").strip()
        if s.startswith("#"):
            continue
        # 跳过元数据行（"最后更新"、"Updated" 等）
        if skip_pattern.match(s):
            continue
        if len(s) > max_chars:
            s = s[:max_chars].rstrip() + "..."
        return s
    return ""


def has_frontmatter(text: str) -> bool:
    return text.startswith("<!--\nmodule:")


def make_frontmatter(number: str, slug: str, topic: str,
                     audience: str, summary: str) -> str:
    return (
        "<!--\n"
        "module:\n"
        f"  number: {number}\n"
        f"  slug: {slug}\n"
        f"  topic: {topic}\n"
        f"  audience: {audience}\n"
        "  category: 主模块\n"
        f"  summary: {summary}\n"
        "-->\n\n"
    )


# 手工维护映射：1-11 主模块 → (number, slug, topic, audience)
META = {
    "01.java":                 ("01", "java", "Java 知识体系", "工程师 / 架构师"),
    "02.computer-basics":      ("02", "computer-basics", "计算机基础", "工程师 / SRE"),
    "03.database":            ("03", "database", "数据库", "工程师 / DBA"),
    "04.system-design":       ("04", "system-design", "系统设计", "架构师 / SRE"),
    "05.tools":               ("05", "tools", "工具链", "工程师 / DevOps"),
    "06.spring":              ("06", "spring", "Spring 全家桶", "Java 工程师"),
    "07.workflow":            ("07", "workflow", "工作流", "架构师 / 业务负责人"),
    "08.application-systems": ("08", "application-systems", "业务应用系统速查", "业务 / PM / 需求"),
    "09.front-end":           ("09", "front-end", "前端工程", "前端 / 全栈工程师"),
    "10.big-data":            ("10", "big-data", "大数据", "数据工程师 / 后端"),
    "11.ai":                  ("11", "ai", "AI 知识体系", "AI 工程师 / 后端"),
}


def main(only: str | None = None) -> None:
    """入口：only=None 处理全部 11 个主模块；only='01.java' 处理单个。"""
    targets = META
    if only:
        if only not in META:
            print(f"未知模块: {only}")
            return
        targets = {only: META[only]}

    changed = 0
    skipped = 0
    for slug, meta in targets.items():
        path = NOTE / slug / "README.md"
        if not path.exists():
            print(f"  [.] SKIP missing: {slug}")
            skipped += 1
            continue
        text = path.read_text(encoding="utf-8")
        if has_frontmatter(text):
            print(f"  [.] {slug}: 已有 frontmatter")
            skipped += 1
            continue
        number, slug_id, topic, audience = meta
        summary = extract_summary(text)
        fm = make_frontmatter(number, slug_id, topic, audience, summary)
        path.write_text(fm + text, encoding="utf-8")
        changed += 1
        print(f"  [+] {slug}: ok (summary={len(summary)} chars)")

    print(f"\n== Total {len(targets)} -> changed {changed} / skipped {skipped}")


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    main(only)
