#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8080}"
FORUM_BASE_URL="${FORUM_BASE_URL:-http://127.0.0.1:8082}"
EXPIRY_WAIT_SECONDS="${EXPIRY_WAIT_SECONDS:-12}"
RUN_MODE="${RUN_MODE:-auto}"

# 模式说明：
# - full: 必须可访问网关，生成回归+过期+缓存三类报告
# - direct: 直接对 forum-service 生成缓存报告（用于无 Nacos/gateway 场景）
# - auto: 优先 full，失败则显式切换 direct

check_gateway() {
  if ! command -v curl >/dev/null 2>&1; then
    echo "[ERROR] 未检测到 curl，无法检测网关可达性。"
    exit 1
  fi
  if ! curl -fsS "${BASE_URL}/actuator/health" >/dev/null 2>&1; then
    return 1
  fi
  return 0
}

check_forum_direct() {
  curl -fsS "${FORUM_BASE_URL}/actuator/health" >/dev/null 2>&1
}

run_full() {
  echo "[INFO] 生成基础回归报告..."
  python3 deploy/scripts/run_system_regression.py \
    --base-url "${BASE_URL}" \
    --report-file docs/regression-report.md \
    --security-report-file docs/security-test-report.md

  echo "[INFO] 生成过期场景回归报告..."
  python3 deploy/scripts/run_system_regression.py \
    --base-url "${BASE_URL}" \
    --verify-expiry \
    --expiry-wait-seconds "${EXPIRY_WAIT_SECONDS}" \
    --report-file docs/regression-report-expiry.md \
    --security-report-file docs/security-test-report-expiry.md

  echo "[INFO] 生成缓存对比报告..."
  python3 deploy/scripts/benchmark_forum_cache.py \
    --base-url "${BASE_URL}" \
    --warm-runs 30 \
    --report-file docs/cache-benchmark-report.md
  python3 deploy/scripts/benchmark_forum_cache.py \
    --base-url "${BASE_URL}" \
    --warm-runs 30 \
    --report-file docs/evidence-cache-benchmark.md

  echo "[INFO] 生成并发负载测试报告..."
  python3 deploy/scripts/load_test_concurrent.py \
    --base-url "${BASE_URL}" \
    --path "/api/forum/posts?page=0&size=10" \
    --concurrency-levels "10,50,100" \
    --requests-per-user 20 \
    --report-file docs/concurrent-load-report.md
}

run_direct() {
  echo "[WARN] 当前使用 direct 模式，仅生成缓存报告（回归报告依赖网关/Nacos）。"
  python3 deploy/scripts/benchmark_forum_cache.py \
    --base-url "${FORUM_BASE_URL}" \
    --path /posts/1 \
    --warm-runs 30 \
    --report-file docs/cache-benchmark-report.md
  python3 deploy/scripts/benchmark_forum_cache.py \
    --base-url "${FORUM_BASE_URL}" \
    --path /posts/1 \
    --warm-runs 30 \
    --report-file docs/evidence-cache-benchmark.md

  echo "[INFO] 生成并发负载测试报告（forum 直连）..."
  python3 deploy/scripts/load_test_concurrent.py \
    --base-url "${FORUM_BASE_URL}" \
    --path "/posts?page=0&size=10" \
    --concurrency-levels "10,50,100" \
    --requests-per-user 20 \
    --report-file docs/concurrent-load-report.md
}

main() {
  local selected_mode=""
  if [ "${RUN_MODE}" = "full" ]; then
    if ! check_gateway; then
      echo "[ERROR] RUN_MODE=full 但网关不可达：${BASE_URL}/actuator/health"
      echo "[ERROR] 请先启动完整后端服务后再执行。"
      exit 1
    fi
    run_full
    selected_mode="full"
  elif [ "${RUN_MODE}" = "direct" ]; then
    if ! check_forum_direct; then
      echo "[ERROR] RUN_MODE=direct 但 forum-service 不可达：${FORUM_BASE_URL}/actuator/health"
      exit 1
    fi
    run_direct
    selected_mode="direct"
  elif [ "${RUN_MODE}" = "auto" ]; then
    if check_gateway; then
      echo "[INFO] auto 模式检测到网关可用，执行 full 报告生成。"
      run_full
      selected_mode="full"
    elif check_forum_direct; then
      echo "[INFO] auto 模式检测到 forum-service 可用，执行 direct 报告生成。"
      run_direct
      selected_mode="direct"
    else
      echo "[ERROR] auto 模式下网关与 forum-service 均不可达。"
      echo "[ERROR] 网关: ${BASE_URL}/actuator/health"
      echo "[ERROR] forum: ${FORUM_BASE_URL}/actuator/health"
      exit 1
    fi
  else
    echo "[ERROR] RUN_MODE 仅支持 auto/full/direct，当前值：${RUN_MODE}"
    exit 1
  fi

  echo "[SUCCESS] 报告生成完成："
  if [ "${selected_mode}" = "full" ]; then
    echo "  - docs/regression-report.md"
    echo "  - docs/regression-report-expiry.md"
    echo "  - docs/security-test-report.md"
    echo "  - docs/security-test-report-expiry.md"
    echo "  - docs/cache-benchmark-report.md"
    echo "  - docs/evidence-cache-benchmark.md"
    echo "  - docs/concurrent-load-report.md"
  else
    echo "  - docs/cache-benchmark-report.md"
    echo "  - docs/evidence-cache-benchmark.md"
    echo "  - docs/concurrent-load-report.md"
  fi
}

main "$@"
