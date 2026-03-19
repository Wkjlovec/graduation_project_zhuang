# 微服务论坛系统（毕业设计）

课题：**微服务架构的论坛系统实现（PC + 移动端）**  
当前已完成框架步骤：

1. 基础设施（Docker + Nacos + MySQL + Redis）  
2. 网关 + 注册发现  
3. 登录鉴权（JWT + Spring Security）  
4. 帖子评论主流程（forum-service）  
5. PC 端页面骨架（Vue3 + Element Plus）  
6. 移动端页面骨架（Vue3 + Vant）  
7. 缓存优化与测试数据（Redis Cache + DemoData）

范围约束文档：`docs/scope-baseline.md`
联调回归文档：`docs/system-regression.md`
测试与答辩报告：`docs/test-defense-report.md`
后端交付清单（启动顺序/排障/配置校验）：`docs/backend-delivery-checklist.md`

---

## 目录结构

```text
backend/
  pom.xml
  common-lib/
  gateway-service/
  auth-user-service/
  forum-service/
  notification-service/
  media-service/
  search-service/
frontend-pc/
frontend-mobile/
deploy/
  docker-compose.yml
  .env.example
  check-prerequisites.sh
  scripts/start-infra.sh
  scripts/verify-infra.sh
  scripts/start-infra-auto.sh
  scripts/verify-infra-auto.sh
  scripts/start-backend-all.sh
  scripts/verify-backend-all.sh
  scripts/stop-backend-all.sh
  scripts/generate-test-reports.sh
docs/
```

---

## 后端技术框架（已搭建）

- Java 17 + Spring Boot 3
- Spring Cloud Alibaba Nacos（注册发现）
- Spring Cloud Gateway（统一入口）
- JWT + Spring Security（登录鉴权）
- MySQL（用户、帖子、评论）
- Redis（帖子列表/详情缓存）

---

## 一键启动基础设施

```bash
cd deploy
cp .env.example .env
bash scripts/start-infra-auto.sh
bash scripts/verify-infra-auto.sh
```

说明：
- 有 Docker 时：自动走 `start-infra.sh`（容器模式）
- 无 Docker 时：自动走本机服务模式（MariaDB/Redis），并提示 Nacos 状态

默认端口：
- Nacos: `8848`
- Gateway: `8080`
- Auth Service: `8081`
- Forum Service: `8082`
- Notification Service: `8083`
- Media Service: `8084`
- Search Service: `8085`
- MySQL: `3306`
- Redis: `6379`

关键环境变量：
- `JWT_SECRET`：网关与鉴权服务必须使用同一个值
- `JWT_EXPIRE_SECONDS`：JWT 过期时间（秒）

---

## 后端全服务一键启动（脚本级）

在基础设施启动完成后，直接执行：

```bash
cd deploy
bash scripts/start-backend-all.sh
bash scripts/verify-backend-all.sh
```

停止后端全服务：

```bash
cd deploy
bash scripts/stop-backend-all.sh
```

脚本内置启动顺序：`auth -> forum -> notification -> media -> search -> gateway`  
（网关最后启动，减少服务未注册阶段的转发报错）

模式说明：
- `RUN_MODE=full`：要求 Nacos 可用，启动全部服务（含 gateway）
- `RUN_MODE=direct`：无 Nacos 场景，启动 auth/forum/notification/media/search（不启动 gateway）
- `RUN_MODE=auto`（默认）：自动根据 Nacos 可达性选择 full/direct

启动后可快速验活（与脚本一致）：

```bash
curl -fsS http://127.0.0.1:8081/actuator/health
curl -fsS http://127.0.0.1:8082/actuator/health
curl -fsS http://127.0.0.1:8083/actuator/health
curl -fsS http://127.0.0.1:8084/actuator/health
curl -fsS http://127.0.0.1:8085/actuator/health
curl -fsS http://127.0.0.1:8080/actuator/health
curl -fsS http://127.0.0.1:8080/api/forum/sections
```

常见报错快速定位：
- `mvn: command not found`：先确保 `mvn -v` 可用
- 401（登录后仍失败）：优先检查 `JWT_SECRET` 是否在 gateway/auth 完全一致
- Nacos 无注册：检查 `NACOS_SERVER_ADDR` 与 Nacos 可达性
- 数据库连接失败：检查 MySQL healthy 与 `.env` 数据库账号配置
- 网关 404：确认通过 `/api/**` 网关路径访问

更完整排障与本地校验清单见：`docs/backend-delivery-checklist.md`

CI 说明（毕设取舍）：
- CI（持续集成）是代码提交后自动执行构建/测试的流水线机制。
- 本项目在本科毕设交付阶段不强制引入 CI 平台流水线，优先保证本地可复现脚本验收闭环（启动脚本 + 回归脚本 + 报告产物）。

---

## 测试准备（一键生成报告）

```bash
cd deploy
bash scripts/generate-test-reports.sh
```

模式说明：
- `RUN_MODE=full`：通过网关生成回归+过期+缓存三类报告
- `RUN_MODE=direct`：仅生成缓存报告（用于无 Nacos/gateway 环境）
- `RUN_MODE=auto`（默认）：自动选择可用模式

---

## 启动前端

### PC 端

```bash
cd frontend-pc
npm install
npm run dev
```

### 移动端

```bash
cd frontend-mobile
npm install
npm run dev
```

---

## 关键网关接口（开发联调用）

- 注册：`POST /api/auth/register`
- 登录：`POST /api/auth/login`
- 刷新令牌：`POST /api/auth/refresh`
- 退出登录：`POST /api/auth/logout`
- 个人信息：`GET /api/users/me`
- 首页通知：`GET /api/notifications/home`
- 我的通知：`GET /api/notifications/my`
- 通知已读：`POST /api/notifications/{id}/read`
- 媒体首页推荐：`GET /api/media/home`
- 媒体推荐列表：`GET /api/media/recommendations?type=music|book|all`
- 帖子搜索：`GET /api/search/posts?keyword=xxx`
- 分区列表：`GET /api/forum/sections`
- 帖子列表：`GET /api/forum/posts`
- 发布帖子：`POST /api/forum/posts`
- 编辑帖子：`PUT /api/forum/posts/{id}`
- 删除帖子：`DELETE /api/forum/posts/{id}`
- 帖子详情：`GET /api/forum/posts/{id}`
- 发表评论：`POST /api/forum/posts/{id}/comments`
- 编辑评论：`PUT /api/forum/posts/{id}/comments/{commentId}`
- 删除评论：`DELETE /api/forum/posts/{id}/comments/{commentId}`
- 点赞：`POST /api/forum/posts/{id}/like`

鉴权规则：
- 匿名可访问：登录/注册、帖子列表、帖子详情
- 需要登录：个人信息、发帖、编辑/删除帖子、评论、删除评论、点赞
- 权限规则：帖子仅作者可编辑/删除；评论支持评论作者或帖子作者删除
- 点赞规则：同一用户对同一帖子仅可点赞一次
- 分区规则：发帖必须选择分区；列表支持按 `sectionId` 过滤
- 评论规则：支持二级评论（回复一级评论）；评论与帖子会返回简单编辑提示（如“该消息编辑于xx分钟前”）
- 首页常驻：PC/移动首页常驻通知、搜索、音乐推荐、书籍推荐板块
- 体验一致性：双端均提供加载态、错误重试、分页与筛选交互
- 会话一致性：双端均支持 401 自动 refresh、logout 服务端失效与本地状态同步
- 通知闭环：双端均提供“我的通知”入口并支持标记已读

基础安全（毕设可交付版）：
- Access Token + Refresh Token 双令牌
- 刷新令牌续签（保持同一会话，降低前端接入复杂度）
- 登出后会话立即失效（网关与鉴权服务都会校验 Redis 会话）
- 登录失败次数锁定（按用户名+来源IP进行短时锁定）
