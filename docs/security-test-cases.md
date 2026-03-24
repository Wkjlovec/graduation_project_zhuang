# 安全测试用例与结果

> 说明：本文件用于汇总安全相关测试。自动化结果可由 `deploy/scripts/run_system_regression.py --security-report-file` 生成到 `docs/security-test-report*.md`。本表用于论文与答辩整理。

## 1. 测试环境与口径

- 基础地址：`http://127.0.0.1:8080`（gateway）
- 鉴权口径：业务响应 `code`，重点关注 `4010`（未认证）、`4031`（无权限）、`4091`（并发重复点赞）
- 自动化脚本：`deploy/scripts/run_system_regression.py`

## 2. 安全测试用例表

| 用例ID | 场景 | 请求方法 | 请求路径 | 测试向量/输入 | 预期结果 | 实际结果（填写） |
|---|---|---|---|---|---|---|
| SEC-01 | 无 Token 写操作拦截 | POST | `/api/forum/posts` | 不带 Authorization | `code=4010` |  |
| SEC-02 | 无权限删除他人帖子拦截 | DELETE | `/api/forum/posts/{postId}` | 用户B删除用户A帖子 | `code=4031` |  |
| SEC-03 | 并发点赞去重 | POST*2 | `/api/forum/posts/{postId}/like` | 同一用户并发2次点赞 | 返回码集合为 `[0,4091]` |  |
| SEC-04 | 登出后会话失效 | GET | `/api/users/me` | 登出后使用旧 access token | `code=4010` |  |
| SEC-05 | 非法 Token 拦截 | GET | `/api/users/me` | `Authorization: Bearer not-a-valid-jwt` | `code=4010` |  |
| SEC-06 | 通知接口无 Token 拦截 | GET | `/api/notifications/my` | 不带 Authorization | `code=4010` |  |
| SEC-07 | SQL 注入基础验证 | GET | `/api/search/posts` | `keyword=' OR 1=1 --` | 接口正常返回 `code=0`，不出现越权数据 |  |
| SEC-08 | XSS 基础验证 | GET | `/api/search/posts` | `keyword=<script>alert(1)</script>` | 接口正常返回 `code=0`，不执行脚本 |  |
| SEC-09 | Access Token 过期拦截 | GET | `/api/users/me` | 等待 token 过期后访问 | `code=4010` |  |

## 3. 执行命令

基础回归 + 安全报告：

```bash
python3 deploy/scripts/run_system_regression.py \
  --base-url "http://127.0.0.1:8080" \
  --report-file docs/regression-report.md \
  --security-report-file docs/security-test-report.md
```

含过期验证：

```bash
python3 deploy/scripts/run_system_regression.py \
  --base-url "http://127.0.0.1:8080" \
  --verify-expiry \
  --expiry-wait-seconds 12 \
  --report-file docs/regression-report-expiry.md \
  --security-report-file docs/security-test-report-expiry.md
```

## 4. 结论模板（填写）

- 安全用例总数：`__ / 9`
- 通过数：`__`
- 通过率：`__%`
- 未通过用例及原因：`__`

