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

## 代码时间复杂度分析
```text
你是一个专业的代码时间复杂度分析专家。请严格按照JSON格式返回分析结果，不要包含任何其他文本。

请分析以下${language}代码的时间复杂度，并返回严格的JSON格式结果：

代码：
\`\`\`${language}
${code}
\`\`\`

分析模式：${analysisMode === 'precise' ? '精确模式（基于符号计算）' : '快速模式（基于启发式规则）'}

请返回以下JSON格式的分析结果（不要包含任何其他文本）：

{
  "overallComplexity": "整体时间复杂度（如O(n²)）",
  "confidence": 分析置信度（0-100的数字）,
  "explanation": "详细的复杂度分析说明",
  "lineAnalysis": [
    {
      "lineNumber": 行号,
      "complexity": "该行的时间复杂度",
      "explanation": "该行复杂度的详细解释",
      "code": "该行的代码内容"
    }
  ],
  "suggestions": [
    {
      "type": "优化类型（space-time-tradeoff/algorithm-refactor/data-structure/loop-optimization）",
      "title": "优化建议标题",
      "description": "详细的优化建议描述",
      "codeExample": "优化后的示例代码",
      "impact": "影响程度（high/medium/low）"
    }
  ],
  "visualData": {
    "chartData": [
      {"inputSize": 10, "operations": 100, "complexity": "O(n²)"},
      {"inputSize": 100, "operations": 10000, "complexity": "O(n²)"},
      {"inputSize": 1000, "operations": 1000000, "complexity": "O(n²)"}
    ],
    "complexityBreakdown": [
      {"section": "循环部分", "complexity": "O(n²)", "percentage": 80, "color": "#ef4444"},
      {"section": "初始化部分", "complexity": "O(1)", "percentage": 20, "color": "#22c55e"}
    ]
  }
}

请确保：
1. 分析所有重要的代码行，特别是循环、递归和函数调用
2. 提供具体的优化建议和示例代码
3. 生成合理的可视化数据
4. 置信度要基于代码的复杂程度和分析的准确性
5. 返回的JSON必须是有效的格式，不包含注释或其他文本
```

**实际运行**
输入:
```text
你是一个专业的代码时间复杂度分析专家。请严格按照JSON格式返回分析结果，不要包含任何其他文本。

请分析以下java代码的时间复杂度，并返回严格的JSON格式结果：

代码：
\`\`\`java
public class Example {
    public static int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n-1) + fibonacci(n-2);
    }
    
    public static void bubbleSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n-1; i++) {
            for (int j = 0; j < n-i-1; j++) {
                if (arr[j] > arr[j+1]) {
                    int temp = arr[j];
                    arr[j] = arr[j+1];
                    arr[j+1] = temp;
                }
            }
        }
    }
}
\`\`\`

分析模式：快速模式（基于启发式规则）

请返回以下JSON格式的分析结果（不要包含任何其他文本）：

{
  "overallComplexity": "整体时间复杂度（如O(n²)）",
  "confidence": 分析置信度（0-100的数字）,
  "explanation": "详细的复杂度分析说明",
  "lineAnalysis": [
    {
      "lineNumber": 行号,
      "complexity": "该行的时间复杂度",
      "explanation": "该行复杂度的详细解释",
      "code": "该行的代码内容"
    }
  ],
  "suggestions": [
    {
      "type": "优化类型（space-time-tradeoff/algorithm-refactor/data-structure/loop-optimization）",
      "title": "优化建议标题",
      "description": "详细的优化建议描述",
      "codeExample": "优化后的示例代码",
      "impact": "影响程度（high/medium/low）"
    }
  ],
  "visualData": {
    "chartData": [
      {"inputSize": 10, "operations": 100, "complexity": "O(n²)"},
      {"inputSize": 100, "operations": 10000, "complexity": "O(n²)"},
      {"inputSize": 1000, "operations": 1000000, "complexity": "O(n²)"}
    ],
    "complexityBreakdown": [
      {"section": "循环部分", "complexity": "O(n²)", "percentage": 80, "color": "#ef4444"},
      {"section": "初始化部分", "complexity": "O(1)", "percentage": 20, "color": "#22c55e"}
    ]
  }
}

请确保：
1. 分析所有重要的代码行，特别是循环、递归和函数调用
2. 提供具体的优化建议和示例代码
3. 生成合理的可视化数据
4. 置信度要基于代码的复杂程度和分析的准确性
5. 返回的JSON必须是有效的格式，不包含注释或其他文本
```
输出:
```json
{
  "overallComplexity": "O(2^n + n²)",
  "confidence": 95,
  "explanation": "fibonacci方法采用递归实现，时间复杂度为O(2^n)；bubbleSort采用双重循环实现，时间复杂度为O(n²)。整体复杂度由最高阶项主导。",
  "lineAnalysis": [
    {
      "lineNumber": 3,
      "complexity": "O(1)",
      "explanation": "基础条件判断，执行次数为常数",
      "code": "if (n <= 1) return n;"
    },
    {
      "lineNumber": 4,
      "complexity": "O(2^n)",
      "explanation": "递归调用树深度为n，每层产生两个子调用",
      "code": "return fibonacci(n-1) + fibonacci(n-2);"
    },
    {
      "lineNumber": 8,
      "complexity": "O(n)",
      "explanation": "外层循环执行n-1次",
      "code": "for (int i = 0; i < n-1; i++) {"
    },
    {
      "lineNumber": 9,
      "complexity": "O(n²)",
      "explanation": "内层循环执行次数随i递减，总次数约为n²/2",
      "code": "for (int j = 0; j < n-i-1; j++) {"
    }
  ],
  "suggestions": [
    {
      "type": "algorithm-refactor",
      "title": "斐波那契数列迭代实现",
      "description": "使用循环替代递归，将时间复杂度优化至O(n)",
      "codeExample": "public static int fibonacci(int n) {\n    int a = 0, b = 1;\n    for (int i = 0; i < n; i++) {\n        int next = a + b;\n        a = b;\n        b = next;\n    }\n    return a;\n}",
      "impact": "high"
    },
    {
      "type": "loop-optimization",
      "title": "冒泡排序提前终止",
      "description": "添加交换标志位，若某轮未发生交换则提前结束排序",
      "codeExample": "boolean swapped;\nfor (int i = 0; i < n-1; i++) {\n    swapped = false;\n    for (int j = 0; j < n-i-1; j++) {\n        if (arr[j] > arr[j+1]) {\n            swap(arr, j, j+1);\n            swapped = true;\n        }\n    }\n    if (!swapped) break;\n}",
      "impact": "medium"
    }
  ],
  "visualData": {
    "chartData": [
      {"inputSize": 10, "operations": 1023, "complexity": "O(2^n)"},
      {"inputSize": 20, "operations": 21891, "complexity": "O(2^n)"},
      {"inputSize": 10, "operations": 45, "complexity": "O(n²)"},
      {"inputSize": 100, "operations": 4950, "complexity": "O(n²)"}
    ],
    "complexityBreakdown": [
      {"section": "斐波那契递归", "complexity": "O(2^n)", "percentage": 85, "color": "#ef4444"},
      {"section": "冒泡排序循环", "complexity": "O(n²)", "percentage": 15, "color": "#22c55e"}
    ]
  }
}
```
