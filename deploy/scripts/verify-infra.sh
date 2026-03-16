#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

if [ ! -f "${ENV_FILE}" ]; then
  echo "[ERROR] 未找到 ${ENV_FILE}。请先执行 start-infra.sh。"
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] 未检测到 docker 命令。"
  exit 1
fi

echo "[INFO] 检查容器运行状态..."
docker compose --env-file "${ENV_FILE}" -f "${ROOT_DIR}/docker-compose.yml" ps

echo "[INFO] 检查 Redis 连通性..."
redis_ping="$(docker compose --env-file "${ENV_FILE}" -f "${ROOT_DIR}/docker-compose.yml" exec -T redis redis-cli ping)"
if [ "${redis_ping}" != "PONG" ]; then
  echo "[ERROR] Redis 校验失败，返回值：${redis_ping}"
  exit 1
fi
echo "[OK] Redis 返回 PONG。"

echo "[INFO] 检查 MySQL 初始化结果..."
mysql_check="$(docker compose --env-file "${ENV_FILE}" -f "${ROOT_DIR}/docker-compose.yml" exec -T mysql mysql -uforum_user -pforum_pass_123 -Nse \"SHOW DATABASES LIKE 'forum_system';\")"
if [ "${mysql_check}" != "forum_system" ]; then
  echo "[ERROR] MySQL 未检测到 forum_system 数据库。"
  exit 1
fi
echo "[OK] MySQL forum_system 数据库已存在。"

nacos_port="$(grep -E '^NACOS_PORT=' "${ENV_FILE}" | cut -d'=' -f2 || true)"
nacos_port="${nacos_port:-8848}"
echo "[INFO] 检查 Nacos HTTP 入口..."
if ! curl -fsS "http://127.0.0.1:${nacos_port}/nacos" >/dev/null; then
  echo "[ERROR] Nacos HTTP 访问失败。"
  exit 1
fi
echo "[OK] Nacos HTTP 可访问： http://127.0.0.1:${nacos_port}/nacos"

echo "[SUCCESS] 基础设施验收通过。"
