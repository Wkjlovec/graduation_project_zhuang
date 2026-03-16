# 微服务论坛系统（毕业设计）

本仓库用于实现课题：**“微服务架构的论坛系统实现（支持 PC 端 + 移动端）”**。

当前已完成：**步骤 1（目录初始化）**、**步骤 2（基础设施 Docker 化）**、**步骤 3（网关 + 注册发现）**。

---

## 1. 当前目录结构

```text
backend/
  gateway-service/
  auth-user-service/
  forum-service/
  media-service/
  common-lib/
  sql/
frontend-pc/
frontend-mobile/
deploy/
  docker-compose.yml
  .env.example
  check-prerequisites.sh
  scripts/start-infra.sh
  scripts/verify-infra.sh
  nginx/
docs/
```

---

## 2. 基础设施说明（第 2 步）

已提供以下基础服务：

- **Nacos**：微服务注册与配置中心
- **MySQL 8.4**：业务数据库
- **Redis 7.4**：缓存与会话
- **数据持久化卷**：MySQL / Redis / Nacos 已持久化

### 服务端口（默认）

- Nacos: `8848`
- MySQL: `3306`
- Redis: `6379`

---

## 3. 前置条件（零基础必看）

你需要先安装并启动 Docker（Windows/Mac 推荐 Docker Desktop，Linux 推荐 Docker Engine）。
如果你安装的是 **Docker Desktop**，通常已经包含 Docker Engine 与 Docker Compose，不需要额外单独安装 Engine。

检查方式：

```bash
docker --version
docker compose version
```

如果提示 `command not found`，说明 Docker 尚未安装完成，先安装再继续。

---

## 4. 零基础启动指南

下面每一条都可以直接复制执行。

### 4.1 进入部署目录

```bash
cd /workspace/deploy
```

### 4.2 准备环境变量文件

```bash
cp .env.example .env
```

> 说明：`.env` 用来放本地参数（端口、密码）。  
> 你可以先不改，直接用默认值跑起来。

默认业务库参数（可在 `.env` 修改）：
- `MYSQL_APP_DATABASE=forum_system`
- `MYSQL_APP_USER=forum_user`
- `MYSQL_APP_PASSWORD=forum_pass_123`

### 4.3 启动基础设施

```bash
bash scripts/start-infra.sh
```

### 4.4 查看容器状态

```bash
docker compose ps
```

你应该看到：
- `forum-mysql` 状态为 `healthy`
- `forum-redis` 状态为 `healthy`
- `forum-nacos` 状态为 `running`

### 4.5 验证是否可访问

1) 浏览器打开 Nacos 控制台：  
`http://localhost:8848/nacos`

2) MySQL 连接信息（给后端服务用）：
- Host: `localhost`
- Port: `3306`
- User: `.env` 中的 `MYSQL_APP_USER`
- Password: `.env` 中的 `MYSQL_APP_PASSWORD`
- Database: `.env` 中的 `MYSQL_APP_DATABASE`

3) Redis 连接信息（给后端服务用）：
- Host: `localhost`
- Port: `6379`

你也可以执行自动化验收：

```bash
bash scripts/verify-infra.sh
```

---

## 5. 常用命令

### 停止服务

```bash
docker compose down
```

### 停止并删除数据卷（危险：会清空 MySQL/Redis 数据）

```bash
docker compose down -v
```

> 注意：如果你修改了 `.env` 里的 MySQL 数据库名/账号/密码，且容器已经初始化过一次，需要执行 `docker compose down -v` 后重启，新的参数才会生效。

### 启动前检查脚本（可选）

```bash
cd /workspace/deploy
bash check-prerequisites.sh
```

---

## 6. 第 3 步：网关 + 注册发现（Nacos）

后端已新增 3 个 Maven 模块：

- `common-lib`：公共常量
- `auth-user-service`：最小用户服务（用于注册发现联调）
- `gateway-service`：Spring Cloud Gateway 网关

### 6.1 启动顺序（先基础设施，再微服务）

1) 启动基础设施（步骤 2）  
2) 启动 `auth-user-service`  
3) 启动 `gateway-service`

### 6.2 在本地启动后端服务

```bash
cd /workspace/backend
mvn -pl auth-user-service -am spring-boot:run
```

再开一个终端：

```bash
cd /workspace/backend
mvn -pl gateway-service -am spring-boot:run
```

### 6.3 联调验证

1) 查看 Nacos 控制台服务列表：  
`http://localhost:8848/nacos`  
应出现：
- `auth-user-service`
- `gateway-service`

2) 通过网关访问用户服务探针接口：

```bash
curl -H "X-Request-Id: demo-001" http://localhost:8080/api/users/ping
```

返回中应包含：
- `message=auth-user-service is reachable`
- `service=auth-user-service`
