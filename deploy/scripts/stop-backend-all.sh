#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="${ROOT_DIR}/.runtime"
PID_DIR="${RUNTIME_DIR}/pids"
MODE_FILE="${RUNTIME_DIR}/backend-mode"

stop_service() {
  local service_name="$1"
  local pid_file="${PID_DIR}/${service_name}.pid"

  if [ ! -f "${pid_file}" ]; then
    echo "[INFO] ${service_name} 未发现 PID 文件，跳过。"
    return 0
  fi

  local pid
  pid="$(cat "${pid_file}")"
  if ! kill -0 "${pid}" >/dev/null 2>&1; then
    echo "[WARN] ${service_name} PID=${pid} 不存在，清理 PID 文件。"
    rm -f "${pid_file}"
    return 0
  fi

  echo "[INFO] 停止 ${service_name}（PID=${pid}）..."
  kill "${pid}" >/dev/null 2>&1 || true
  for _ in {1..20}; do
    if ! kill -0 "${pid}" >/dev/null 2>&1; then
      rm -f "${pid_file}"
      echo "[OK] ${service_name} 已停止。"
      return 0
    fi
    sleep 1
  done

  echo "[WARN] ${service_name} 未在预期时间内退出，执行强制停止。"
  kill -9 "${pid}" >/dev/null 2>&1 || true
  rm -f "${pid_file}"
}

main() {
  mkdir -p "${PID_DIR}"
  stop_service "gateway-service"
  stop_service "search-service"
  stop_service "media-service"
  stop_service "notification-service"
  stop_service "forum-service"
  stop_service "auth-user-service"
  rm -f "${MODE_FILE}"
  echo "[SUCCESS] 后端服务停止流程完成。"
}

main "$@"
