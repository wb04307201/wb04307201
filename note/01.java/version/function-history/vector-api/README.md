<!--
module:
  parent: java
  slug: java/version/vector-api
  type: article
  category: 主模块子文章
  summary: Java 16+ Vector API（孵化）：SIMD 加速数值计算。
-->

# Vector API

## 引言：变更说明

Vector API 是 N 个 JEP / 特性 / 章节的合集。

本篇按主题归类，给出每个条目的一句话定位 + 适用版本/场景，**先扫一遍再决定读哪节**。

---

## 功能描述

Vector API 提供了一套标准化的 Java 向量计算 API，允许开发者编写利用现代 CPU SIMD（Single Instruction, Multiple Data）指令集的代码。通过自动向量化优化，显著提升数值计算密集型任务的性能，适用于科学计算、机器学习、图像处理等场景。该特性自 Java 16 起作为孵化特性持续演进。

## 基本用法（最新，Java 26+ 孵化）

```java
import jdk.incubator.vector.*;

// 1. 基本向量运算 - 数组乘法
public static int[] vectorMultiply(int[] array, int factor) {
    int[] result = new int[array.length];
    // 选择 256 位向量（一次处理 8 个 int）
    VectorSpecies<Integer> species = IntVector.SPECIES_256;
    int bound = array.length - (array.length % species.length());
    int i = 0;
    for (; i < bound; i += species.length()) {
        IntVector va = IntVector.fromArray(species, array, i);
        va.mul(factor).intoArray(result, i);
    }
    // 处理尾部元素
    for (; i < array.length; i++) {
        result[i] = array[i] * factor;
    }
    return result;
}

// 2. 向量加法
public static float[] vectorAdd(float[] a, float[] b) {
    float[] result = new float[a.length];
    VectorSpecies<Float> species = FloatVector.SPECIES_PREFERRED;
    int bound = Math.min(a.length, b.length) - (Math.min(a.length, b.length) % species.length());
    int i = 0;
    for (; i < bound; i += species.length()) {
        FloatVector va = FloatVector.fromArray(species, a, i);
        FloatVector vb = FloatVector.fromArray(species, b, i);
        va.add(vb).intoArray(result, i);
    }
    return result;
}

// 3. 向量规约（点积）
public static double dotProduct(double[] a, double[] b) {
    DoubleVector sum = DoubleVector.zero(DoubleVector.SPECIES_PREFERRED);
    VectorSpecies<Double> species = sum.species();
    int bound = Math.min(a.length, b.length) - (Math.min(a.length, b.length) % species.length());
    int i = 0;
    for (; i < bound; i += species.length()) {
        DoubleVector va = DoubleVector.fromArray(species, a, i);
        DoubleVector vb = DoubleVector.fromArray(species, b, i);
        sum = va.fma(vb, sum);  // fused multiply-add
    }
    double result = sum.reduceLanes(VectorOperators.ADD);
    // 处理尾部
    for (; i < Math.min(a.length, b.length); i++) {
        result += a[i] * b[i];
    }
    return result;
}

// 4. 向量掩码操作（处理边界）
public static int[] vectorAddWithMask(int[] a, int[] b) {
    int[] result = new int[a.length];
    VectorSpecies<Integer> species = IntVector.SPECIES_PREFERRED;
    int i = 0;
    for (; i < a.length; i += species.length()) {
        IntVector.Mask mask = species.maskFromIndex(Math.min(species.length(), a.length - i));
        IntVector va = IntVector.fromArray(species, a, i, mask);
        IntVector vb = IntVector.fromArray(species, b, i, mask);
        va.add(vb).intoArray(result, i, mask);
    }
    return result;
}
```

## 变更历史表

| Java版本  | 新特性/增强内容                              |
|---------|---------------------------------------|
| Java 26 | JEP 529: Vector API（第十一次孵化）- 持续改进        |
| Java 25 | JEP 508: Vector API（第十次孵化）- 最新改进         |
| Java 24 | JEP 489: Vector API（第九次孵化）- 接近稳定        |
| Java 23 | JEP 469: Vector API（第八次孵化）- 进一步优化       |
| Java 22 | JEP 460: Vector API（第七次孵化）- 继续完善        |
| Java 21 | JEP 448: Vector API（第六次孵化）- 持续改进        |
| Java 20 | JEP 438: Vector API（第五次孵化）- 进一步增强       |
| Java 19 | JEP 426: Vector API（第四次孵化）- 继续优化        |
| Java 18 | JEP 417: Vector API（第三次孵化）- 进一步增强 API   |
| Java 17 | JEP 414: Vector API（第二次孵化）- 继续完善功能      |
| Java 16 | JEP 338: Vector API（第一次孵化）- 引入向量计算 API   |

## 功能详细介绍

### 1. Java 16 - Vector API 首次孵化 (JEP 338)

首次引入 Vector API，核心概念：
- **`VectorSpecies`**：定义向量类型（元素类型和长度）
- **`Vector`**：表示不可变向量，支持 add、mul、div 等操作
- **`VectorMask`**：控制哪些向量元素参与运算
- 目标：替代 JNI 调用本地库的方式，用纯 Java 实现 SIMD 加速

### 2. Java 17-26 - 持续孵化迭代 (JEP 414/417/426/438/448/460/469/489/508/529)

每次孵化版本持续改进：
- **性能优化**：C2 JIT 编译器对向量操作的优化不断增强
- **API 完善**：增加更多向量操作（fma、lane shuffle、broadcast 等）
- **平台支持**：扩展对 x64（AVX-512）、AArch64（NEON/SVE）的支持
- **稳定性提升**：修复早期版本的 bug，API 设计逐渐稳定

### 3. 核心组件

| 组件                | 说明                           |
|-------------------|------------------------------|
| `VectorSpecies<T>` | 向量类型描述符，定义元素类型和向量长度           |
| `IntVector` 等     | 具体向量实现类（IntVector、FloatVector 等） |
| `VectorMask`       | 掩码，控制向量元素的选择性操作              |
| `VectorOperators`  | 向量操作常量（ADD、MUL、FMA 等）         |

## 性能对比

在 AVX-512 支持的 CPU 上，使用 `SPECIES_512` 处理 100 万元素数组：
- **标量循环**：基准时间 1.0x
- **Vector API**：约 4-8x 加速（取决于操作类型）

## 注意事项

1. **孵化特性**：需要添加 `--add-modules jdk.incubator.vector` 启动参数
2. **硬件依赖**：性能提升取决于 CPU 是否支持 SIMD 指令集
3. **JIT 优化**：某些简单循环可能被 C2 自动向量化，无需显式使用 Vector API

## 总结

Vector API 自 Java 16 孵化以来，经过 11 轮迭代已接近稳定。它为 Java 数值计算提供了接近原生性能的向量化能力，是弥补 Java 在高性能计算领域差距的重要特性。
