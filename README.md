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

---

## 目录结构

```text
backend/
  pom.xml
  common-lib/
  gateway-service/
  auth-user-service/
  forum-service/
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
- MySQL: `3306`
- Redis: `6379`

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

再开一个终端启动 `gateway-service`：

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
- 个人信息：`GET /api/users/me`
- 帖子列表：`GET /api/forum/posts`
- 发布帖子：`POST /api/forum/posts`
- 帖子详情：`GET /api/forum/posts/{id}`
- 发表评论：`POST /api/forum/posts/{id}/comments`
- 点赞：`POST /api/forum/posts/{id}/like`
