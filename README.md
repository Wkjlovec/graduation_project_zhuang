# 微服务论坛系统（毕业设计）

本仓库用于实现课题：**“微服务架构的论坛系统实现（支持 PC 端 + 移动端）”**。

当前已完成：**步骤 1（目录初始化）**、**步骤 2（基础设施 Docker 化）**。

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
  mysql/init/01-init-databases.sql
  nginx/
docs/
```

---

## 2. 基础设施说明（第 2 步）

已提供以下基础服务：

- **Nacos**：微服务注册与配置中心
- **MySQL 8.4**：业务数据库
- **Redis 7.4**：缓存与会话

### 服务端口（默认）

- Nacos: `8848`
- MySQL: `3306`
- Redis: `6379`

---

## 3. 前置条件（零基础必看）

你需要先安装并启动 Docker（Windows/Mac 推荐 Docker Desktop，Linux 推荐 Docker Engine）。

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

### 4.3 启动基础设施

```bash
docker compose up -d
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
- User: `forum_user`
- Password: `forum_pass_123`
- Database: `forum_system`

3) Redis 连接信息（给后端服务用）：
- Host: `localhost`
- Port: `6379`

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

### 启动前检查脚本（可选）

```bash
cd /workspace/deploy
bash check-prerequisites.sh
```
