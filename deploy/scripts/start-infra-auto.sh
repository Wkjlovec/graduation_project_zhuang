#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

load_env() {
  if [ ! -f "${ENV_FILE}" ]; then
    cp "${ROOT_DIR}/.env.example" "${ENV_FILE}"
    echo "[INFO] 未找到 .env，已基于 .env.example 自动创建。"
  fi
  # shellcheck source=/dev/null
  set -a
  source "${ENV_FILE}"
  set +a
}

use_docker_mode() {
  command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1
}

start_local_mariadb() {
  if command -v service >/dev/null 2>&1; then
    sudo service mariadb start >/dev/null 2>&1 || sudo service mysql start >/dev/null 2>&1 || true
  fi
  local sql_cmd="mariadb"
  if ! command -v mariadb >/dev/null 2>&1; then
    sql_cmd="mysql"
  fi
  if ! command -v "${sql_cmd}" >/dev/null 2>&1; then
    echo "[ERROR] 本地模式未检测到 mariadb/mysql 客户端。"
    exit 1
  fi
  sudo "${sql_cmd}" -e "CREATE DATABASE IF NOT EXISTS ${MYSQL_APP_DATABASE:-forum_system} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" >/dev/null
  sudo "${sql_cmd}" -e "CREATE USER IF NOT EXISTS '${MYSQL_APP_USER:-forum_user}'@'%' IDENTIFIED BY '${MYSQL_APP_PASSWORD:-forum_pass_123}';" >/dev/null
  sudo "${sql_cmd}" -e "GRANT ALL PRIVILEGES ON ${MYSQL_APP_DATABASE:-forum_system}.* TO '${MYSQL_APP_USER:-forum_user}'@'%'; FLUSH PRIVILEGES;" >/dev/null
  echo "[OK] 本地 MariaDB 已就绪。"
}

start_local_redis() {
  if command -v service >/dev/null 2>&1; then
    sudo service redis-server start >/dev/null 2>&1 || true
  fi
  if ! command -v redis-cli >/dev/null 2>&1; then
    echo "[ERROR] 本地模式未检测到 redis-cli。"
    exit 1
  fi
  if [ "$(redis-cli ping)" != "PONG" ]; then
    echo "[ERROR] Redis 未就绪。"
    exit 1
  fi
  echo "[OK] 本地 Redis 已就绪。"
}

check_nacos_hint() {
  local nacos_url="http://127.0.0.1:${NACOS_PORT:-8848}/nacos"
  if curl -fsS "${nacos_url}" >/dev/null 2>&1; then
    echo "[OK] Nacos 可访问：${nacos_url}"
  else
    echo "[WARN] Nacos 不可访问：${nacos_url}"
    echo "[WARN] 后端请使用 direct 模式启动：RUN_MODE=direct bash deploy/scripts/start-backend-all.sh"
  fi
}

main() {
  load_env
  if use_docker_mode; then
    echo "[INFO] 检测到 Docker，使用容器模式启动基础设施。"
    bash "${ROOT_DIR}/scripts/start-infra.sh"
    exit 0
  fi

  echo "[INFO] 未检测到 Docker，使用本地服务模式启动基础设施。"
  if ! command -v sudo >/dev/null 2>&1; then
    echo "[ERROR] 本地模式需要 sudo 启动数据库与 Redis。"
    exit 1
  fi
  start_local_mariadb
  start_local_redis
  check_nacos_hint
  echo "[SUCCESS] 基础设施启动完成（auto 本地模式）。"
}

main "$@"
