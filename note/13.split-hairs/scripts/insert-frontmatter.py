#!/usr/bin/env python3
"""
批量给 note/13.split-hairs/**/*.md 插入 frontmatter。

frontmatter 模板（HTML 注释形式，可被 Markdown 渲染忽略，但能被脚本读取）：

    <!--
    question:
      id: <topic_dir>-<leaf_dir>       e.g. 01.java-hashmap-resizing
      topic: <01.java|03.database|...>  从路径第 2 段推断
      difficulty: <⭐ 估计>             ⭐ / ⭐⭐ / ⭐⭐⭐ / ⭐⭐⭐⭐ / ⭐⭐⭐⭐⭐
      frequency: <高频|中频|低频>        从 README 的"速查表"提示自动提取，未匹配时为"中频"
      scenario_type: <4 类之一>         从 ## 引子 + 引子内关键字启发式判断：
        - "alert / 告警 / OOM / 崩溃" → 生产 Bug
        - "== / 反射 / 神秘代码 / 反直觉" → 反直觉代码
        - "选型 / 决策 / 选 / 怎么办" → 架构困境
        - "20 倍 / 性能 / 慢 / 优化" → 性能对比
        默认 "反直觉代码"
      tags: [<topic>, <关键词>]         topic 默认 + 从文件名与章节标题提取 1-3 个
    -->

依据规范：note/13.split-hairs/QUESTION-FORMAT-SPEC.md §5
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPLIT_HAIRS = ROOT

# topic 推断：从路径第 2 段（13.split-hairs/<topic>/<id>/README.md）
TOPIC_KEYS = ["01.java", "03.database", "04.system-design",
              "06.spring", "09.front-end", "11.ai"]


def parse_topic(path: Path) -> str:
    """从相对 split-hairs 的路径推断 topic。"""
    rel = path.relative_to(SPLIT_HAIRS)
    parts = rel.parts  # e.g. ('01.java', 'hashmap-resizing', 'README.md')
    for cand in parts:
        if cand in TOPIC_KEYS:
            return cand
    return "unknown"


def infer_difficulty(text: str) -> str:
    """从 H1 的'⭐'或文本中提取难度。"""
    # 抓 ⭐⭐⭐⭐ 的形式
    m = re.search(r"⭐{1,5}", text)
    if m:
        return m.group()
    # 文末标注格式 '· ⭐⭐' 同样可以
    return "未标"


def infer_frequency(text: str) -> str:
    """启发式：文档开头提到 '高频' / '中频' / '低频'。"""
    head = text[:500]
    for kw in ("高频", "中频", "低频"):
        if kw in head:
            return kw
    return "中频"  # 默认


def infer_scenario(text: str) -> str:
    """从 ## 引子 一段启发式判断场景类型。"""
    # 找 ## 引子 一段的内容
    m = re.search(r"## 引子：[^\n]*\n([\s\S]*?)\n##\s", text)
    snip = m.group(1) if m else text[:500]
    if any(k in snip for k in ("告警", "凌晨", "崩溃", "OOM", "上线", "事故")):
        return "生产 Bug"
    if any(k in snip for k in ("==", "反射", "反直觉", "诡异", "看不出", "没搞懂", "困惑")):
        return "反直觉代码"
    if any(k in snip for k in ("选型", "决策", "选哪个", "怎么办", "工程师选", "架构")):
        return "架构困境"
    if any(k in snip for k in ("20 倍", "10 倍", "性能", "慢", "快", "对比", "差距", "省钱")):
        return "性能对比"
    # 默认
    return "反直觉代码"


def infer_tags(path: Path, topic: str, text: str) -> list[str]:
    """基于 topic + 文件名 + H1 标题生成 2-4 个 tag。"""
    tags = [topic]
    # 从 H1 提取主关键词
    m = re.match(r"# (.+)", text)
    if m:
        title = m.group(1)
        # 简单规则
        for kw in ("HashMap", "ThreadLocal", "Spring", "Bean", "AOP",
                   "MVCC", "Redis", "MySQL", "SQL", "HTTP", "CORS",
                   "XSS", "CSRF", "Vue", "React", "Domain", "JVM",
                   "Transformer", "LLM", "RAG", "Prompt", "Context",
                   "Harness", "Loop", "Function Calling", "Agent"):
            if kw in title and kw not in tags:
                tags.append(kw)
                break
    # 从文件名推断
    stem = path.parent.name
    for kw in stem.split("-"):
        if kw and len(kw) >= 3 and kw.isalpha() and kw not in tags:
            tags.append(kw)
            if len(tags) >= 3:
                break
    return tags


def make_frontmatter(file_id: str, topic: str, difficulty: str,
                     frequency: str, scenario_type: str,
                     tags: list[str]) -> str:
    """生成 HTML 注释形式的前置元数据。"""
    tags_str = ", ".join(tags)
    return (
        "<!--\n"
        "question:\n"
        f"  id: {file_id}\n"
        f"  topic: {topic}\n"
        f"  difficulty: {difficulty}\n"
        f"  frequency: {frequency}\n"
        f"  scenario_type: {scenario_type}\n"
        f"  tags: [{tags_str}]\n"
        "-->\n\n"
    )


def has_frontmatter(text: str) -> bool:
    """判断是否已有 frontmatter 注释。"""
    return text.startswith("<!--\nquestion:") or text.startswith("<!--question:") \
           or '<!--\nquestion:' in text[:200]


def process_file(path: Path) -> tuple[bool, str]:
    """单文件处理：(是否变更, 改动理由)。"""
    rel = path.relative_to(SPLIT_HAIRS)
    if rel.parts[0] not in TOPIC_KEYS:
        return False, "skip non-topic"

    text = path.read_text(encoding="utf-8")
    if has_frontmatter(text):
        return False, "已有 frontmatter，跳过"

    topic = parse_topic(path)
    leaf = path.parent.name
    file_id = f"{topic}-{leaf}"

    difficulty = infer_difficulty(text)
    frequency = infer_frequency(text)
    scenario_type = infer_scenario(text)
    tags = infer_tags(path, topic, text)

    fm = make_frontmatter(file_id, topic, difficulty, frequency, scenario_type, tags)
    # 插入到文件最开头（保证 frontmatter 在 H1 之前）
    new_text = fm + text
    path.write_text(new_text, encoding="utf-8")
    return True, f"{topic}/{leaf}: difficulty={difficulty}, freq={frequency}, scenario={scenario_type}"


def main(limit: int | None = None) -> None:
    """入口。`limit` 为 None 表示全量；为整数则只跑前 N 个文件（dry run / 测试用）。"""
    md_files = sorted(SPLIT_HAIRS.glob("*/**/README.md"))
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
            if msg != "skip non-topic":
                print(f"  [.] {msg} ({f.relative_to(SPLIT_HAIRS)})")

    print(f"\n== Total {len(md_files)} files -> changed {changed} / skipped {skipped}")


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(limit)
