# 系统级联调与稳定性回归（全链路）

本文档用于执行以下目标：

1. 全链路回归：登录 -> 发帖 -> 评论 -> 搜索 -> 通知 -> 推荐  
2. 异常场景验证：无权限、并发操作、登出失效、（可选）token 过期

## 1. 前置条件

1) 基础设施与后端服务已启动（gateway/auth/forum/notification/media/search）  
2) 网关可访问 `http://127.0.0.1:8080`

## 2. 执行命令

默认回归（不等待 token 过期）：

```bash
python3 deploy/scripts/run_system_regression.py
```

指定网关地址：

```bash
python3 deploy/scripts/run_system_regression.py --base-url "http://127.0.0.1:8080"
```

启用 token 过期验证：

```bash
python3 deploy/scripts/run_system_regression.py --verify-expiry --expiry-wait-seconds 12
```

> 说明：启用过期验证时，请确保当前系统 access token 过期时间小于等于等待时间。

## 3. 覆盖场景

脚本会自动校验：

1. 分区读取  
2. 双用户注册登录  
3. 发帖与评论  
4. 搜索命中  
5. 首页通知与媒体推荐接口  
6. 未带 token 的写操作应失败  
7. 无权限删除他人帖子应失败  
8. 并发重复点赞（期望 1 次成功 + 1 次重复失败）  
9. 登出后旧 token 立即失效  
10. refresh 获取新 access token 并可访问受保护接口  
11. （可选）token 过期后访问受保护接口失败

## 4. 失败处理

脚本失败会返回非 0 并输出失败场景与接口响应，可用于快速定位问题。
