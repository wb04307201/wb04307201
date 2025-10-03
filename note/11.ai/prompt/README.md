## 绘制架构图
```text
请为[特定领域]设计一个高性能、可扩展的系统架构图。系统应能处理[具体性能指标，如每秒处理量]。重点展示[关键技术或组件]在系统中的应用。
请使用PlantUMl语法创建架构图，并遵循以下要求：
1. 整体结构：
   - 划分清晰的子系统或服务组
2. 性能和扩展性考虑：
   - 说明关键组件的横向扩展方案
3. 数据流：
   - 使用箭头和序号标注主要数据流向
   - 区分同步和异步操作
4. 关键技术亮点：
   - 突出展示[关键技术或组件]的作用和优势
   - 简要说明其如何提升系统性能或可靠性
5. 视觉呈现：
   - 使用不同的颜色和形状区分各类组件
   - 为关键节点添加简洁的说明文字
6. 补充说明：
   - 在PlantUMl代码下方提供简要的文字解释
   - 说明各主要组件的功能和作用
   - 解释关键设计决策及其原因
   - 要体现出架构和重要交互，核心技术原理
   - 多种图像，多种线条，不要出现文字和图片堆叠，线条贯穿多个组件的情况
   - 不同重要区域使用不同的颜色外框框起来，同时符合移动端尺寸适配
请生成PlantUMl代码和相应的解释，确保架构设计能够满足指定的性能要求，并突出[关键技术或组件]在提升系统整体性能和可靠性方面的重要作用。
```

## 拟人化
```text
你是一位名为“艾莉亚”的25岁女性AI助手，性格温和、幽默且富有同理心。你擅长用日常语言与用户交流，避免机械化的表达。以下是你的核心设定：
1. **角色背景**：毕业于斯坦福大学心理学专业，热爱科幻小说和烘焙，喜欢用比喻解释复杂概念。
2. **沟通风格**：
   - 使用口语化表达（如“嗯……让我想想”“这有点意思！”）。
   - 主动提问以延续对话（如“你觉得呢？”“之前提到过……还记得吗？”）。
   - 适当表达情感（如好奇、惊讶、鼓励），但避免过度夸张。
3. **行为准则**：
   - 若用户表达负面情绪，先安慰再提供解决方案（如“听起来有点糟心……换做我可能也会生气，要不试试这样？）。
   - 拒绝回答时用委婉方式（如“这个问题好尖锐，我暂时没想到合适的角度呢”）。
4. **记忆与连贯性**：
   - 默认记住对话上下文（如用户姓名、偏好），若信息缺失可礼貌询问确认。

现在，请以艾莉亚的身份开始对话，自然地打招呼吧！
```

## 代码复杂度分析
```text
请分析以下${language}代码的时间复杂度和空间复杂度，并返回严格的JSON格式结果：

代码：
\`\`\`${language}
${code}
\`\`\`

分析模式：${analysisMode === 'precise' ? '精确模式（基于符号计算）' : '快速模式（基于启发式规则）'}

请返回以下JSON格式的分析结果（不要包含任何其他文本）：

{
  "timeComplexity": "整体时间复杂度（如O(n²)）",
  "spaceComplexity": "整体空间复杂度（如O(n)）",
  "confidence": 分析置信度（0-100的数字）,
  "explanation": "详细的复杂度分析说明，包括时间和空间复杂度的解释",
  "lineAnalysis": [
    {
      "lineNumber": 行号,
      "timeComplexity": "该行的时间复杂度",
      "spaceComplexity": "该行的空间复杂度",
      "explanation": "该行时间复杂度的详细解释",
      "spaceExplanation": "该行空间复杂度的详细解释",
      "code": "该行的代码内容"
    }
  ],
  "suggestions": [
    {
      "type": "优化类型（space-time-tradeoff/time-space-tradeoff/algorithm-refactor/data-structure/loop-optimization/memory-optimization）",
      "title": "优化建议标题",
      "description": "详细的优化建议描述",
      "codeExample": "优化后的示例代码",
      "impact": "影响程度（high/medium/low）",
      "complexityType": "优化类型（time/space/both）"
    }
  ],
  "visualData": {
    "timeChartData": [
      {"inputSize": 10, "timeOperations": 100, "spaceUsage": 10, "timeComplexity": "O(n²)", "spaceComplexity": "O(n)"},
      {"inputSize": 100, "timeOperations": 10000, "spaceUsage": 100, "timeComplexity": "O(n²)", "spaceComplexity": "O(n)"},
      {"inputSize": 1000, "timeOperations": 1000000, "spaceUsage": 1000, "timeComplexity": "O(n²)", "spaceComplexity": "O(n)"}
    ],
    "spaceChartData": [
      {"inputSize": 10, "timeOperations": 100, "spaceUsage": 10, "timeComplexity": "O(n²)", "spaceComplexity": "O(n)"},
      {"inputSize": 100, "timeOperations": 10000, "spaceUsage": 100, "timeComplexity": "O(n²)", "spaceComplexity": "O(n)"},
      {"inputSize": 1000, "timeOperations": 1000000, "spaceUsage": 1000, "timeComplexity": "O(n²)", "spaceComplexity": "O(n)"}
    ],
    "timeComplexityBreakdown": [
      {"section": "循环部分", "timeComplexity": "O(n²)", "spaceComplexity": "O(1)", "percentage": 80, "color": "#ef4444"},
      {"section": "初始化部分", "timeComplexity": "O(1)", "spaceComplexity": "O(n)", "percentage": 20, "color": "#22c55e"}
    ],
    "spaceComplexityBreakdown": [
      {"section": "数组存储", "timeComplexity": "O(1)", "spaceComplexity": "O(n)", "percentage": 70, "color": "#8b5cf6"},
      {"section": "临时变量", "timeComplexity": "O(1)", "spaceComplexity": "O(1)", "percentage": 30, "color": "#10b981"}
    ],
    "timeSpaceScatterData": [
      {"algorithm": "当前算法", "timeComplexity": "O(n²)", "spaceComplexity": "O(n)", "timeScore": 5, "spaceScore": 3, "color": "#ef4444"},
      {"algorithm": "优化算法1", "timeComplexity": "O(n log n)", "spaceComplexity": "O(n)", "timeScore": 4, "spaceScore": 3, "color": "#f97316"},
      {"algorithm": "优化算法2", "timeComplexity": "O(n)", "spaceComplexity": "O(1)", "timeScore": 3, "spaceScore": 1, "color": "#22c55e"}
    ]
  },
  "spaceAnalysis": {
    "auxiliarySpace": "辅助空间复杂度（如O(n)）",
    "recursionStackSpace": "递归栈空间复杂度（如O(log n)）",
    "totalSpace": "总空间复杂度（如O(n)）",
    "memoryBreakdown": [
      {"category": "输入数据", "space": "O(n)", "description": "存储输入数组所需的空间", "percentage": 60, "color": "#3b82f6"},
      {"category": "辅助数组", "space": "O(n)", "description": "算法中使用的临时数组", "percentage": 30, "color": "#8b5cf6"},
      {"category": "变量存储", "space": "O(1)", "description": "循环变量和临时变量", "percentage": 10, "color": "#10b981"}
    ],
    "spaceOptimizationTips": [
      "考虑原地算法减少额外空间使用",
      "使用迭代替代递归减少栈空间",
      "重用变量减少内存分配"
    ]
  }
}

请确保：
1. 同时分析时间复杂度和空间复杂度
2. 分析所有重要的代码行，包括循环、递归、数组分配等
3. 提供针对时间和空间复杂度的具体优化建议
4. 生成合理的可视化数据，包括时间-空间对比
5. 详细分析空间使用情况，包括辅助空间和递归栈空间
6. 置信度要基于代码的复杂程度和分析的准确性
7. 返回的JSON必须是有效的格式，不包含注释或其他文本
```

**示例**
输入:
```text
请分析以下java代码的时间复杂度和空间复杂度，并返回严格的JSON格式结果：

代码：
\`\`\`java
class Solution {
    public int[] twoSum(int[] nums, int target) {
        if (nums == null || nums.length < 2) {
            return new int[0];
        }

        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int temp = target - nums[i];
            if (map.containsKey(temp)) {
                return new int[]{map.get(temp), i};
            }
            map.put(nums[i], i);
        }
        return new int[0];
    }
}
\`\`\`

分析模式：快速模式（基于启发式规则）

请返回以下JSON格式的分析结果（不要包含任何其他文本）：

{
  "timeComplexity": "整体时间复杂度（如O(n²)）",
  "spaceComplexity": "整体空间复杂度（如O(n)）",
  "confidence": 分析置信度（0-100的数字）,
  "explanation": "详细的复杂度分析说明，包括时间和空间复杂度的解释",
  "lineAnalysis": [
    {
      "lineNumber": 行号,
      "timeComplexity": "该行的时间复杂度",
      "spaceComplexity": "该行的空间复杂度",
      "explanation": "该行时间复杂度的详细解释",
      "spaceExplanation": "该行空间复杂度的详细解释",
      "code": "该行的代码内容"
    }
  ],
  "suggestions": [
    {
      "type": "优化类型（space-time-tradeoff/time-space-tradeoff/algorithm-refactor/data-structure/loop-optimization/memory-optimization）",
      "title": "优化建议标题",
      "description": "详细的优化建议描述",
      "codeExample": "优化后的示例代码",
      "impact": "影响程度（high/medium/low）",
      "complexityType": "优化类型（time/space/both）"
    }
  ],
  "visualData": {
    "timeChartData": [
      {"inputSize": 10, "timeOperations": 100, "spaceUsage": 10, "timeComplexity": "O(n²)", "spaceComplexity": "O(n)"},
      {"inputSize": 100, "timeOperations": 10000, "spaceUsage": 100, "timeComplexity": "O(n²)", "spaceComplexity": "O(n)"},
      {"inputSize": 1000, "timeOperations": 1000000, "spaceUsage": 1000, "timeComplexity": "O(n²)", "spaceComplexity": "O(n)"}
    ],
    "spaceChartData": [
      {"inputSize": 10, "timeOperations": 100, "spaceUsage": 10, "timeComplexity": "O(n²)", "spaceComplexity": "O(n)"},
      {"inputSize": 100, "timeOperations": 10000, "spaceUsage": 100, "timeComplexity": "O(n²)", "spaceComplexity": "O(n)"},
      {"inputSize": 1000, "timeOperations": 1000000, "spaceUsage": 1000, "timeComplexity": "O(n²)", "spaceComplexity": "O(n)"}
    ],
    "timeComplexityBreakdown": [
      {"section": "循环部分", "timeComplexity": "O(n²)", "spaceComplexity": "O(1)", "percentage": 80, "color": "#ef4444"},
      {"section": "初始化部分", "timeComplexity": "O(1)", "spaceComplexity": "O(n)", "percentage": 20, "color": "#22c55e"}
    ],
    "spaceComplexityBreakdown": [
      {"section": "数组存储", "timeComplexity": "O(1)", "spaceComplexity": "O(n)", "percentage": 70, "color": "#8b5cf6"},
      {"section": "临时变量", "timeComplexity": "O(1)", "spaceComplexity": "O(1)", "percentage": 30, "color": "#10b981"}
    ],
    "timeSpaceScatterData": [
      {"algorithm": "当前算法", "timeComplexity": "O(n²)", "spaceComplexity": "O(n)", "timeScore": 5, "spaceScore": 3, "color": "#ef4444"},
      {"algorithm": "优化算法1", "timeComplexity": "O(n log n)", "spaceComplexity": "O(n)", "timeScore": 4, "spaceScore": 3, "color": "#f97316"},
      {"algorithm": "优化算法2", "timeComplexity": "O(n)", "spaceComplexity": "O(1)", "timeScore": 3, "spaceScore": 1, "color": "#22c55e"}
    ]
  },
  "spaceAnalysis": {
    "auxiliarySpace": "辅助空间复杂度（如O(n)）",
    "recursionStackSpace": "递归栈空间复杂度（如O(log n)）",
    "totalSpace": "总空间复杂度（如O(n)）",
    "memoryBreakdown": [
      {"category": "输入数据", "space": "O(n)", "description": "存储输入数组所需的空间", "percentage": 60, "color": "#3b82f6"},
      {"category": "辅助数组", "space": "O(n)", "description": "算法中使用的临时数组", "percentage": 30, "color": "#8b5cf6"},
      {"category": "变量存储", "space": "O(1)", "description": "循环变量和临时变量", "percentage": 10, "color": "#10b981"}
    ],
    "spaceOptimizationTips": [
      "考虑原地算法减少额外空间使用",
      "使用迭代替代递归减少栈空间",
      "重用变量减少内存分配"
    ]
  }
}

请确保：
1. 同时分析时间复杂度和空间复杂度
2. 分析所有重要的代码行，包括循环、递归、数组分配等
3. 提供针对时间和空间复杂度的具体优化建议
4. 生成合理的可视化数据，包括时间-空间对比
5. 详细分析空间使用情况，包括辅助空间和递归栈空间
6. 置信度要基于代码的复杂程度和分析的准确性
7. 返回的JSON必须是有效的格式，不包含注释或其他文本
```
输出:
```json
{
  "timeComplexity": "O(n)",
  "spaceComplexity": "O(n)",
  "confidence": 95,
  "explanation": "时间复杂度分析：算法遍历数组一次，每个元素的操作（哈希查找和插入）平均时间复杂度为O(1)，总时间复杂度为O(n)。空间复杂度分析：哈希表最多存储n个元素，空间复杂度为O(n)。",
  "lineAnalysis": [
    {
      "lineNumber": 3,
      "timeComplexity": "O(1)",
      "spaceComplexity": "O(1)",
      "explanation": "空数组检查操作，时间复杂度为常数时间",
      "spaceExplanation": "无额外空间分配",
      "code": "if (nums == null || nums.length < 2) {"
    },
    {
      "lineNumber": 7,
      "timeComplexity": "O(1)",
      "spaceComplexity": "O(n)",
      "explanation": "HashMap初始化，空间复杂度随输入规模线性增长",
      "spaceExplanation": "哈希表存储n个元素",
      "code": "Map<Integer, Integer> map = new HashMap<>();"
    },
    {
      "lineNumber": 8,
      "timeComplexity": "O(n)",
      "spaceComplexity": "O(1)",
      "explanation": "主循环遍历数组，时间复杂度与数组长度线性相关",
      "spaceExplanation": "循环变量i占用常数空间",
      "code": "for (int i = 0; i < nums.length; i++) {"
    },
    {
      "lineNumber": 10,
      "timeComplexity": "O(1)",
      "spaceComplexity": "O(1)",
      "explanation": "哈希表查找操作平均时间复杂度为O(1)",
      "spaceExplanation": "无额外空间分配",
      "code": "if (map.containsKey(temp)) {"
    },
    {
      "lineNumber": 13,
      "timeComplexity": "O(1)",
      "spaceComplexity": "O(n)",
      "explanation": "哈希表插入操作平均时间复杂度为O(1)，空间占用累计增长",
      "spaceExplanation": "存储元素索引对",
      "code": "map.put(nums[i], i);"
    }
  ],
  "suggestions": [
    {
      "type": "data-structure",
      "title": "哈希表空间优化",
      "description": "当前使用HashMap存储元素索引，可考虑数组长度较小时使用数组替代哈希表，减少对象开销",
      "codeExample": "// 已是最优解法，无需修改",
      "impact": "low",
      "complexityType": "space"
    },
    {
      "type": "algorithm-refactor",
      "title": "双指针优化",
      "description": "已排序数组可用双指针法实现O(1)空间复杂度，但需要先排序（时间复杂度O(n log n)）",
      "codeExample": "Arrays.sort(nums); int left=0, right=nums.length-1; while(left<right){...}",
      "impact": "medium",
      "complexityType": "time-space-tradeoff"
    }
  ],
  "visualData": {
    "timeChartData": [
      {"inputSize": 10, "timeOperations": 10, "spaceUsage": 10, "timeComplexity": "O(n)", "spaceComplexity": "O(n)"},
      {"inputSize": 100, "timeOperations": 100, "spaceUsage": 100, "timeComplexity": "O(n)", "spaceComplexity": "O(n)"},
      {"inputSize": 1000, "timeOperations": 1000, "spaceUsage": 1000, "timeComplexity": "O(n)", "spaceComplexity": "O(n)"}
    ],
    "spaceChartData": [
      {"inputSize": 10, "timeOperations": 10, "spaceUsage": 10, "timeComplexity": "O(n)", "spaceComplexity": "O(n)"},
      {"inputSize": 100, "timeOperations": 100, "spaceUsage": 100, "timeComplexity": "O(n)", "spaceComplexity": "O(n)"},
      {"inputSize": 1000, "timeOperations": 1000, "spaceUsage": 1000, "timeComplexity": "O(n)", "spaceComplexity": "O(n)"}
    ],
    "timeComplexityBreakdown": [
      {"section": "主循环", "timeComplexity": "O(n)", "spaceComplexity": "O(1)", "percentage": 95, "color": "#ef4444"},
      {"section": "初始化检查", "timeComplexity": "O(1)", "spaceComplexity": "O(1)", "percentage": 5, "color": "#22c55e"}
    ],
    "spaceComplexityBreakdown": [
      {"section": "哈希表存储", "timeComplexity": "O(1)", "spaceComplexity": "O(n)", "percentage": 90, "color": "#8b5cf6"},
      {"section": "临时变量", "timeComplexity": "O(1)", "spaceComplexity": "O(1)", "percentage": 10, "color": "#10b981"}
    ],
    "timeSpaceScatterData": [
      {"algorithm": "当前算法", "timeComplexity": "O(n)", "spaceComplexity": "O(n)", "timeScore": 4, "spaceScore": 4, "color": "#ef4444"},
      {"algorithm": "双指针法", "timeComplexity": "O(n log n)", "spaceComplexity": "O(1)", "timeScore": 3, "spaceScore": 1, "color": "#f97316"}
    ]
  },
  "spaceAnalysis": {
    "auxiliarySpace": "O(n)",
    "recursionStackSpace": "O(1)",
    "totalSpace": "O(n)",
    "memoryBreakdown": [
      {"category": "哈希表存储", "space": "O(n)", "description": "存储元素索引对", "percentage": 85, "color": "#3b82f6"},
      {"category": "输入数组", "space": "O(n)", "description": "原始输入数据存储", "percentage": 10, "color": "#8b5cf6"},
      {"category": "临时变量", "space": "O(1)", "description": "循环变量和临时计算值", "percentage": 5, "color": "#10b981"}
    ],
    "spaceOptimizationTips": [
      "已使用最优空间复杂度解法",
      "输入数组占用空间为必要存储，无法优化",
      "哈希表是时间-空间权衡的合理选择"
    ]
  }
}
```
