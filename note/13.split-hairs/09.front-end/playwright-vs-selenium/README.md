# Playwright vs Selenium：2026 Web 自动化测试选型

> Selenium 真的要退出历史舞台了吗？Playwright 凭什么成为 2026 主流？考察的是 **测试工具选型的工程判断**，不是"哪个更好用"。

## 引子：Selenium 测试 30 分钟跑不完，团队想换工具

```text
测试团队老王：
- Selenium 测试 200 条 CI 跑 30 分钟
- 经常由于"元素未加载"假阴性，flaky 率高
- 工程师每天 1 小时在排查 flaky
- 老板：能不能换个快点的工具？
```

**真相**：

- Selenium 的根因：**WebDriver 协议有双向通信瓶颈**
- Playwright 用 **Chrome DevTools Protocol（CDP）** 直接驱动浏览器，无中间协议 → **快 2-5 倍**
- 自动等待（auto-wait）机制 → flaky 率下降 80%

但 Selenium 不会消亡：

- 老旧浏览器（IE / 远古 Safari）还得靠它
- 庞大的现有 case 库迁移成本

**选 Playwright if 新项目，保留 Selenium if 维护老 stack**。

## 一、核心结论（TL;DR）

| 维度 | Selenium | Playwright |
|------|----------|------------|
| 架构 | WebDriver 协议 | DevTools 协议 |
| 速度 | 慢 | ⚡ 快 2-5 倍 |
| 自动等待 | ❌ 手动 | ✅ 内置 |
| 多浏览器 | ✅ | ✅ |
| 多语言 | ✅ Java/Python/JS/... | ✅ JS/Python/Java/.NET |
| 多标签页 | ❌ 难 | ✅ 内置 |
| Trace Viewer | ❌ 无 | ✅ 内置 |
| 录制工具 | Selenium IDE | Codegen |
| 维护方 | Selenium 社区 | Microsoft |
| 学习曲线 | 中 | 较低 |
| 2026 主流度 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

> 一句话：**2026 年新项目首选 Playwright，老项目维护可保留 Selenium**。

---

## 二、Playwright 为什么能取代 Selenium？

### 1. 架构更现代

**Selenium（2004-）**：
- 用 WebDriver 协议（基于 HTTP REST）
- 浏览器和测试代码之间有 WebDriver 中间层
- 每次操作都要走 HTTP 通信，慢

**Playwright（2020-）**：
- 用 Chrome DevTools Protocol（CDP）
- 直接通过 WebSocket 与浏览器通信
- 一次连接，长期使用，快

### 2. 自动等待（Auto-waiting）

**Selenium**：
```python
# 手动等待 + 异常处理
from selenium.webdriver.support.ui import WebDriverWait

wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.ID, "submit")))
element.click()  # 可能还是失败，要加 try-catch
```

**Playwright**：
```python
# 自动等待元素可见、可点击、稳定
page.click("#submit")  # Playwright 自动等待 5 大状态
```

Playwright 自动等待元素的 5 个状态：
1. attached to DOM
2. visible
3. enabled
4. stable (not animating)
5. receives events (not covered)

### 3. 多标签页 / iframe / Shadow DOM

**Selenium**：
```python
# 切换 iframe 要先 find，再 switch_to
iframe = driver.find_element(By.CSS_SELECTOR, "iframe")
driver.switch_to.frame(iframe)
```

**Playwright**：
```python
# 直接用 frame_locator 自动处理
page.frame_locator("iframe").locator("#submit").click()
```

### 4. Trace Viewer（调试神器）

Playwright 内置 Trace Viewer，能录制完整的执行过程：

```
- 截图（每一步）
- DOM 快照
- 网络请求
- Console 日志
- 时间线
```

Selenium 没有这个能力，只能靠截图 + log。

### 5. Codegen（录制工具）

Playwright 内置 `codegen` 命令，录制用户操作 → 自动生成测试代码：

```bash
playwright codegen https://example.com
# 打开浏览器，记录操作，生成 Python/JS 代码
```

Selenium IDE 类似但功能弱很多。

---

## 三、5 大维度详细对比

### 1. 性能

| 操作 | Selenium | Playwright |
|------|----------|------------|
| 启动浏览器 | 3-5 秒 | 0.5-1 秒 |
| 点击元素 | 200ms | 50ms |
| 100 个测试用例 | 10 分钟 | 3 分钟 |

### 2. API 设计

| Selenium | Playwright |
|----------|------------|
| `driver.find_element()` | `page.locator()` |
| `driver.click()` | `page.click()` |
| `driver.send_keys()` | `page.fill()` |
| `driver.get(url)` | `page.goto(url)` |

Playwright 的 API 更简洁、更语义化。

### 3. 跨浏览器

| 浏览器 | Selenium | Playwright |
|--------|----------|------------|
| Chrome | ✅ | ✅ |
| Firefox | ✅ | ✅ |
| Safari | ✅ | ✅ |
| Edge | ✅ | ✅ |
| WebKit | ⚠️ | ✅ 内置 |
| Mobile (iOS/Android) | ⚠️ Appium | ✅ 内置 |

Playwright 移动端测试是真正的"原生移动浏览器"，Selenium 需要 Appium 桥接。

### 4. 测试稳定性

| 维度 | Selenium | Playwright |
|------|----------|------------|
| 偶发性失败（flaky） | 高（10-20%） | 低（< 1%） |
| 自动重试 | ❌ 手动 | ✅ 内置 |
| 网络拦截 | 复杂 | 简单 |

### 5. CI/CD 集成

| 工具 | Selenium | Playwright |
|------|----------|------------|
| GitHub Actions | ✅ | ✅（官方支持） |
| GitLab CI | ✅ | ✅ |
| Docker | 复杂 | ✅ 官方镜像 |
| 并行执行 | Selenium Grid | Playwright 内置 |

---

## 四、实战代码对比

### 任务：登录 → 搜索 → 验证结果

**Selenium（Python）**：
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()
driver.get("https://example.com/login")

# 1. 输入用户名
username = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "username"))
)
username.send_keys("user")

# 2. 输入密码
password = driver.find_element(By.ID, "password")
password.send_keys("pass")

# 3. 点击登录
driver.find_element(By.ID, "submit").click()

# 4. 等待页面加载
time.sleep(2)  # ❌ 硬编码等待，不稳定

# 5. 验证登录成功
assert "Welcome" in driver.page_source
```

**Playwright（Python）**：
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    page.goto("https://example.com/login")
    
    # 自动等待，无需 time.sleep
    page.fill("#username", "user")
    page.fill("#password", "pass")
    page.click("#submit")
    
    # 等待元素出现
    page.wait_for_selector("text=Welcome")
    
    assert "Welcome" in page.content()
    
    browser.close()
```

**对比**：
- 代码量：Selenium 12 行 → Playwright 8 行
- 稳定性：time.sleep 是"反模式"，Playwright 无
- 可读性：Playwright API 更接近自然语言

---

## 五、2026 生态现状

### Selenium 的现状

- 仍是大量遗留项目的"主力"
- Selenium 4 加入了 CDP 协议支持（向 Playwright 看齐）
- 学习曲线低，文档丰富
- 主要劣势：架构老、等待机制弱、社区分散

### Playwright 的现状

- 2020 年发布，2026 年已是 Web 自动化测试事实标准
- 微软持续投入，每月发布新版本
- 主流框架（Next.js、Nuxt、SvelteKit）官方推荐 Playwright
- 2026 年新项目 80%+ 选 Playwright

### Cypress 的补充

- 另一主流 Web 测试框架
- 但仅支持 Chromium 系浏览器（不支持 Safari、Firefox 完整功能）
- 定位与 Playwright 接近，但生态稍弱

---

## 六、什么时候还用 Selenium？

虽然 Playwright 是趋势，但以下场景仍可选 Selenium：

1. **遗留项目维护**：已有大量 Selenium 测试用例
2. **团队技能**：团队熟悉 Selenium，学习成本高
3. **Appium 桥接**：需要测试原生移动 App（但 Playwright 已支持移动浏览器）
4. **特殊浏览器**：需要测试 IE / 旧版 Edge

---

## 七、面试陷阱

### 陷阱 1：以为 Selenium 完全过时

- **真相**：Selenium 仍是大量项目的主力，新项目选 Playwright

### 陷阱 2：以为 Playwright 只支持 Chromium

- **真相**：Playwright 支持 Chromium、Firefox、WebKit，移动端原生支持

### 陷阱 3：以为自动等待能解决所有稳定性问题

- **真相**：Playwright 解决 90% 的 flaky test，但仍有 10% 需要人工处理（如动画、网络）

### 陷阱 4：以为 Playwright 比 Selenium 快 10 倍

- **真相**：架构差异导致 Playwright 快 2-5 倍，但测试速度更多取决于用例设计

---

## 八、面试话术模板

> Playwright 是 2026 年 Web 自动化测试的事实标准，主要优势：
>
> 1. **架构现代**：基于 Chrome DevTools Protocol（WebSocket），比 Selenium 的 WebDriver HTTP 协议快 2-5 倍
> 2. **自动等待**：内置 5 元素状态等待（attached/visible/enabled/stable/receives events），无需 time.sleep
> 3. **多标签页 / Shadow DOM**：内置 frame_locator 自动处理
> 4. **Trace Viewer**：内置录制回放工具，可查看截图、DOM、网络请求
> 5. **Codegen**：内置录制工具，录制操作自动生成测试代码
>
> Selenium 仍有价值：遗留项目维护、团队技能栈、企业级应用。
>
> 新项目建议直接选 Playwright，老项目可逐步迁移。

---

## 九、相关章节

- 主模块：[`09.front-end/04-engineering`](../../../../09.front-end/04-engineering/README.md) — 前端工程化
- 主模块：[`05.tools`](../../../../05.tools/README.md) — 工具链

---

> 📅 2026-06-28 · 咬文嚼字 · 前端工具 · ⭐⭐⭐（工程必知 + 选型决策）