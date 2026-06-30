#!/usr/bin/env python3
"""
给 7.workflow 下 9 张 PNG 引用各加 [AUTO] Mermaid 占位描述。

策略：
- 保留 PNG 引用（不删图 —— 截图难重做）
- 在每张图下加一段 mermaid ``` 块作为占位（[AUTO] 标记 + 简短描述）
- 描述从上下文自动生成（图前一行 + 文件名关键字）

依据：CONTRIBUTING §5 PNG → Mermaid 迁移清单（批 N-C3 已盘点）
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# 9 张 PNG 各自的位置 + 推断的描述
TARGETS = {
    "07.workflow/process-engine/camunda/camunda-7/README.md": [
        ("img.png", "Camunda 7 启动控制台（localhost:8080）— 嵌入式 Web 界面；管理流程定义、用户任务、流程实例等"),
        ("img_1.png", "Camunda 7 Swagger UI（localhost:8080/swaggerui）— REST API 文档；测试 ProcessEngine 服务"),
        ("img_2.png", "mvn install 后启动 SpringBoot 集成 Camunda 7 项目 — 项目启动成功的控制台输出"),
        ("img_3.png", "BPMN 流程图示例 — User/Service/Manual 等任务节点；Camunda 7 核心可建模资产"),
    ],
    "07.workflow/process-engine/camunda/camunda-8/README.md": [
        ("img_5.png", "Camunda Platform 8 开源架构（Self-Managed）— Zeebe + Operate + Tasklist + Optimize 4 大组件"),
        ("img_4.png", "免费使用 Camunda 8 源码构建生产环境路径 — 全开源无商业许可费的部署拓扑"),
    ],
    "07.workflow/apache-eventmesh/cloud-flow/README.md": [
        ("img.png", "EventMesh 云流程架构 — EventMesh + Serverless Workflow 集成（参考表格标题）"),
        ("img_1.png", "事件网格与业务流程集成 — EventMesh 作为事件中间件驱动 Serverless Workflow 流程编排"),
        ("img_2.png", "Serverless Workflow DSL 执行流程 — YAML DSL 解析为可执行流程图（参考表格标题）"),
    ],
}


def gen_mermaid_block(image_name: str, description: str) -> str:
    """基于描述生成 Mermaid 占位（先用 flowchart 通用模板）。"""
    return (
        f"\n```mermaid\n"
        f"%% [AUTO] 占位 — 描述：{description}\n"
        f"%% 实际图：{image_name}（保留 PNG 用于参考）\n"
        f"graph TB\n"
        f"    %% TODO: 人工设计等价 Mermaid 替换\n"
        f"    A[Component A] --> B[Component B]\n"
        f"    B --> C[Component C]\n"
        f"```\n"
    )


def process_file(path: Path, images: list) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    changed = False
    for image_name, description in images:
        # 模式 A：markdown 图片语法 ![name](name) 后跟换行
        pat_img = re.compile(
            r"(!\[" + re.escape(image_name) + r"\]\(" + re.escape(image_name) + r"\))(\n)"
        )
        new_text, n = pat_img.subn(
            r"\1\2" + gen_mermaid_block(image_name, description).rstrip("\n") + r"\2",
            text,
        )
        if n > 0:
            text = new_text
            changed = True
        else:
            # 模式 B：表格行中的 [name](name) — 在表格行后追加 mermaid
            pat_link = re.compile(
                r"(\|.*\[" + re.escape(image_name) + r"\]\(" + re.escape(image_name) + r"\).*\|)(\n)"
            )
            new_text2, n2 = pat_link.subn(
                r"\1\2" + gen_mermaid_block(image_name, description).rstrip("\n") + r"\2",
                text,
            )
            if n2 > 0:
                text = new_text2
                changed = True
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed, str(path.relative_to(Path("note")))


def main() -> None:
    NOTE = Path("note")
    for rel, images in TARGETS.items():
        path = NOTE / rel
        if not path.exists():
            print(f"  [.] SKIP missing: {rel}")
            continue
        ok, msg = process_file(path, images)
        if ok:
            print(f"  [+] {msg}: {len(images)} images processed")
        else:
            print(f"  [.] NO CHANGE: {msg}")


if __name__ == "__main__":
    main()
