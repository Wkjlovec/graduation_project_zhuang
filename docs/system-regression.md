# 系统级联调与稳定性回归（全链路）

本文档用于执行以下目标：

1. 全链路回归：登录 -> 发帖 -> 评论 -> 搜索 -> 通知 -> 推荐  
2. 异常场景验证：无权限、并发操作、登出失效、（可选）token 过期

## 1. 前置条件

1) 基础设施与后端服务已启动（gateway/auth/forum/notification/media/search）  
2) 网关可访问 `http://127.0.0.1:8080`

## 2. 执行命令

一键生成回归与缓存报告（推荐）：

```bash
bash deploy/scripts/generate-test-reports.sh
```

可选参数：
- `BASE_URL`（默认 `http://127.0.0.1:8080`）
- `FORUM_BASE_URL`（默认 `http://127.0.0.1:8082`）
- `EXPIRY_WAIT_SECONDS`（默认 `12`）
- `RUN_MODE`（`auto/full/direct`）

说明：
- `full`：生成回归+过期+缓存报告（需要 gateway）
- `direct`：仅生成缓存报告（forum 直连）

默认回归（不等待 token 过期）：

```bash
python3 deploy/scripts/run_system_regression.py --report-file docs/regression-report.md
```

仅生成安全测试明细报告（由回归脚本提炼）：

```bash
python3 deploy/scripts/run_system_regression.py \
  --report-file docs/regression-report.md \
  --security-report-file docs/security-test-report.md
```

指定网关地址：

```bash
python3 deploy/scripts/run_system_regression.py --base-url "http://127.0.0.1:8080"
```

启用 token 过期验证：

```bash
python3 deploy/scripts/run_system_regression.py --verify-expiry --expiry-wait-seconds 12 --report-file docs/regression-report-expiry.md
```

> 说明：启用过期验证时，请确保当前系统 access token 过期时间小于等于等待时间。

## 3. 覆盖场景

脚本会自动校验：

1. 分区读取  
2. 双用户注册登录  
3. 发帖与评论  
4. 搜索命中  
5. 首页通知与媒体推荐接口  
6. 我的通知读取与已读标记（有未读则校验标记接口）  
7. 未带 token 的写操作应失败  
8. 无权限删除他人帖子应失败  
9. 并发重复点赞（期望 1 次成功 + 1 次重复失败）  
10. 登出后旧 token 立即失效  
11. refresh 获取新 access token 并可访问受保护接口  
12. （可选）token 过期后访问受保护接口失败

新增安全向量场景（同脚本内执行）：

13. 非法 Token 拦截  
14. 通知接口无 Token 拦截  
15. 搜索关键词 SQL 注入基础向量（`' OR 1=1 --`）  
16. 搜索关键词 XSS 基础向量（`<script>alert(1)</script>`）

## 4. 失败处理

脚本失败会返回非 0 并输出失败场景与接口响应，可用于快速定位问题。

## 5. 本轮云端执行记录

当前云端环境未启动网关/微服务时，已保留一次真实失败报告用于排障：

- `docs/regression-report-cloud.md`

## 6. 并发负载测试

为补齐并发性能验证，新增脚本：

```bash
python3 deploy/scripts/load_test_concurrent.py \
  --base-url "http://127.0.0.1:8080" \
  --path "/api/forum/posts?page=0&size=10" \
  --concurrency-levels "10,50,100" \
  --requests-per-user 20 \
  --report-file docs/concurrent-load-report.md
```

输出：
- `docs/concurrent-load-report.md`（并发量 vs 平均响应/P95/成功率/QPS 对照表 + Mermaid 曲线图）
