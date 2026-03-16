#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] 未检测到 docker 命令。请先安装 Docker Desktop 或 Docker Engine。"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "[ERROR] 未检测到 docker compose 子命令。请升级 Docker 到支持 compose 的版本。"
  exit 1
fi

echo "[OK] Docker 与 Docker Compose 均可用。可以继续执行：docker compose up -d"
