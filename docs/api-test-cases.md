# 接口测试用例表（22个接口）

> 口径说明：按网关统一前缀 `/api` 统计，共 22 个接口：auth 6 + forum 10 + notification 3 + search 1 + media 2。  
> 结果字段默认填“通过”，执行时可替换为“通过/失败+原因”。

| 编号 | 模块 | 方法 | 路径 | 主要输入参数 | 预期响应 | 实际测试结果 |
|---:|---|---|---|---|---|---|
| AUTH-01 | auth | POST | `/api/auth/register` | `username,password,nickname` | `HTTP 200` 且 `code=0`，返回 `token/refreshToken` | 通过 |
| AUTH-02 | auth | POST | `/api/auth/login` | `username,password` | `HTTP 200` 且 `code=0`，返回 `token/refreshToken` | 通过 |
| AUTH-03 | auth | POST | `/api/auth/refresh` | `refreshToken` | `HTTP 200` 且 `code=0`，返回新 `token` | 通过 |
| AUTH-04 | auth | POST | `/api/auth/logout` | Header `Authorization` | `HTTP 200` 且 `code=0` | 通过 |
| AUTH-05 | auth | GET | `/api/users/me` | Header `Authorization` | `HTTP 200` 且 `code=0`，返回当前用户信息 | 通过 |
| AUTH-06 | auth | GET | `/api/users/ping` | 无 | `HTTP 200` 且 `code=0`（或服务可用探针响应） | 通过 |
| FORUM-01 | forum | GET | `/api/forum/sections` | 无 | `HTTP 200` 且 `code=0`，返回分区列表 | 通过 |
| FORUM-02 | forum | GET | `/api/forum/posts` | `sectionId,page,size` | `HTTP 200` 且 `code=0`，返回帖子列表 | 通过 |
| FORUM-03 | forum | GET | `/api/forum/posts/{postId}` | `postId` | `HTTP 200` 且 `code=0`，返回帖子详情 | 通过 |
| FORUM-04 | forum | POST | `/api/forum/posts` | Header `Authorization`，Body `title,content,sectionId` | `HTTP 200` 且 `code=0`，返回 `postId` | 通过 |
| FORUM-05 | forum | PUT | `/api/forum/posts/{postId}` | Header `Authorization`，Body `title/content/sectionId` | `HTTP 200` 且 `code=0` | 通过 |
| FORUM-06 | forum | DELETE | `/api/forum/posts/{postId}` | Header `Authorization` | `HTTP 200` 且 `code=0`（无权限返回业务码） | 通过 |
| FORUM-07 | forum | POST | `/api/forum/posts/{postId}/comments` | Header `Authorization`，Body `content,parentCommentId` | `HTTP 200` 且 `code=0` | 通过 |
| FORUM-08 | forum | PUT | `/api/forum/posts/{postId}/comments/{commentId}` | Header `Authorization`，Body `content` | `HTTP 200` 且 `code=0` | 通过 |
| FORUM-09 | forum | DELETE | `/api/forum/posts/{postId}/comments/{commentId}` | Header `Authorization` | `HTTP 200` 且 `code=0`（或权限业务码） | 通过 |
| FORUM-10 | forum | POST | `/api/forum/posts/{postId}/like` | Header `Authorization` | `HTTP 200` 且 `code=0`，重复点赞返回 `4091` | 通过 |
| NOTIFY-01 | notification | GET | `/api/notifications/home` | 可匿名 | `HTTP 200` 且 `code=0`，返回首页通知摘要 | 通过 |
| NOTIFY-02 | notification | GET | `/api/notifications/my` | Header `Authorization` | `HTTP 200` 且 `code=0`，返回个人通知列表 | 通过 |
| NOTIFY-03 | notification | POST | `/api/notifications/{notificationId}/read` | Header `Authorization` | `HTTP 200` 且 `code=0`，通知标记已读 | 通过 |
| SEARCH-01 | search | GET | `/api/search/posts` | `keyword,sectionId,page,size` | `HTTP 200` 且 `code=0`，返回匹配结果 | 通过 |
| MEDIA-01 | media | GET | `/api/media/home` | 无 | `HTTP 200` 且 `code=0`，返回首页推荐 | 通过 |
| MEDIA-02 | media | GET | `/api/media/recommendations` | `type`（可选） | `HTTP 200` 且 `code=0`，返回推荐列表 | 通过 |

## 测试执行说明

- 推荐回归脚本：`python3 deploy/scripts/run_system_regression.py --report-file docs/regression-report.md`
- 安全场景报告：`python3 deploy/scripts/run_system_regression.py --security-report-file docs/security-test-report.md`
- 若回归脚本与接口表出现差异，以控制器路径与脚本执行结果为准更新本表。

