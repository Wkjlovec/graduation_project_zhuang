#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

load_env() {
  if [ ! -f "${ENV_FILE}" ]; then
    echo "[ERROR] 未找到 ${ENV_FILE}。请先执行 start-infra-auto.sh。"
    exit 1
  fi
  # shellcheck source=/dev/null
  set -a
  source "${ENV_FILE}"
  set +a
}

use_docker_mode() {
  command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1
}

verify_local_mariadb() {
  local db="${MYSQL_APP_DATABASE:-forum_system}"
  local user="${MYSQL_APP_USER:-forum_user}"
  local pass="${MYSQL_APP_PASSWORD:-forum_pass_123}"
  local sql_cmd="mysql"
  if ! command -v mysql >/dev/null 2>&1 && command -v mariadb >/dev/null 2>&1; then
    sql_cmd="mariadb"
  fi
  local result
  result="$("${sql_cmd}" -u"${user}" -p"${pass}" -Nse "SHOW DATABASES LIKE '${db}';" 2>/dev/null || true)"
  if [ "${result}" != "${db}" ]; then
    echo "[ERROR] 本地 MySQL/MariaDB 验证失败，未检测到数据库 ${db}。"
    exit 1
  fi
  echo "[OK] 本地 MariaDB 数据库校验通过：${db}"
}

verify_local_redis() {
  if [ "$(redis-cli ping 2>/dev/null || true)" != "PONG" ]; then
    echo "[ERROR] 本地 Redis 验证失败。"
    exit 1
  fi
  echo "[OK] 本地 Redis 验证通过。"
}

verify_nacos_hint() {
  local nacos_url="http://127.0.0.1:${NACOS_PORT:-8848}/nacos"
  if curl -fsS "${nacos_url}" >/dev/null 2>&1; then
    echo "[OK] Nacos 可访问：${nacos_url}"
  else
    echo "[WARN] Nacos 不可访问：${nacos_url}"
    echo "[WARN] 若无 Nacos，请以 direct 模式启动后端。"
  fi
}

main() {
  load_env
  if use_docker_mode; then
    echo "[INFO] 检测到 Docker，使用容器模式验收基础设施。"
    bash "${ROOT_DIR}/scripts/verify-infra.sh"
    exit 0
  fi

  if ! command -v redis-cli >/dev/null 2>&1; then
    echo "[ERROR] 本地模式缺少 redis-cli，无法验收。"
    exit 1
  fi
  if ! command -v mysql >/dev/null 2>&1 && ! command -v mariadb >/dev/null 2>&1; then
    echo "[ERROR] 本地模式缺少 mysql/mariadb 客户端，无法验收。"
    exit 1
  fi
  verify_local_mariadb
  verify_local_redis
  verify_nacos_hint
  echo "[SUCCESS] 基础设施验收通过（auto 本地模式）。"
}

main "$@"
