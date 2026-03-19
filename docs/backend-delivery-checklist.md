# 后端全服务启动与本地校验清单（交付版）

本文档用于“从零到可联调”一次性检查后端交付完整度，重点覆盖：

1. 服务启动顺序（含验活）  
2. 常见报错排查  
3. 关键配置本地校验清单（端口 / JWT / 数据库）

---

## 1. 启动顺序（脚本级一键）

### 1.1 启动基础设施（一步）

```bash
cd deploy
cp .env.example .env
bash check-prerequisites.sh
bash scripts/start-infra.sh
bash scripts/verify-infra.sh
```

通过标准：
- `docker compose ps` 中 `mysql`、`redis` 为 healthy
- `http://127.0.0.1:8848/nacos` 可打开

### 1.2 启动后端微服务（一键）

```bash
cd deploy
bash scripts/start-backend-all.sh
```

脚本启动顺序固定为：
- `auth-user-service`
- `forum-service`
- `notification-service`
- `media-service`
- `search-service`
- `gateway-service`（最后启动）

脚本会在每个服务启动后自动执行 `/actuator/health` 检查。

### 1.3 一键验活与停止

验活：

```bash
cd deploy
bash scripts/verify-backend-all.sh
```

停止：

```bash
cd deploy
bash scripts/stop-backend-all.sh
```

### 1.4 启动后快速验活（手工备选）

```bash
curl -fsS http://127.0.0.1:8081/actuator/health
curl -fsS http://127.0.0.1:8082/actuator/health
curl -fsS http://127.0.0.1:8083/actuator/health
curl -fsS http://127.0.0.1:8084/actuator/health
curl -fsS http://127.0.0.1:8085/actuator/health
curl -fsS http://127.0.0.1:8080/actuator/health
curl -fsS http://127.0.0.1:8080/api/forum/sections
```

通过标准：
- 每个 `actuator/health` 返回 `{"status":"UP"}`（字段顺序可能不同）
- 网关 `GET /api/forum/sections` 返回 code=0 的业务响应

---

## 2. 常见报错排查（高频）

### 2.1 `mvn: command not found`

原因：本机 Maven 未安装或 PATH 未生效。  
排查：

```bash
mvn -v
java -version
```

处理：安装 Maven 3.9+，并确认 `mvn -v` 可用后重试。

### 2.2 端口占用（Address already in use）

常见端口：`8080~8085`、`3306`、`6379`、`8848`。  
排查（Linux/macOS）：

```bash
lsof -i :8080
```

排查（Windows PowerShell）：

```powershell
netstat -ano | findstr :8080
```

处理：结束占用进程，或在 `.env` 中改端口并保持前后端配置一致。

### 2.3 Nacos 没有服务注册

现象：Nacos 控制台看不到某服务。  
排查：
- 确认 Nacos 可访问：`http://127.0.0.1:8848/nacos`
- 确认服务配置 `NACOS_SERVER_ADDR=127.0.0.1:8848`
- 查看对应服务启动日志是否有连接失败报错

### 2.4 网关返回 401（登录后仍失败）

高频原因：`gateway-service` 与 `auth-user-service` 的 `JWT_SECRET` 不一致。  
排查：
- `deploy/.env` 中 `JWT_SECRET` 仅保留一个值
- 重启 `auth-user-service` 与 `gateway-service`

### 2.5 数据库连接失败（Access denied / Communications link failure）

排查：
- `docker compose ps` 中 MySQL healthy
- `.env` 的 `MYSQL_APP_DATABASE / MYSQL_APP_USER / MYSQL_APP_PASSWORD` 与服务配置一致
- 账号是否有对应数据库权限

### 2.6 网关 404

排查：
- 是否通过网关前缀访问（如 `/api/forum/posts`）
- 是否误直接调用内部服务路径
- 确认 gateway 已启动且目标服务已注册到 Nacos

---

## 3. 关键配置本地校验清单（可打勾）

### 3.1 端口清单

- [ ] `GATEWAY_PORT=8080`
- [ ] `AUTH_USER_PORT=8081`
- [ ] `FORUM_PORT=8082`
- [ ] `NOTIFICATION_PORT=8083`
- [ ] `MEDIA_PORT=8084`
- [ ] `SEARCH_PORT=8085`
- [ ] `MYSQL_PORT=3306`
- [ ] `REDIS_PORT=6379`
- [ ] `NACOS_PORT=8848`
- [ ] 上述端口无冲突（本机无重复占用）

### 3.2 JWT 清单

- [ ] `deploy/.env` 中已设置 `JWT_SECRET`（长度 >= 32）
- [ ] `JWT_SECRET` 被 `auth-user-service` 与 `gateway-service` 统一读取
- [ ] `JWT_EXPIRE_SECONDS`、`JWT_REFRESH_EXPIRE_SECONDS` 符合预期
- [ ] 修改 JWT 参数后已重启 auth + gateway

### 3.3 数据库清单

- [ ] `.env` 中 `MYSQL_APP_DATABASE`、`MYSQL_APP_USER`、`MYSQL_APP_PASSWORD` 已配置
- [ ] MySQL 容器 healthy
- [ ] `SHOW DATABASES LIKE 'forum_system';`（或你的库名）可查到目标数据库
- [ ] auth/forum/notification 三个服务使用同一数据库连接参数

### 3.4 Redis 与注册中心清单

- [ ] Redis `PING` 返回 `PONG`
- [ ] Nacos 可访问并显示 6 个服务实例（gateway + 5 个业务服务）

### 3.5 网关业务清单

- [ ] `GET /api/forum/sections` 正常返回
- [ ] 登录 -> 发帖 -> 评论 -> 搜索 主链路可跑通
- [ ] refresh、logout、我的通知/已读可正常联调

---

## 4. 仓库静态配置一致性校验（无需启动服务）

执行：

```bash
python3 - <<'PY'
import re
from pathlib import Path
root=Path('/workspace')
env=(root/'deploy/.env.example').read_text(encoding='utf-8')
env_keys={line.split('=',1)[0].strip() for line in env.splitlines() if line.strip() and not line.strip().startswith('#') and '=' in line}
files=list((root/'backend').glob('*/src/main/resources/application.yml'))
pat=re.compile(r'\\$\\{([A-Z0-9_]+)(?::[^}]*)?\\}')
used=set()
for f in files:
    used |= set(pat.findall(f.read_text(encoding='utf-8')))
focus={'GATEWAY_PORT','AUTH_USER_PORT','FORUM_PORT','NOTIFICATION_PORT','MEDIA_PORT','SEARCH_PORT','MYSQL_PORT','MYSQL_APP_DATABASE','MYSQL_APP_USER','MYSQL_APP_PASSWORD','JWT_SECRET','JWT_EXPIRE_SECONDS','JWT_REFRESH_EXPIRE_SECONDS','NACOS_SERVER_ADDR','REDIS_PORT'}
missing=[k for k in sorted((used & focus)-env_keys) if k not in {'NACOS_SERVER_ADDR'}]
print('missing_in_env_example=', missing)
PY
```

预期：
- `missing_in_env_example=[]`

本轮云端执行产物：
- `docs/config-validation-report-cloud.md`

---

## 5. CI 取舍说明（本科毕设）

CI（持续集成）指代码提交后自动执行构建、测试、质量检查的流水线。

本项目当前阶段的取舍：
- 不强制引入 CI 平台流水线（非本科毕设硬性要求）
- 以“本地可复现脚本验收闭环”替代：
  - 基础设施一键脚本
  - 后端全服务一键脚本
  - 回归与缓存基准脚本
  - 报告产物落盘
