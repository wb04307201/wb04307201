#!/usr/bin/env python3
"""
批量给 note/12.story/*.md 插入 frontmatter。

frontmatter 字段：
  story:
    number: <01-46 或 34a 等>
    type: <前传|续集N|正传 N|终章|番外 N>
    title: <从 H1 提取>
    audience: <从 README "推荐阅读路线" 推断，可空>

依据 STORY-FORMAT-SPEC.md §10。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORY = ROOT

# 文件 → (number, type, position)
# 来源：note/12.story/README.md L166 "44 个叙事段中..."
META = {
    "01-ai-agent-architecture.md": ("01", "续集", "续集一"),
    "02-system-architecture-evolution.md": ("02", "前传", "前传"),
    "03-refactoring-guide-for-pm.md": ("03", "番外", "番外一"),
    "04-peak-traffic-defense.md": ("04", "正传", "正传 1"),
    "05-observability.md": ("05", "正传", "正传 2"),
    "06-security-architecture.md": ("06", "正传", "正传 3"),
    "07-from-chef-to-ceo.md": ("07", "终章", "终章"),
    "08-qa-testing-strategy.md": ("08", "正传", "正传 4"),
    "09-cicd-devops.md": ("09", "正传", "正传 5"),
    "10-api-design.md": ("10", "正传", "正传 6"),
    "11-ai-learning-paradox.md": ("11", "续集", "续集二"),
    "12-data-kitchen.md": ("12", "正传", "正传 7"),
    "13-frontend-renovation.md": ("13", "正传", "正传 8"),
    "14-cloud-finops.md": ("14", "番外", "番外二"),
    "15-incident-response.md": ("15", "正传", "正传 9"),
    "16-performance-optimization.md": ("16", "正传", "正传 10"),
    "18-distributed-puzzles.md": ("18", "正传", "正传 12"),
    "19-saas-multitenant.md": ("19", "番外", "番外三"),
    "20-realtime-eventdriven.md": ("20", "正传", "正传 11"),
    "21-multiplatform-architecture.md": ("21", "正传", "正传 13"),
    "22-search-recommendation.md": ("22", "番外", "番外四"),
    "24-database-migration.md": ("24", "正传", "正传 14"),
    "25-lowcode-platform.md": ("25", "番外", "番外五"),
    "26-globalization.md": ("26", "番外", "番外六"),
    "27-ai-org-transformation.md": ("27", "续集", "续集三"),
    "28-ai-native-startup.md": ("28", "续集", "续集四"),
    "29-self-evolving-company.md": ("29", "续集", "续集五"),
    "30-ai-hallucination-safety.md": ("30", "续集", "续集六"),
    "31-codebase-cognitive-debt.md": ("31", "续集", "续集七"),
    "32-agent-harness.md": ("32", "续集", "续集八"),
    "33-ai-fatal-trio.md": ("33", "续集", "续集九"),
    "34a-ai-evaluation-fundamentals.md": ("34a", "续集", "续集十（上）"),
    "34b-ai-evaluation-pipeline.md": ("34b", "续集", "续集十（下）"),
    "35a-mcp-protocol.md": ("35a", "续集", "续集十一（上）"),
    "35b-a2a-protocol.md": ("35b", "续集", "续集十一（下）"),
    "36a-ai-token-cost-structure.md": ("36a", "续集", "续集十二（上）"),
    "36b-ai-token-cost-optimization.md": ("36b", "续集", "续集十二（下）"),
    "37-ai-observability.md": ("37", "续集", "续集十三"),
    "38-rag-retrieval-augmented-generation.md": ("38", "续集", "续集十四"),
    "39-vector-database-and-embedding.md": ("39", "续集", "续集十五"),
    "40-ai-compliance-and-regulation.md": ("40", "续集", "续集十六"),
    "41-ai-private-deployment.md": ("41", "续集", "续集十七"),
    "42-prompt-engineering.md": ("42", "番外", "番外七"),
    "43-multimodal-ai.md": ("43", "番外", "番外八"),
    "44-ai-engineer-responsibility.md": ("44", "续集", "续集十八"),
    "45-ai-productivity-paradox.md": ("45", "续集", "续集十九"),
    "46-tech-debt-career-trap.md": ("46", "续集", "续集二十"),
}

# 主题受众映射（从 README "推荐阅读路线" 表推断）
AUDIENCE_BY_TOPIC = {
    "前传": "工程师 / 架构师",
    "续集": "AI 工程师 / 架构师",
    "终章": "CTO / 技术管理者",
    "番外": "PM / 创业者",
    "正传": "工程师 / SRE / 架构师",
}


def extract_title(text: str) -> str:
    """从 H1 提取标题（剥掉编号）。"""
    m = re.match(r"^# (\d+[a-c]?) · (.+)$", text, re.MULTILINE)
    if m:
        return m.group(2).strip()
    m = re.match(r"^# (.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def has_frontmatter(text: str) -> bool:
    return text.startswith("<!--\nstory:") or '<!--\nstory:' in text[:200]


def make_frontmatter(number: str, story_type: str, position: str,
                     title: str, audience: str) -> str:
    return (
        "<!--\n"
        "story:\n"
        f"  number: {number}\n"
        f"  type: {story_type}\n"
        f"  position: {position}\n"
        f"  title: {title}\n"
        f"  audience: {audience}\n"
        "-->\n\n"
    )


def process_file(path: Path) -> tuple[bool, str]:
    fname = path.name
    if fname not in META:
        return False, f"unknown file: {fname}"

    text = path.read_text(encoding="utf-8")
    if has_frontmatter(text):
        return False, "已有 frontmatter"

    number, story_type, position = META[fname]
    title = extract_title(text)
    audience = AUDIENCE_BY_TOPIC.get(story_type, "")

    fm = make_frontmatter(number, story_type, position, title, audience)
    new_text = fm + text
    path.write_text(new_text, encoding="utf-8")
    return True, f"{number} {title[:30]}: type={story_type}, pos={position}"


def main(limit: int | None = None) -> None:
    md_files = sorted(STORY.glob("[0-9]*.md"))
    if limit:
        md_files = md_files[:limit]

    changed = 0
    skipped = 0
    for f in md_files:
        ok, msg = process_file(f)
        if ok:
            changed += 1
            print(f"  [+] {msg}")
        else:
            skipped += 1
            print(f"  [.] {msg}")

    print(f"\n== Total {len(md_files)} files -> changed {changed} / skipped {skipped}")


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(limit)
