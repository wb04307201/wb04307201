<!--
module:
  parent: high-performance
  slug: system-design/04-high-performance/sensitive-word-filter/anti-evasion
  type: deep-dive
  category: 敏感词过滤
  summary: 敏感词变体绕过对抗 —— 6 大绕过手法 + 归一化流水线 + Unicode/繁简/谐音/零宽字符处理 + AI 语义兜底
-->

# 敏感词变体绕过对抗（Anti-Evasion）

> **一句话答案**：纯 AC 自动机只能匹配"字面量"，用户一定会用**变体绕过**（谐音 / 拼音 / 繁简 / 形近 / 零宽字符 / 夹杂干扰符）。对抗核心 = **在进 AC 自动机之前，先跑一条归一化流水线（Normalization Pipeline）把变体还原成标准形**，纯词典拦不住的靠 **AI 语义审核兜底**。

← [返回: sensitive-word-filter 总目录](README.md) · 上一章：[04-selection-decision-tree](04-selection-decision-tree.md)

---

## 0. 为什么 AC 自动机不够

前四章的 AC 自动机解决了"**怎么快**"（O(n) 单次扫描 10 万词典毫秒级），但没解决"**怎么准**"。真实业务里，用户是**对抗性输入**：

```text
敏感词词典里有：违禁品

用户实际发出：
- "违 禁 品"        ← 夹杂空格
- "违*禁*品"        ← 夹杂标点
- "wéijìnpǐn"       ← 拼音
- "違禁品"           ← 繁体
- "违​禁品"    ← 零宽空格（肉眼看不见）
- "韦禁品" / "喂禁品" ← 谐音

AC 自动机全部漏检 —— 因为它们在"字面上"都不是"违禁品"。
```

**核心认知**：敏感词过滤是**攻防对抗**，不是一次性工程。词典匹配是"守"，用户变体是"攻"，中间必须夹一层**归一化**把攻击面收敛。

---

## 1. 6 大绕过手法与对抗策略

| # | 绕过手法 | 例子 | 对抗策略 |
|---|---------|------|---------|
| 1 | **夹杂干扰符** | `违 禁 品` / `违.禁.品` | 去噪：剥离空格/标点/特殊符号 |
| 2 | **谐音 / 拼音** | `wéijìnpǐn` / `韦禁品` | 拼音归一 + 音近词典 |
| 3 | **繁简 / 异体字** | `違禁品` / `違禁品` | OpenCC 繁转简 |
| 4 | **形近字 / 拆字** | `氵去某某` / 部件替换 | 形近字映射表 |
| 5 | **零宽 / Unicode 变体** | `违​禁品` / 全角 | NFKC 归一 + 剥零宽 |
| 6 | **大小写 / 全半角混淆** | `Ｆｕｃｋ` / `FuCk` | 全角转半角 + 小写 |

> 记忆：**干扰、谐音、繁简、形近、零宽、大小写**——6 类归一化，前进 AC 自动机前一次性抹平。

---

## 2. 归一化流水线（核心）

对抗的正确架构不是"改 AC 自动机"，而是在它**前面**加一条预处理流水线，把任意变体收敛成标准形，再喂给已有的高性能引擎：

```
原始文本
  ↓ ① 全角 → 半角（ＡＢＣ → ABC）
  ↓ ② 转小写（FUCK → fuck）
  ↓ ③ Unicode NFKC 归一（兼容等价字符合并）
  ↓ ④ 剥离零宽字符（U+200B/200C/200D/FEFF）
  ↓ ⑤ 繁 → 简（OpenCC：違 → 违）
  ↓ ⑥ 去干扰符（保留字母/数字/汉字，删空格标点）
  ↓ ⑦（可选）谐音 → 拼音归一
标准文本 → AC 自动机匹配（复用前 4 章引擎）
```

**关键点**：流水线是**幂等的纯函数**，可在 AC 自动机之前无状态执行，不影响原有 O(n) 性能（预处理本身也是 O(n)）。

---

## 3. Java 实现

```java
public class TextNormalizer {

    // 零宽字符集合
    private static final Pattern ZERO_WIDTH =
        Pattern.compile("[\\u200B\\u200C\\u200D\\uFEFF]");
    // 干扰符：非字母/数字/汉字
    private static final Pattern NOISE =
        Pattern.compile("[^\\p{IsHan}a-z0-9]");

    /** 归一化流水线：任意变体 → 标准形 */
    public String normalize(String raw) {
        String s = ToDBC(raw);                       // ① 全角→半角
        s = s.toLowerCase();                         // ② 小写
        s = Normalizer.normalize(s, Normalizer.Form.NFKC); // ③ Unicode 归一
        s = ZERO_WIDTH.matcher(s).replaceAll("");    // ④ 剥零宽
        s = ZhConverterUtil.toSimple(s);             // ⑤ 繁→简（OpenCC/HanLP）
        s = NOISE.matcher(s).replaceAll("");         // ⑥ 去干扰符
        return s;
    }

    /** 全角转半角 */
    private String ToDBC(String s) {
        char[] c = s.toCharArray();
        for (int i = 0; i < c.length; i++) {
            if (c[i] == '　') c[i] = ' ';
            else if (c[i] > '＀' && c[i] < '｟') c[i] -= 65248;
        }
        return new String(c);
    }
}

// 使用：先归一化，再复用原 AC 自动机引擎
String clean = normalizer.normalize(userInput);
FilterResult result = sensitiveFilter.filter(clean);
```

> ⚠️ **命中位置回映射**：归一化会改变字符下标。若需要"把原文里的敏感词打码"，要维护 `归一化后下标 → 原文下标` 的映射，否则打码位置会错位。评论场景常用简化方案：命中即整段拦截，不做精确打码。

---

## 4. 对抗升级战：词典打不过怎么办

变体是**无限的**（用户能持续造新谐音/新拆字），纯归一化 + 词典会陷入"打地鼠"。分层兜底：

| 层 | 手段 | 拦什么 | 成本 |
|----|------|--------|------|
| L1 | 归一化 + AC 自动机 | 已知词 + 常规变体 | 极低（毫秒） |
| L2 | 谐音/形近扩展词典 | 高频变体 | 低（离线扩词） |
| L3 | **AI 语义审核** | 未知变体 + 上下文语义 | 高（100ms+，仅兜底） |

**L3 的定位**：不是替代词典，而是**对 L1/L2 漏网的、疑似但不确定的内容做异步二审**。详见 [11.ai/07-llmops/05-llm-security](../../../11.ai/07-llmops/05-llm-security/README.md) 的内容审核部分。

---

## 5. 权衡：归一化的反噬

归一化越激进，**误杀率（false positive）越高**：

- 去掉所有标点后，正常文本 `他今天很菜，输了比赛` 里的分词可能拼出敏感词
- 繁简 + 谐音归一后，正常词被误判为敏感词的变体
- **原则**：归一化强度分场景——弹幕/评论可激进（宁可错杀），商品标题/正式文案要保守（避免误伤商家）

> 一句话：**anti-evasion 是准确率与误杀率的平衡艺术**，不是"归一化越多越好"。

---

## 6. 相关章节

- 上一章：[04-selection-decision-tree](04-selection-decision-tree.md) —— 5 维选型矩阵
- 专题首页：[sensitive-word-filter 总目录](README.md) —— AC 自动机 + Bloom + 分布式全景
- 算法基础：[string-algorithms/AC 自动机](../../../../02.computer-basics/02-algorithms/string-algorithms/03-ac-automaton.md) —— 归一化后喂给的匹配引擎
- AI 兜底：[11.ai/07-llmops/05-llm-security](../../../11.ai/07-llmops/05-llm-security/README.md) —— LLM 内容审核（L3 语义兜底）
- 面试题：[13.split-hairs/02.computer-basics/sensitive-word-filter](../../../13.split-hairs/02.computer-basics/sensitive-word-filter/README.md) —— 变体绕过精选 Q&A

---

> **变体绕过对抗 = 归一化流水线（全半角/小写/NFKC/零宽/繁简/去噪）把攻击面收敛 + AC 自动机复用 + AI 语义兜底。核心权衡是准确率 vs 误杀率，纯词典打不过无限变体。**

---

← [返回: sensitive-word-filter 总目录](README.md) · 上一章：[04-selection-decision-tree](04-selection-decision-tree.md) · 专题结束
