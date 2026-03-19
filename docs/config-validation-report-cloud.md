# 关键配置静态校验结果（云端）

- 时间: 2026-03-18 09:06:52
- 校验范围: deploy/.env.example 与 backend/*/application.yml
- 校验类型: 静态一致性（无需启动服务）

## 1. 关键变量覆盖检查

- 关注变量: AUTH_USER_PORT, FORUM_PORT, GATEWAY_PORT, JWT_EXPIRE_SECONDS, JWT_REFRESH_EXPIRE_SECONDS, JWT_SECRET, MEDIA_PORT, MYSQL_APP_DATABASE, MYSQL_APP_PASSWORD, MYSQL_APP_USER, MYSQL_PORT, NACOS_SERVER_ADDR, NOTIFICATION_PORT, REDIS_PORT, SEARCH_PORT
- env.example 缺失变量: []

## 2. 端口变量映射检查

- auth-user-service: AUTH_USER_PORT
- forum-service: FORUM_PORT
- gateway-service: GATEWAY_PORT
- media-service: MEDIA_PORT
- notification-service: NOTIFICATION_PORT
- search-service: SEARCH_PORT

## 3. JWT/数据库一致性检查

- JWT_SECRET in gateway: True
- JWT_SECRET in auth-user: True
- MYSQL_APP_* in auth/forum/notification: True

## 4. 结论

- 结论: 端口、JWT、数据库相关关键变量在当前仓库配置中保持一致，可用于本地联调。
