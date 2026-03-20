#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
BACKEND_DIR="${ROOT_DIR}/../backend"
RUNTIME_DIR="${ROOT_DIR}/.runtime"
PID_DIR="${RUNTIME_DIR}/pids"
LOG_DIR="${RUNTIME_DIR}/logs"
BUILD_LOG="${LOG_DIR}/common-lib-build.log"
MODE_FILE="${RUNTIME_DIR}/backend-mode"
RUN_MODE="${RUN_MODE:-auto}"

# 模式说明：
# - full: 依赖 Nacos，启动 auth/forum/notification/media/search/gateway 全链路
# - direct: 无 Nacos 场景，启动 auth/forum/notification/media/search（不启动 gateway）
# - auto: 运行时自动探测 Nacos 可达性并选择模式

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

check_prerequisites() {
  if ! command -v mvn >/dev/null 2>&1; then
    echo "[ERROR] 未检测到 mvn，请先安装 Maven 并确保 mvn -v 可用。"
    exit 1
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "[ERROR] 未检测到 curl，无法进行健康检查。"
    exit 1
  fi
  if [ ! -d "${BACKEND_DIR}" ]; then
    echo "[ERROR] 未找到 backend 目录：${BACKEND_DIR}"
    exit 1
  fi
}

prepare_runtime() {
  mkdir -p "${PID_DIR}" "${LOG_DIR}"
}

detect_mode() {
  local nacos_url="http://127.0.0.1:${NACOS_PORT:-8848}/nacos"
  if [ "${RUN_MODE}" = "full" ]; then
    if ! curl -fsS "${nacos_url}" >/dev/null 2>&1; then
      echo "[ERROR] RUN_MODE=full 但 Nacos 不可访问：${nacos_url}"
      echo "[ERROR] 请先启动基础设施：bash deploy/scripts/start-infra.sh"
      exit 1
    fi
    echo "full" > "${MODE_FILE}"
    return
  fi
  if [ "${RUN_MODE}" = "direct" ]; then
    echo "direct" > "${MODE_FILE}"
    return
  fi
  if [ "${RUN_MODE}" != "auto" ]; then
    echo "[ERROR] RUN_MODE 仅支持 auto/full/direct，当前值：${RUN_MODE}"
    exit 1
  fi

  if curl -fsS "${nacos_url}" >/dev/null 2>&1; then
    echo "[INFO] 检测到 Nacos 可用，使用 full 模式。"
    echo "full" > "${MODE_FILE}"
  else
    echo "[WARN] 未检测到 Nacos，使用 direct 模式（不启动 gateway）。"
    echo "direct" > "${MODE_FILE}"
  fi
}

build_common_lib() {
  echo "[INFO] 预构建 common-lib（确保多模块依赖可用）..."
  (
    cd "${BACKEND_DIR}"
    mvn -pl common-lib -am -DskipTests install >"${BUILD_LOG}" 2>&1
  )
  echo "[OK] common-lib 构建完成。日志：${BUILD_LOG}"
}

normalize_host() {
  local current="$1"
  local fallback="$2"
  if [ -z "${current}" ] || [[ "${current}" == *"REDACTED"* ]]; then
    echo "${fallback}"
    return
  fi
  echo "${current}"
}

wait_health() {
  local service_name="$1"
  local port="$2"
  local pid="$3"
  local url="http://127.0.0.1:${port}/actuator/health"
  for i in {1..90}; do
    if curl -fsS "${url}" >/dev/null 2>&1; then
      echo "[OK] ${service_name} 健康检查通过：${url}"
      return 0
    fi
    if ! kill -0 "${pid}" >/dev/null 2>&1; then
      echo "[ERROR] ${service_name} 进程提前退出，请检查日志：${LOG_DIR}/${service_name}.log"
      exit 1
    fi
    sleep 2
  done
  echo "[ERROR] ${service_name} 健康检查超时，请检查日志：${LOG_DIR}/${service_name}.log"
  exit 1
}

start_service() {
  local service_name="$1"
  local port="$2"
  local module_dir="${BACKEND_DIR}/${service_name}"
  local pid_file="${PID_DIR}/${service_name}.pid"
  local log_file="${LOG_DIR}/${service_name}.log"

  if [ ! -d "${module_dir}" ]; then
    echo "[ERROR] 服务目录不存在：${module_dir}"
    exit 1
  fi

  if curl -fsS "http://127.0.0.1:${port}/actuator/health" >/dev/null 2>&1; then
    echo "[WARN] ${service_name} 已在端口 ${port} 运行，跳过启动。"
    return 0
  fi

  if [ -f "${pid_file}" ]; then
    old_pid="$(cat "${pid_file}")"
    if kill -0 "${old_pid}" >/dev/null 2>&1; then
      echo "[WARN] ${service_name} 进程已存在（PID=${old_pid}），跳过启动。"
      return 0
    fi
    rm -f "${pid_file}"
  fi

  echo "[INFO] 启动 ${service_name}（port=${port}）..."
  (
    cd "${module_dir}"
    mvn spring-boot:run >"${log_file}" 2>&1
  ) &
  local pid=$!
  echo "${pid}" > "${pid_file}"
  wait_health "${service_name}" "${port}" "${pid}"
}

main() {
  load_env
  check_prerequisites
  prepare_runtime
  detect_mode
  build_common_lib

  local mode
  mode="$(cat "${MODE_FILE}")"

  if [ "${mode}" = "direct" ]; then
    export MYSQL_HOST="127.0.0.1"
    export REDIS_HOST="127.0.0.1"
    export SPRING_CLOUD_NACOS_DISCOVERY_ENABLED=false
    export SPRING_CLOUD_NACOS_DISCOVERY_REGISTER_ENABLED=false
    export GATEWAY_DISCOVERY_LOCATOR_ENABLED=false
    export AUTH_ROUTE_URI="http://127.0.0.1:${AUTH_USER_PORT:-8081}"
    export AUTH_USER_ROUTE_URI="http://127.0.0.1:${AUTH_USER_PORT:-8081}"
    export FORUM_ROUTE_URI="http://127.0.0.1:${FORUM_PORT:-8082}"
    export NOTIFICATION_ROUTE_URI="http://127.0.0.1:${NOTIFICATION_PORT:-8083}"
    export MEDIA_ROUTE_URI="http://127.0.0.1:${MEDIA_PORT:-8084}"
    export SEARCH_ROUTE_URI="http://127.0.0.1:${SEARCH_PORT:-8085}"
    export FORUM_SERVICE_URL="http://127.0.0.1:${FORUM_PORT:-8082}"
    echo "[INFO] direct 模式：禁用 Nacos 注册发现，search 直连 forum，gateway 走静态路由。"
  else
    export MYSQL_HOST
    MYSQL_HOST="$(normalize_host "${MYSQL_HOST:-}" "127.0.0.1")"
    export REDIS_HOST
    REDIS_HOST="$(normalize_host "${REDIS_HOST:-}" "127.0.0.1")"
  fi
  export NACOS_SERVER_ADDR="${NACOS_SERVER_ADDR:-127.0.0.1:${NACOS_PORT:-8848}}"
  export SPRING_DATA_REDIS_HOST="${REDIS_HOST}"
  export SPRING_DATA_REDIS_PORT="${REDIS_PORT:-6379}"

  start_service "auth-user-service" "${AUTH_USER_PORT:-8081}"
  start_service "forum-service" "${FORUM_PORT:-8082}"
  start_service "notification-service" "${NOTIFICATION_PORT:-8083}"
  start_service "media-service" "${MEDIA_PORT:-8084}"
  start_service "search-service" "${SEARCH_PORT:-8085}"
  start_service "gateway-service" "${GATEWAY_PORT:-8080}"

  if [ "${mode}" = "full" ]; then
    if curl -fsS "http://127.0.0.1:${GATEWAY_PORT:-8080}/api/forum/sections" >/dev/null 2>&1; then
      echo "[OK] 网关业务路由可用：/api/forum/sections"
    else
      echo "[ERROR] 网关已启动，但业务路由检查失败：/api/forum/sections"
      exit 1
    fi
    echo "[SUCCESS] 后端全服务启动完成（full 模式）。"
  else
    if curl -fsS "http://127.0.0.1:${GATEWAY_PORT:-8080}/api/forum/sections" >/dev/null 2>&1; then
      echo "[OK] direct 模式下网关静态路由可用：/api/forum/sections"
    else
      echo "[ERROR] direct 模式下网关静态路由检查失败：/api/forum/sections"
      exit 1
    fi
    echo "[SUCCESS] 后端服务启动完成（direct 模式，含 gateway 静态路由）。"
  fi
  echo "[INFO] 日志目录：${LOG_DIR}"
  echo "[INFO] 当前模式：${mode}"
}

main "$@"
