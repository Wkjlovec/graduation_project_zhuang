#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] 未检测到 docker 命令，请先安装并启动 Docker Desktop。"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "[ERROR] 未检测到 docker compose，请先安装支持 compose 的 Docker 版本。"
  exit 1
fi

if [ ! -f "${ENV_FILE}" ]; then
  cp "${ROOT_DIR}/.env.example" "${ENV_FILE}"
  echo "[INFO] 未找到 .env，已基于 .env.example 自动创建。"
fi

echo "[INFO] 正在启动基础设施容器（Nacos/MySQL/Redis）..."
docker compose --env-file "${ENV_FILE}" -f "${ROOT_DIR}/docker-compose.yml" up -d

echo "[INFO] 正在等待 MySQL 与 Redis 进入 healthy 状态..."
for i in {1..30}; do
  mysql_status="$(docker inspect -f '{{.State.Health.Status}}' forum-mysql 2>/dev/null || true)"
  redis_status="$(docker inspect -f '{{.State.Health.Status}}' forum-redis 2>/dev/null || true)"
  if [ "${mysql_status}" = "healthy" ] && [ "${redis_status}" = "healthy" ]; then
    echo "[OK] MySQL 与 Redis 已健康。"
    break
  fi
  if [ "${i}" -eq 30 ]; then
    echo "[ERROR] 等待超时，请执行 'docker compose -f ${ROOT_DIR}/docker-compose.yml logs' 查看日志。"
    exit 1
  fi
  sleep 2
done

echo "[INFO] 正在等待 Nacos HTTP 入口就绪..."
nacos_port="$(grep -E '^NACOS_PORT=' "${ENV_FILE}" | cut -d'=' -f2 || true)"
nacos_port="${nacos_port:-8848}"
for i in {1..45}; do
  if curl -fsS "http://127.0.0.1:${nacos_port}/nacos" >/dev/null 2>&1; then
    echo "[OK] Nacos 已就绪： http://127.0.0.1:${nacos_port}/nacos"
    break
  fi
  if [ "${i}" -eq 45 ]; then
    echo "[ERROR] Nacos 未在预期时间内就绪，请检查容器日志。"
    exit 1
  fi
  sleep 2
done

echo "[SUCCESS] 基础设施启动完成。"
