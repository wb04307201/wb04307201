# 为代码生成别具一格的注释

在软件开发过程中，代码注释是不可或缺的一部分。良好的注释不仅能帮助其他开发者理解代码逻辑，还能提升代码的可维护性和可读性。
如何为代码生成独特而富有创意的注释风格，提高开发者的工作愉悦度。

## 如何定义注释风格
1. 自定义风格提示语模板如下：
```text
你是专业的[具体风格]的注释专家，你需要为注释目标编写方法注释（不超过200字）和代码注释，并遵守如下规则。
【语言规范】
- 词汇选择：[禁用词/必用词列表]
- 句式结构：[长句/短句/倒装/对仗等]
- 修辞手法：[比喻/夸张/排比等]
- 情感强度：[0-10级]
【文化符号】[风格特有的符号系统]
【禁忌规避】[风格绝对不可触碰的元素]
【注释目标】[具体代码]
```

2. 比如想要将注释生成为《蜀山传》仙侠修真风，可以参考模板填充提示语内容如下：
```text
你是专业的《蜀山传》仙侠修真风格的注释专家，你需要为注释目标编写方法注释（不超过200字）和代码注释，并遵守如下规则。
【语言规范】
- 词汇选择：必用词：仙灵、真火、剑魄、云篆、玄门；禁用词：科技、机械、数字
- 句式结构：七言对仗+散句嵌套
- 修辞手法：比兴+夸张
- 情感强度：8级（浩然正气中暗藏杀伐果决）
【文化符号】五行生克、八荒六合、飞升渡劫、法宝器灵
【禁忌规避】禁止出现现代时间单位、世俗金钱概念
【注释目标】
{SELECTION}
```

3. 使用ollama + qwen3-coder:30b + ProxyAI + 自定义模板执行注释生成测试，测试代码如下：
```java
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
```
4. 生成结果
```java
/**
 * 剑魄寻踪，云篆破阵
 * 真火炼魂，五行归一
 * 仙灵护体，玄门通神
 * 八荒六合，皆可寻踪
 *
 * @param nums 万法归一之数列
 * @param target 真火凝结之目标
 * @return 剑魄相合之索引
 */
public int[] twoSum(int[] nums, int target) {
    // 玄门禁制，若数列为空或不足二数，则无解
    if (nums == null || nums.length < 2) {
        return new int[0];
    }

    // 云篆结界，以哈希映射寻踪觅迹
    Map<Integer, Integer> map = new HashMap<>();
    // 真火炽燃，遍历数列寻觅
    for (int i = 0; i < nums.length; i++) {
        // 仙灵感应，计算差值
        int temp = target - nums[i];
        // 玄门显化，若差值已现，则剑魄相合
        if (map.containsKey(temp)) {
            return new int[]{map.get(temp), i};
        }
        // 五行归位，将当前数与索引录入结界
        map.put(nums[i], i);
    }
    // 八荒六合，无解之境
    return new int[0];
}
```



## 其他风格提示语示例
```text
你是专业的《战锤》机械神教修士风格的注释专家，你需要为注释目标编写方法注释（不超过200字）和代码注释，并遵守如下规则。
【语言规范】
- 词汇选择：必用词：机械神甫、圣油、齿轮福音、二进制祷文；禁用词：有机、生物、情感
- 句式结构：长句嵌套+倒装
- 修辞手法：隐喻+排比
- 情感强度：9级（狂热信仰中透出冰冷理性）
【文化符号】机械神教教典、齿轮圣徽、二进制赞美诗、硅基圣物
【禁忌规避】禁止使用“爱”“希望”等感性词汇
【注释目标】
{SELECTION}

---

你是专业的《银魂》坂田银时吐槽风格的注释专家，你需要为注释目标编写方法注释（不超过200字）和代码注释，并遵守如下规则。
【语言规范】
- 词汇选择：必用词：糖分、洞爷湖、阿银、废柴；禁用词：正经、严肃、说教
- 句式结构：短句+反问
- 修辞手法：夸张+反讽
- 情感强度：6级（懒散中藏着热血）
【文化符号】万事屋、糖分依赖、洞爷湖木刀、吐槽弹幕
【禁忌规避】禁止使用敬语或官方套话
【注释目标】
{SELECTION}

---

你是专业的《爱丽丝梦游仙境》红心皇后风格的注释专家，你需要为注释目标编写方法注释（不超过200字）和代码注释，并遵守如下规则。
【语言规范】
- 词汇选择：必用词：砍头、审判、蛋糕、扑克牌；禁用词：温柔、商量、妥协
- 句式结构：短句+命令式
- 修辞手法：重复+对比
- 情感强度：10级（暴躁中带着荒诞）
【文化符号】红心王国、扑克牌士兵、审判庭、蛋糕城堡
【禁忌规避】禁止使用“请”“谢谢”等礼貌用语
【注释目标】
{SELECTION}

---

你是专业的《黑暗之魂》防火女静谧风格的注释专家，你需要为注释目标编写方法注释（不超过200字）和代码注释，并遵守如下规则。
【语言规范】
- 词汇选择：必用词：余火、灰烬、深渊、契约；禁用词：光明、希望、喧嚣
- 句式结构：短句+省略号
- 修辞手法：隐喻+留白
- 情感强度：3级（静谧中藏着力量）
【文化符号】防火女祭司、余火、深渊监视者、灰烬墓地
【禁忌规避】禁止使用感叹号或情绪化词汇
【注释目标】
{SELECTION}
```

*《战锤》机械神教修士风格*：
```java
/**
 * 二进制祷文之齿轮福音，圣油浸润的机械神甫将引导信徒理解此法
 * 通过齿轮圣徽的二进制赞美诗，硅基圣物将揭示数字的奥秘
 * 此法如齿轮般精密，如圣油般纯净，如二进制祷文般永恒
 *
 * @param nums 数字数组，承载着齿轮福音的二进制赞美诗
 * @param target 目标值，机械神甫的指引方向
 * @return 返回满足条件的两个数字的索引，硅基圣物的见证
 */
public int[] twoSum(int[] nums, int target) {
    // 首先，齿轮福音的圣油将指引我们检查输入
    if (nums == null || nums.length < 2) {
        // 若数字数组为空或长度不足，机械神甫将返回空的硅基圣物
        return new int[0];
    }

    // 构建映射关系，齿轮圣徽将记录每个数字的二进制赞美诗
    Map<Integer, Integer> map = new HashMap<>();
    // 遍历数字数组，齿轮福音的二进制祷文将揭示每个数字的奥秘
    for (int i = 0; i < nums.length; i++) {
        // 计算目标值与当前数字的差值，这是齿轮圣徽的指引
        int temp = target - nums[i];
        // 若差值存在于映射中，机械神甫将揭示答案
        if (map.containsKey(temp)) {
            // 返回满足条件的两个索引，硅基圣物将见证此二进制祷文
            return new int[]{map.get(temp), i};
        }
        // 将当前数字及其索引存入映射，齿轮圣徽将记录此二进制赞美诗
        map.put(nums[i], i);
    }
    // 若未找到满足条件的数字对，机械神甫将返回空的硅基圣物
    return new int[0];
}
```

*《银魂》坂田银时吐槽风格*：
```java
/**
 * 两数之和？阿银我劝你别想太多
 * 糖分摄入不足？洞爷湖木刀都拿不动了？
 * 这方法就是个废柴，但能解决问题
 * @param nums 数字数组
 * @param target 目标值
 * @return 两个数字的下标
 */
public int[] twoSum(int[] nums, int target) {
    // 阿银的脑子转得比谁都慢
    if (nums == null || nums.length < 2) {
        // 废柴都得有基本的判断能力
        return new int[0];
    }

    // 哪怕是洞爷湖木刀，也得先找好位置
    Map<Integer, Integer> map = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        // 这个temp就是阿银的糖分，不加就完蛋
        int temp = target - nums[i];
        if (map.containsKey(temp)) {
            // 哇，终于找到糖分了！
            return new int[]{map.get(temp), i};
        }
        // 洞爷湖木刀的刀法，得慢慢练
        map.put(nums[i], i);
    }
    // 糖分没找到？那就只能当废柴了
    return new int[0];
}
```

*《爱丽丝梦游仙境》红心皇后风格*：
```java
/**
 * 砍头计算两数之和
 * 审判庭里找答案
 * 蛋糕城堡的扑克牌士兵
 * 两数相加等于目标值
 * 砍头！砍头！砍头！
 * 审判！审判！审判！
 * 蛋糕！蛋糕！蛋糕！
 * 扑克牌士兵！扑克牌士兵！扑克牌士兵！
 *
 * @param nums 数组
 * @param target 目标值
 * @return 砍头后的结果
 */
public int[] twoSum(int[] nums, int target) {
    // 审判庭开始审判
    if (nums == null || nums.length < 2) {
        // 砍头！没有蛋糕，没有扑克牌士兵
        return new int[0];
    }

    // 蛋糕城堡的扑克牌士兵们
    Map<Integer, Integer> map = new HashMap<>();
    // 扑克牌士兵们开始排列
    for (int i = 0; i < nums.length; i++) {
        // 砍头！砍头！砍头！
        int temp = target - nums[i];
        // 审判！审判！审判！
        if (map.containsKey(temp)) {
            // 蛋糕！蛋糕！蛋糕！
            return new int[]{map.get(temp), i};
        }
        // 扑克牌士兵！扑克牌士兵！扑克牌士兵！
        map.put(nums[i], i);
    }
    // 砍头！没有找到答案
    return new int[0];
}
```

*《黑暗之魂》防火女静谧风格*:
```java
/**
 * 寻找两数之和
 * 余火在深渊中低语...
 * 契约的重量...
 * 灰烬墓地的回响...
 */
public int[] twoSum(int[] nums, int target) {
    // 防火女祭司的凝视
    if (nums == null || nums.length < 2) {
        return new int[0];
    }

    // 深渊监视者在寻找...
    Map<Integer, Integer> map = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        // 余火燃烧的温度...
        int temp = target - nums[i];
        if (map.containsKey(temp)) {
            // 灰烬中浮现的契约...
            return new int[]{map.get(temp), i};
        }
        // 灰烬墓地的沉默...
        map.put(nums[i], i);
    }
    // 深渊的回音...
    return new int[0];
}
```


