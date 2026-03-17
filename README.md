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
bash check-prerequisites.sh
bash scripts/start-infra.sh
bash scripts/verify-infra.sh
```

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

## 启动后端微服务

先启动 `auth-user-service`：

```bash
cd backend
mvn -pl auth-user-service -am spring-boot:run
```

再开一个终端启动 `forum-service`：

```bash
cd backend
mvn -pl forum-service -am spring-boot:run
```

再开一个终端启动 `notification-service`：

```bash
cd backend
mvn -pl notification-service -am spring-boot:run
```

再开一个终端启动 `media-service`：

```bash
cd backend
mvn -pl media-service -am spring-boot:run
```

再开一个终端启动 `search-service`：

```bash
cd backend
mvn -pl search-service -am spring-boot:run
```

最后启动 `gateway-service`：

```bash
cd backend
mvn -pl gateway-service -am spring-boot:run
```

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

基础安全（毕设可交付版）：
- Access Token + Refresh Token 双令牌
- 刷新令牌续签（保持同一会话，降低前端接入复杂度）
- 登出后会话立即失效（网关与鉴权服务都会校验 Redis 会话）
- 登录失败次数锁定（按用户名+来源IP进行短时锁定）
