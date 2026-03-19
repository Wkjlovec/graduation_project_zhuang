#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8080}"
EXPIRY_WAIT_SECONDS="${EXPIRY_WAIT_SECONDS:-12}"

check_gateway() {
  if ! command -v curl >/dev/null 2>&1; then
    echo "[ERROR] 未检测到 curl，无法检测网关可达性。"
    exit 1
  fi
  if ! curl -fsS "${BASE_URL}/actuator/health" >/dev/null 2>&1; then
    echo "[ERROR] 网关不可达：${BASE_URL}/actuator/health"
    echo "[ERROR] 请先启动基础设施与全部后端服务后再执行。"
    exit 1
  fi
}

main() {
  check_gateway
  echo "[INFO] 生成基础回归报告..."
  python3 deploy/scripts/run_system_regression.py --base-url "${BASE_URL}" --report-file docs/regression-report.md

  echo "[INFO] 生成过期场景回归报告..."
  python3 deploy/scripts/run_system_regression.py \
    --base-url "${BASE_URL}" \
    --verify-expiry \
    --expiry-wait-seconds "${EXPIRY_WAIT_SECONDS}" \
    --report-file docs/regression-report-expiry.md

  echo "[INFO] 生成缓存对比报告..."
  python3 deploy/scripts/benchmark_forum_cache.py --base-url "${BASE_URL}" --report-file docs/cache-benchmark-report.md

  echo "[SUCCESS] 报告生成完成："
  echo "  - docs/regression-report.md"
  echo "  - docs/regression-report-expiry.md"
  echo "  - docs/cache-benchmark-report.md"
}

main "$@"
