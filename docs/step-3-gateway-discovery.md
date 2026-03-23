# 步骤 3：网关 + 注册发现（零基础联调指南）

本步骤目标：让 `auth-user-service` 与 `gateway-service` 都注册到 Nacos，并通过网关转发请求。

## 1. 前置条件

1) 基础设施已启动（步骤 2）  
2) 本机已安装 Java 17 与 Maven  

检查命令：

```bash
java -version
mvn -version
```

## 2. 启动用户服务

```bash
cd /workspace/backend
mvn -pl auth-user-service -am spring-boot:run
```

默认端口：`8081`

## 3. 启动网关服务

新开一个终端：

```bash
cd /workspace/backend
mvn -pl gateway-service -am spring-boot:run
```

默认端口：`8080`

## 4. 验证注册发现

打开 Nacos：`http://localhost:8848/nacos`  
服务列表应有：

- `auth-user-service`
- `gateway-service`

## 5. 验证网关路由

执行：

```bash
curl -H "X-Request-Id: test-123" http://localhost:8080/api/users/ping
```

预期返回示例：

```json
{
  "message": "auth-user-service is reachable",
  "service": "auth-user-service",
  "time": "2026-03-16T18:30:00+08:00",
  "requestId": "test-123"
}
```

## 6. 常见问题

1) Nacos 没有服务注册  
确认两服务配置里的 `NACOS_SERVER_ADDR` 指向 `127.0.0.1:8848` 且 Nacos 已启动。

2) 网关访问 404  
确认请求路径为：`/api/users/ping`。  
网关会去掉 `/api` 前缀，再转发到用户服务的 `/users/ping`。
