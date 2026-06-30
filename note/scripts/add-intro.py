#!/usr/bin/env python3
"""
批量给 note/01-11 主模块的子 README 加 ## 引言（场景段）。

策略：
  - 从 README 提取 H1 + L1-L5 的简介
  - 推断场景类型（基于关键字 / 文件路径）
  - 生成 150-200 字的"## 引言"段并插入
  - 在段末加 [AUTO] 标记，便于后续人工 review

依据：CONTRIBUTING §11 推荐项 7（"## 学习路径" / 一句话定位）
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

NOTE = Path("note")

TOPIC_KEYS = (
    "01.java", "02.computer-basics", "03.database", "04.system-design",
    "05.tools", "06.spring", "07.workflow", "08.application-systems",
    "09.front-end", "10.big-data", "11.ai",
)
EXCLUDE = {"12.story", "13.split-hairs", "14.project-management"}


def detect_title(text: str) -> str:
    m = re.match(r"^# (.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def detect_intent(text: str, leaf_name: str) -> str:
    """根据标题 + 文件路径推断可能场景类型。"""
    title = detect_title(text)
    blob = (title + " " + leaf_name).lower()
    if any(k in blob for k in ("对比", "vs", "差异", "区别")):
        return "反直觉代码"
    if any(k in blob for k in ("性能", "调优", "优化", "gc", "jvm", "吞吐量")):
        return "性能对比"
    if any(k in blob for k in ("安全", "鉴权", "权限", "敏感", "加密", "csrf", "xss")):
        return "生产 Bug"
    if any(k in blob for k in ("架构", "模式", "选型", "演进", "演化")):
        return "架构困境"
    if any(k in blob for k in ("流程", "编排", "事件", "异步")):
        return "架构困境"
    return "反直觉代码"


def extract_topic_summary(text: str, max_chars: int = 120) -> str:
    """从 H1 后提取一段简介，取首段。"""
    lines = text.split("\n")
    in_body = False
    for line in lines:
        if line.startswith("# "):
            in_body = True
            continue
        if not in_body:
            continue
        s = line.strip()
        if s.startswith(">"):
            s = s.lstrip(">").strip()
        if not s or s.startswith("#"):
            continue
        if len(s) > max_chars:
            s = s[:max_chars].rstrip() + "..."
        return s
    return ""


def has_intro(text: str) -> bool:
    return bool(re.search(r"^## 引言[：:]", text, re.MULTILINE))


def has_auto_intro(text: str) -> bool:
    return "[AUTO]" in text and "## 引言" in text


def build_intro(title: str, leaf_name: str, summary: str,
                scene_type: str) -> str:
    """生成 150-200 字的 ## 引言 段（标 [AUTO] 待人工 review）。"""
    title_clean = title.strip().rstrip("：:") or leaf_name
    summary_clean = summary.strip().rstrip("。.") or "（暂无简介）"

    prompts = {
        "反直觉代码": (
            "{title} 本应该很简单，{summary_clean}\n\n"
            "**但实际**：面试/生产中常被问起或踩坑的是——\n"
            "代码看着对、跑起来对，但仔细一问深一层就漏馅。"
            "本篇就从'反直觉'这个角度切入，把踩坑点和根因摆出来。"
        ),
        "性能对比": (
            "{title} 的{summary_clean}\n\n"
            "**但实际**：常被问起'为什么我的版本慢 10 倍'、'怎么排查'。"
            "本篇用'对比数字'切入，把'常见 vs 极端'两种场景拆给你看。"
        ),
        "生产 Bug": (
            "{title} 的{summary_clean}\n\n"
            "**但实际**：常被攻击或出 Bug 后背锅。本篇用'生产场景'切入：\n"
            "线上怎么炸、有没有上线过的坑、为什么按官方文档写也会错。"
        ),
        "架构困境": (
            "{title} 的{summary_clean}\n\n"
            "**但实际**：常被问起'这种方案我怎么选'/'大厂怎么做'。"
            "本篇用'决策困境'切入，比较几种主流路径并讲清取舍。"
        ),
    }
    body = prompts.get(scene_type, prompts["反直觉代码"])
    body = body.format(title=title_clean, summary_clean=summary_clean)

    # 标题稍短，主标题稍短
    out = "## 引言：" + scene_type + "（[AUTO] 自动生成，待人工 review）\n\n"
    out += body + "\n\n"
    out += "> 📌 本段由 `note/scripts/add-intro.py` 自动生成（场景模板 + README 摘录）。"
    out += "**下次 review 时请改为真实场景 + 数字 + 反思**，目前仅满足'有引言'的最低要求。\n\n"
    out += "---\n\n"

    return out


def process_file(path: Path) -> tuple[bool, str]:
    """判断 path 是否为子 README：note/<topic>/<subdir>/README.md 格式。"""
    rel = path.relative_to(NOTE)
    if rel.parts[0] in EXCLUDE:
        return False, "skip excluded topic"
    if rel.parts[0] not in TOPIC_KEYS:
        return False, "skip not topic"
    # 跳过 01.java/README.md 这样的入口文件（parts 长度 < 3）
    if len(rel.parts) < 3:
        return False, "skip entry readme"
    text = path.read_text(encoding="utf-8", errors="replace")
    if has_intro(text):
        return False, "already has intro"

    title = detect_title(text)
    leaf_name = path.parent.name
    summary = extract_topic_summary(text)
    scene = detect_intent(text, leaf_name)
    intro_block = build_intro(title, leaf_name, summary, scene)

    # 插入位置：在 H1 + 第一个分隔 --- 之后插入
    lines = text.split("\n")
    insert_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "---" and i > 0 and lines[i-1].strip() == "":
            insert_idx = i + 1
            break
    if insert_idx is None:
        # 默认在 H1 后插入
        for i, line in enumerate(lines):
            if line.startswith("# "):
                insert_idx = i + 2
                break
    if insert_idx is None:
        return False, "no anchor"

    lines.insert(insert_idx, intro_block)
    new_text = "\n".join(lines)
    path.write_text(new_text, encoding="utf-8")
    return True, f"{leaf_name}/{path.name}: scene={scene}"


def main(only_topic: str | None = None) -> None:
    targets = [NOTE / t for t in TOPIC_KEYS if not only_topic or t == only_topic]
    changed = 0
    skipped = 0
    for t in targets:
        if not t.exists():
            continue
        # 匹配所有中间层 README：note/<topic>/<sub>/<sub2>/README.md
        # 至少 depth=3（即 topic 之下一级），跳过 entry README
        for f in sorted(t.glob("**/*/README.md")):
            rel = f.relative_to(NOTE)
            # 跳过 entry README（rel 长度 < 3，如 note/01.java/README.md）
            if len(rel.parts) < 3:
                continue
            ok, msg = process_file(f)
            if ok:
                changed += 1
                # 只显示前 5 个作 preview，避免刷屏
                if changed <= 5 or only_topic:
                    print(f"  [+] {msg}")
            else:
                skipped += 1

    print(f"\n== changed {changed} / skipped {skipped}")


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    main(only)
