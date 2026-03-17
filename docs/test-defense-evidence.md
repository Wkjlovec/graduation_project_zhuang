# 测试与答辩证据清单（可直接留档）

本文档用于提交前形成“可复现实验 + 可展示证据”。

## 1. 自动化回归证据

执行命令（基础回归）：

```bash
python3 deploy/scripts/run_system_regression.py --report-file docs/evidence-regression.md
```

执行命令（含 token 过期）：

```bash
python3 deploy/scripts/run_system_regression.py --verify-expiry --expiry-wait-seconds 12 --report-file docs/evidence-regression-expiry.md
```

产出物：
- `docs/evidence-regression.md`
- `docs/evidence-regression-expiry.md`

## 2. 手工联调证据（截图建议）

建议至少保留以下截图（PC+移动端）：

1. 登录成功页（含用户信息）  
2. 发帖成功后详情页  
3. 二级评论回复展示  
4. 搜索命中结果  
5. 首页通知模块  
6. 首页音乐/书籍推荐模块  
7. 无权限操作错误提示  
8. 登出后访问受保护接口失败提示

## 3. 答辩演示顺序（建议）

1. 启动基础设施 + 微服务注册列表  
2. 登录 -> 发帖 -> 评论 -> 搜索  
3. 打开首页展示通知/推荐  
4. 演示无权限删除与并发点赞重复拦截  
5. 演示登出后 token 失效

## 4. 性能与稳定性简表（可填）

| 指标 | 数据 | 备注 |
|---|---:|---|
| 帖子列表平均响应（无缓存） | 待填 | 本地压测 |
| 帖子列表平均响应（有缓存） | 待填 | 本地压测 |
| 回归脚本通过率 | 待填 | 近3次执行 |
| 异常场景通过率 | 待填 | 无权限/并发/过期 |

## 5. 判定标准

- 自动回归脚本通过  
- PC/移动端主流程可演示  
- 关键异常场景有证据截图或报告  
- 文档可复现（README + system-regression + 本文档）
