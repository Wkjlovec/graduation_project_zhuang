#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
RUNTIME_DIR="${ROOT_DIR}/.runtime"
PID_DIR="${RUNTIME_DIR}/pids"
MODE_FILE="${RUNTIME_DIR}/backend-mode"

load_env() {
  if [ ! -f "${ENV_FILE}" ]; then
    echo "[ERROR] 未找到 ${ENV_FILE}。请先执行 start-backend-all.sh。"
    exit 1
  fi
  # shellcheck source=/dev/null
  set -a
  source "${ENV_FILE}"
  set +a
}

check_prerequisites() {
  if ! command -v curl >/dev/null 2>&1; then
    echo "[ERROR] 未检测到 curl，无法执行健康检查。"
    exit 1
  fi
}

check_health() {
  local service_name="$1"
  local port="$2"
  local url="http://127.0.0.1:${port}/actuator/health"
  if curl -fsS "${url}" >/dev/null 2>&1; then
    echo "[OK] ${service_name} 健康检查通过：${url}"
    return 0
  fi
  echo "[ERROR] ${service_name} 健康检查失败：${url}"
  return 1
}

show_pid() {
  local service_name="$1"
  local pid_file="${PID_DIR}/${service_name}.pid"
  if [ -f "${pid_file}" ]; then
    local pid
    pid="$(cat "${pid_file}")"
    if kill -0 "${pid}" >/dev/null 2>&1; then
      echo "[INFO] ${service_name} PID=${pid}"
      return
    fi
  fi
  echo "[INFO] ${service_name} 未发现有效 PID 文件（可能非脚本启动）"
}

main() {
  load_env
  check_prerequisites

  local mode="full"
  if [ -f "${MODE_FILE}" ]; then
    mode="$(cat "${MODE_FILE}")"
  fi
  echo "[INFO] 当前后端模式：${mode}"

  local failed=0
  check_health "auth-user-service" "${AUTH_USER_PORT:-8081}" || failed=1
  check_health "forum-service" "${FORUM_PORT:-8082}" || failed=1
  check_health "notification-service" "${NOTIFICATION_PORT:-8083}" || failed=1
  check_health "media-service" "${MEDIA_PORT:-8084}" || failed=1
  check_health "search-service" "${SEARCH_PORT:-8085}" || failed=1
  if [ "${mode}" = "full" ]; then
    check_health "gateway-service" "${GATEWAY_PORT:-8080}" || failed=1
    if curl -fsS "http://127.0.0.1:${GATEWAY_PORT:-8080}/api/forum/sections" >/dev/null 2>&1; then
      echo "[OK] 网关业务路由可用：/api/forum/sections"
    else
      echo "[ERROR] 网关业务路由失败：/api/forum/sections"
      failed=1
    fi
  else
    if curl -fsS "http://127.0.0.1:${FORUM_PORT:-8082}/sections" >/dev/null 2>&1; then
      echo "[OK] forum 业务接口可用：/sections"
    else
      echo "[ERROR] forum 业务接口失败：/sections"
      failed=1
    fi
  fi

  show_pid "auth-user-service"
  show_pid "forum-service"
  show_pid "notification-service"
  show_pid "media-service"
  show_pid "search-service"
  if [ "${mode}" = "full" ]; then
    show_pid "gateway-service"
  fi

  if [ "${failed}" -ne 0 ]; then
    echo "[FAILED] 后端服务验活失败。"
    exit 1
  fi
  echo "[SUCCESS] 后端服务验活通过。"
}

main "$@"
