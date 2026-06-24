# 07 安全

> 一句话定位：**前端安全——把浏览器与服务器之间的攻击面收敛到可防可控的范围内**

## 本模块覆盖

| 主题 | 状态 | 说明 |
|------|------|------|
| XSS | ✓ 已有 | [xss/](xss/) — 反射型 / 存储型 / DOM 型 + 转义策略 |
| CSRF | ✓ 已有 | [csrf/](csrf/) — 攻击原理 + SameSite / Token / Origin 校验 |
| CSP / SRI | ✓ 已有 | [csp/](csp/) — 内容安全策略 + 子资源完整性 |
| 依赖供应链 | ✓ 已有 | [supply-chain/](supply-chain/) — npm audit / Snyk / 锁文件 / 私有 Registry |
| CORS | ✓ 已有 | [cors/](cors/) — 跨域资源共享 |
| Sessions | ✓ 已有 | [sessions/](sessions/) — Cookies / LocalStorage 选型 |

## 与其他模块的关系

- 上游：[05-architecture](../05-architecture/)
- 下游：贯穿所有对外交付的应用

## 学习建议

- 安全是「**默认安全**」的心态,而不是「**事后修补**」的清单
- 关注 [OWASP Top 10](https://owasp.org/www-project-top-ten/) 行业基线即可覆盖 80% 场景
