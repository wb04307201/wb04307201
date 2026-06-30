#!/usr/bin/env python3
"""
批量给 note/14.project-management/**/*.md 插入 frontmatter。

frontmatter 模板：
    <!--
    pm:
      topic: <主题名>
      audience: <老板|PM|CTO|创业者>
      category: 决策实战
      summary: <一句话核心问题>
      checklist: [算 TCO, 评估风险, ...]
    -->

本模块无固定编号（不像 12.story / 13.split-hairs）；
metadata 通过手工维护的 META 表 + 文件名推断 topic。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PM = ROOT

# 文件名 → PM 主题元数据
META = {
    "app-quote-breakdown": {
        "topic": "报价拆解",
        "audience": "老板 / PM / 创业者",
        "summary": "5 万 vs 50 万 App 报价背后的 12 大成本维度",
    },
    "outsourcing-pitfalls": {
        "topic": "外包避坑",
        "audience": "老板 / PM / 创业者",
        "summary": "外包项目的 5 大隐性成本 + 合同 8 条必看条款",
    },
    # 待添加：4 篇候选
    "self-vs-saas-vs-outsourcing": {
        "topic": "技术选型 ROI",
        "audience": "CTO / 技术总监",
        "summary": "自研 vs SaaS vs 外包三种方案的全生命周期 ROI 对比",
    },
    "ai-pm-dora-space": {
        "topic": "AI 项目管理账本",
        "audience": "CTO / PM / 研发效能负责人",
        "summary": "DORA + SPACE + ROI 三件套，AI 时代研发效能度量框架",
    },
    "team-sizing-3x-buffer": {
        "topic": "人力配比 + 排期",
        "audience": "PM / 创业公司 CTO",
        "summary": "团队配比模型 + 排期 3 倍缓冲原则",
    },
    "conways-law-team-topologies": {
        "topic": "组织/团队",
        "audience": "架构师 / CTO",
        "summary": "康威定律下的团队拓扑：组织结构如何映射系统架构",
    },
}


def has_frontmatter(text: str) -> bool:
    return '<!--\npm:' in text[:200]


def make_frontmatter(topic: str, audience: str, summary: str) -> str:
    return (
        "<!--\n"
        "pm:\n"
        f"  topic: {topic}\n"
        f"  audience: {audience}\n"
        "  category: 决策实战\n"
        f"  summary: {summary}\n"
        "-->\n\n"
    )


def process_file(path: Path) -> tuple[bool, str]:
    leaf = path.parent.name
    meta = META.get(leaf)
    if not meta:
        return False, f"unknown leaf: {leaf}"

    text = path.read_text(encoding="utf-8")
    if has_frontmatter(text):
        return False, "已有 frontmatter"

    fm = make_frontmatter(meta["topic"], meta["audience"], meta["summary"])
    path.write_text(fm + text, encoding="utf-8")
    return True, f"{leaf}: topic={meta['topic']}"


def main(limit: int | None = None) -> None:
    files = sorted(PM.glob("*/README.md"))
    files = [f for f in files if f.parent.name in META]
    if limit:
        files = files[:limit]

    changed = 0
    skipped = 0
    for f in files:
        ok, msg = process_file(f)
        if ok:
            changed += 1
            print(f"  [+] {msg}")
        else:
            skipped += 1
            print(f"  [.] {msg}")

    print(f"\n== Total {len(files)} files -> changed {changed} / skipped {skipped}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
