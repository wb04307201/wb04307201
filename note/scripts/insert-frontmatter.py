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


def main(only: str | None = None, with_subs: bool = False) -> None:
    """入口：only=None 处理全部 11 个主模块；only='01.java' 处理单个。

    with_subs=True 同时处理该主模块下的子 README（mode: article）。
    """
    targets = META
    if only:
        if only not in META:
            print(f"未知模块: {only}")
            return
        targets = {only: META[only]}

    changed = 0
    skipped = 0
    for slug, meta in targets.items():
        topic_dir = NOTE / slug
        number, slug_id, topic, audience = meta

        # 1) 主模块 README 自身
        readme = topic_dir / "README.md"
        if readme.exists():
            text = readme.read_text(encoding="utf-8")
            if has_frontmatter(text):
                skipped += 1
            else:
                summary = extract_summary(text)
                fm = make_frontmatter(number, slug_id, topic, audience, summary)
                readme.write_text(fm + text, encoding="utf-8")
                changed += 1

        # 2) 子 README（with_subs 开启时）
        if with_subs:
            for sub in topic_dir.glob("**/*/README.md"):
                if sub == readme:
                    continue
                rel = sub.relative_to(topic_dir)
                # 跳过 examples/ training/ 等非文章目录（启发：含 'examples' / 'training' / 'tutorial-images' 路径的）
                rel_str = str(rel).lower()
                if any(skip in rel_str for skip in (
                    "examples/", "training/", "tutorial-images/",
                    "/imgs/", "/images/",
                )):
                    continue
                leaf = sub.parent.name
                t = sub.read_text(encoding="utf-8")
                if has_frontmatter(t):
                    skipped += 1
                    continue
                # 子级 module 字段：article mode
                fm = (
                    "<!--\n"
                    "module:\n"
                    f"  parent: {slug_id}\n"
                    f"  slug: {slug_id}/{leaf}\n"
                    f"  type: article\n"
                    "  category: 主模块子文章\n"
                    f"  summary: {extract_summary(t)}\n"
                    "-->\n\n"
                )
                sub.write_text(fm + t, encoding="utf-8")
                changed += 1

    print(f"\n== changed {changed} / skipped {skipped}")


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    with_subs = "--subs" in sys.argv
    main(only, with_subs=with_subs)
