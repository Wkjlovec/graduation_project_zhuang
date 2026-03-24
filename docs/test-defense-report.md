# 测试与答辩报告清单（可直接留档）

本文档用于提交前形成“可复现实验 + 可展示材料”。

## 1. 自动化回归报告

推荐一键生成（在后端服务已启动前提下）：

```bash
bash deploy/scripts/generate-test-reports.sh
```

可选参数：
- `BASE_URL`（默认 `http://127.0.0.1:8080`）
- `FORUM_BASE_URL`（默认 `http://127.0.0.1:8082`）
- `EXPIRY_WAIT_SECONDS`（默认 `12`）
- `RUN_MODE`（`auto/full/direct`）

---

执行命令（基础回归）：

```bash
python3 deploy/scripts/run_system_regression.py --report-file docs/regression-report.md
```

执行命令（输出安全测试报告）：

```bash
python3 deploy/scripts/run_system_regression.py --report-file docs/regression-report.md --security-report-file docs/security-test-report.md
```

执行命令（含 token 过期）：

```bash
python3 deploy/scripts/run_system_regression.py --verify-expiry --expiry-wait-seconds 12 --report-file docs/regression-report-expiry.md
```

产出物：
- `docs/regression-report.md`
- `docs/regression-report-expiry.md`

执行命令（缓存前后响应时间对比）：

```bash
python3 deploy/scripts/benchmark_forum_cache.py --report-file docs/cache-benchmark-report.md
# 如需兼容旧命名产物（答辩材料引用）：
python3 deploy/scripts/benchmark_forum_cache.py --report-file docs/evidence-cache-benchmark.md
```

执行命令（并发负载测试）：

```bash
python3 deploy/scripts/load_test_concurrent.py --report-file docs/concurrent-load-report.md
```

产出物：
- `docs/cache-benchmark-report.md`
- `docs/evidence-cache-benchmark.md`（兼容旧命名）
- `docs/concurrent-load-report.md`
- `docs/security-test-report.md`

> 说明：该脚本会对同一帖子列表接口先做 1 次“冷请求”，再做 N 次“热请求”（默认 20 次），自动输出均值、P95 与相对提升百分比，可直接用于论文与答辩表格。

本轮云端检查结果（用于排障留档）：
- `docs/regression-report-cloud.md`（当前云端 8080 未启动，连接被拒绝）
- `docs/cache-benchmark-report-cloud.md`（当前云端 8080 未启动，连接被拒绝）

## 2. 手工联调展示材料（截图建议）

建议至少保留以下截图（PC+移动端）：

1. 登录成功页（含用户信息）  
2. 发帖成功后详情页  
3. 二级评论回复展示  
4. 搜索命中结果  
5. 首页通知模块  
6. 首页音乐/书籍推荐模块  
7. 我的通知页（含“标记已读”）  
8. 无权限操作错误提示  
9. 登出后访问受保护接口失败提示

## 3. 答辩演示顺序（建议）

1. 启动基础设施 + 微服务注册列表  
2. 登录 -> 发帖 -> 评论 -> 搜索  
3. 打开首页展示通知/推荐  
4. 演示无权限删除与并发点赞重复拦截  
5. 演示登出后 token 失效

## 3.1 接口测试与兼容性文档

新增文档：
- `docs/api-test-cases.md`（22 个接口测试用例表）
- `docs/security-test-cases.md`（安全测试用例与结果模板）
- `docs/compatibility-test-matrix.md`（浏览器与移动端兼容性测试记录）

## 4. 性能与稳定性简表（可填）

| 指标 | 数据 | 备注 |
|---|---:|---|
| 帖子列表首次请求（冷） | 见 `docs/cache-benchmark-report.md` | `benchmark_forum_cache.py` |
| 帖子列表后续请求均值（热） | 见 `docs/cache-benchmark-report.md` | `benchmark_forum_cache.py` |
| 回归脚本通过率 | 100%（2/2） | 样本：`regression-report.md`、`regression-report-expiry.md` |
| 异常场景通过率 | 100%（6/6） | 无 token、无权限、并发点赞、登出失效、refresh、token 过期 |

统计口径说明（2026-03-20）：
- 回归脚本通过率：以“是否整份报告通过”为单位，当前两份报告均通过。
- 异常场景通过率：口径为 6 项（无 token、无权限、并发点赞、登出失效、refresh、token 过期），当前样本全部通过。

## 5. 判定标准

- 自动回归脚本通过  
- PC/移动端主流程可演示  
- 关键异常场景有截图或报告  
- 文档可复现（README + system-regression + 本文档）
