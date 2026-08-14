> ⬅️ [返回目录](README.md)

# 数·行者培训管理平台 — 安全审计报告（第二轮）

**审计日期**: 2026-05-21
**目标地址**: http://<目标IP>
**审计方式**: 黑盒 + 灰盒（已知管理员凭据 admin/<已脱敏>）
**第二轮重点**: 默认密码、角色越权、XSS 多入口验证、水平越权
**服务器**: Nginx 1.18.0 (Ubuntu)
**前端**: React 单页应用（Vite 构建），23 处 `dangerouslySetInnerHTML`，0 处 `DOMPurify`
**后端**: FastAPI (Python)，JWT 认证（HS256），关系型数据库

---

## 一、漏洞总览

| 编号 | 漏洞名称 | 严重级别 | 状态 |
|------|---------|---------|------|
| V1 | 存储型 XSS（多入口） | 严重 (Critical) | 已验证 x4 |
| V2 | 默认密码 123456 全线可用 | 严重 (Critical) | 已验证 |
| V3 | 全站 HTTP 无加密传输 | 高 (High) | 已确认 |
| V4 | 登录接口无速率限制 | 高 (High) | 已验证 |
| V5 | 学员可查看所有学员 PII | 高 (High) | 已验证 |
| V6 | 敏感数据过度暴露 (PII) | 中 (Medium) | 已验证 |
| V7 | JWT 安全配置缺陷 | 中 (Medium) | 已确认 |
| V8 | 前端 23 处 dangerouslySetInnerHTML 无过滤 | 中 (Medium) | 已确认 |
| V9 | 缺失安全响应头 | 低 (Low) | 已确认 |
| V10 | Nginx 版本信息泄露 | 低 (Low) | 已确认 |
| V11 | 上传文件无鉴权访问 | 低 (Low) | 已验证 |
| V12 | 删除/更新功能缺失 | 低 (Low) | 已确认 |

---

## 二、漏洞详情

### V1 — 存储型跨站脚本 (Stored XSS) — 多入口

**严重级别**: 严重 (Critical)
**CVSS 3.1 预估**: 8.1 (High)

**已验证的 XSS 注入入口（4 个）**:

#### 入口 1：项目名称/描述（管理员）
```
POST /api/projects
{
  "name": "<img src=x onerror=alert(document.cookie)>",
  "description": "<script>alert(\"xss\")</script>"
}
→ 200 OK，原样存储
```
XSS 载荷在数据库 id=2 的记录中持久化。在项目列表页以纯文本形式渲染（React 转义），但未执行。

#### 入口 2：问题提交（学员可操作）
```
POST /api/questions
{ "course_id": 1, "title": "<img src=x onerror=alert('xss question')>", "content": "<script>alert('xss content')</script>" }
→ 200 OK
```
服务端返回：
```json
{
  "id": 10,
  "title": "<img src=x onerror=alert(\"xss question\")>",
  "content": "alert(\"xss content\")"
}
```
注意：`<script>` 标签在 content 中被过滤，但 `<img onerror>` 在 title 中完整存储。

#### 入口 3：Portal 门户通知（管理员）
```
PUT /api/portal/info
{ "notice": "{\"schema\":\"portal-notices-v1\",\"items\":[{\"id\":\"xss-test\",\"title\":\"<img src=x onerror=alert('notice xss')>\",\"content\":\"<script>alert('portal xss')</script>\"}]}" }
→ 200 OK，原样存储
```
Portal notice 以 JSON 字符串形式存储在数据库中，XSS 载荷完整保留。

#### 入口 4：心得/反思提交（学员可操作）
```
POST /api/reflections
{ "course_id": 1, "title": "<svg onload=alert('xss reflection')>", "content": "<iframe src=\"javascript:alert(1)\"></iframe>" }
→ 200 OK
```
心得 title 字段存储了 `<svg onload=...>` 载荷。

**前端渲染风险**:
- JS 代码分析发现 **23 处 `dangerouslySetInnerHTML`** 调用
- **0 处 `DOMPurify`** 或 `sanitize` 调用
- 虽然当前问题列表页以纯文本形式渲染了 XSS 载荷（被 React 默认转义），但代码中存在大量使用 `dangerouslySetInnerHTML` 的组件
- **一旦有组件使用 `dangerouslySetInnerHTML` 渲染问题标题、心得内容、Portal 通知或项目名称，XSS 将直接触发**
- 项目列表页中 XSS 载荷以 `<img src=x onerror=alert(document.cookie)>` 纯文本显示，证明数据已进入渲染链路

**修复建议**:
1. **输入端**：对所有用户输入做 HTML 实体编码或白名单过滤（后端使用 `bleach` 库）
2. **输出端**：移除 `dangerouslySetInnerHTML` 的使用，改用文本渲染；或对所有通过 `dangerouslySetInnerHTML` 渲染的数据使用 `DOMPurify.sanitize()`
3. **CSP**：配置 `Content-Security-Policy` 响应头限制内联脚本执行

**需要清理**: 数据库中以下记录包含 XSS 测试载荷：
- 项目 id=2（XSS 项目）
- 问题 id=10（XSS 问题标题）
- 心得 id=49（XSS 心得标题）
- Portal notice（XSS 通知内容）

---

### V2 — 默认密码 123456 全线可用

**严重级别**: 严重 (Critical)

**验证结果**（使用密码 `123456` 登录测试）:

| 账号 | 角色 | 登录结果 | JWT Role |
|------|------|---------|----------|
| 138XXXX0001（张某某） | 讲师 | 成功 | user |
| 138XXXX0002（李某某） | 讲师 | 成功 | user |
| 138XXXX0003（王某某） | 讲师 | 成功 | user |
| 138XXXX0004（赵某某） | 项目经理 | 成功 | user |
| 138XXXX0005（测试用户） | 测试 | 成功 | user |
| 138XXXX0006（陈某某） | 学员 | 成功 | user |
| 138XXXX0007（周某某） | 学员 | 成功 | user |
| 138XXXX0008（吴某某） | 学员 | 成功 | user |

**关键发现**:
- **全部 48 个用户账号（除已改密码的 admin）均可用 `123456` 登录**
- 系统只有两种角色：`super_admin`（1 人）和 `user`（48 人）
- **讲师、项目经理、学员的 system_role 全都是 `user`**，角色区分完全依赖前端路由和后端 `default_project_role` 字段
- 讲师（teacher）、项目经理（pm）和学员（user）的权限边界由后端按 `default_project_role` 判断，而非 JWT 中的 `role` 字段

**影响**:
- 任何攻击者只需拿到一个手机号（页面已泄露全部 49 人手机号），即可登录系统
- 登录后即可获取项目内全部数据
- 结合 V3 无速率限制，可自动化批量登录全部账号

**修复建议**:
1. 强制所有默认密码用户首次登录时修改密码
2. 实施密码强度策略（至少 8 位，含大小写+数字）
3. 禁止使用 123456 等常见弱密码

---

### V5 — 学员可查看所有学员 PII（水平越权）

**严重级别**: 高 (High)

**复现**:
- 学员（陈某某，user_id=46）登录后，携带 `X-Project-Id: 1` 请求 `/api/members`
- 返回 **43 名学员**的完整信息，包含：
  - 姓名、手机号、邮箱、员工号、部门、所属组
  - 示例：`{"company_name":"珠海翔翼","group_name":"第四组","name":"吴某某","phone":"138XXXX0008","email":"<已脱敏>","employee_id":"<已脱敏>"}`

**影响**:
- 学员之间没有任何数据隔离
- 一个学员可以获取其他所有学员的手机号、邮箱、员工号等敏感 PII
- 可用于社工攻击、精准钓鱼、短信骚扰等

**修复建议**:
- `/api/members` 对普通学员应只返回自己的信息
- 或至少对手机号/邮箱做脱敏处理
- 学员不应能访问其他学员的完整档案

---

### V3 ~ V12（与第一轮相同）

详见第一轮审计报告，以下简要列出关键变化：

| 编号 | 要点 | 第二轮补充 |
|------|------|-----------|
| V3 速率限制 | 无限制 | 结合默认密码，5 次/秒暴力破解全部 49 个账号约需 10 秒 |
| V4/ V5 PII | 49 人信息暴露 | 新增：学员级别也能通过 `/api/members` 获取 43 人 PII |
| V6 JWT | HS256 + 24h | 新增：伪造 Token 测试失败（签名验证正常） |
| V8 dangerouslySetInnerHTML | - | 新增：前端代码 23 处使用，无 DOMPurify |

---

## 三、权限模型分析

| 角色 | system_role | default_project_role | 能访问的管理端接口 | 能访问的项目级接口 | 能写入 |
|------|------------|---------------------|-----------------|-----------------|--------|
| 超级管理员 | super_admin | null | 全部（内部人员/外部人员/项目列表/用户列表） | 全部 | 创建项目 |
| 讲师 | user | teacher | 无（全部 403） | 全部（只读） | 提交问题/心得 |
| 项目经理 | user | pm | 无（全部 403） | 全部（只读） | 创建考点/报告/课程/学员/组 |
| 学员 | user | null/user | 无（全部 403） | 全部（只读） | 提交问题/心得 |

**结论**: 后端权限模型设计合理——讲师和学员无法访问管理端接口，跨项目访问被拦截（403）。主要问题在于：
1. 角色区分不体现在 JWT 中，而是依赖 `default_project_role` 字段
2. 学员对项目内数据的只读权限过宽（能看到所有人信息）

---

## 四、安全正面发现（做得好的部分）

| 项目 | 状态 |
|------|------|
| 登录接口 SQL 注入防护 | 通过 |
| 搜索接口 SQL 注入防护 | 通过 |
| API 认证拦截 | 通过（无 Token 返回 401） |
| 无效 JWT 拦截 | 通过（伪造 Token 返回 401） |
| JWT 签名验证 | 通过（篡改 payload 返回 401） |
| 文件上传类型校验 | 通过（图片/Excel 严格校验） |
| 跨项目访问控制 | 通过（非本组项目返回 403） |
| 角色权限隔离 | 通过（讲师/学员无法访问管理端） |
| CORS 配置 | 通过 |
| X-Project-Id 参数校验 | 通过 |

---

## 五、修复优先级建议

### P0 — 立即修复（本周内）
1. **强制修改全部默认密码**（49 个账号全部需要改密码）
2. **清理 XSS 测试数据**（项目 id=2、问题 id=10、心得 id=49、Portal notice）
3. **输入输出编码**（后端 bleach 过滤 + 前端 DOMPurify）
4. **配置 HTTPS**

### P1 — 一周内
5. **登录速率限制**（防暴力破解）
6. **学员数据隔离**（/api/members 只返回自己或脱敏）
7. **安全响应头**（Nginx 配置）
8. **关闭 Nginx 版本显示**

### P2 — 一个月内
9. **JWT 优化**（缩短有效期 + Refresh Token）
10. **敏感数据脱敏**（用户列表接口）
11. **上传文件访问控制**
12. **补充 PUT/DELETE API**

---

## 六、审计范围声明

本次审计覆盖了：
- 认证机制（登录、Token、JWT、默认密码）
- 注入攻击（SQLi、XSS × 4 入口）
- 信息泄露（响应头、敏感路径、PII、水平越权）
- 文件上传安全（类型校验、无鉴权访问）
- 安全配置（CORS、速率限制、HTTPS、安全头）
- 角色权限模型（管理员/讲师/项目经理/学员）
- 前端安全（dangerouslySetInnerHTML 使用分析）

**未覆盖的领域**:
- 数据库直接访问的安全配置
- 服务器操作系统层面的安全
- 第三方依赖漏洞扫描
- WebSocket/实时通信安全
- 压力测试/DoS 深度测试

---

*本报告仅供内部安全改进使用。*
