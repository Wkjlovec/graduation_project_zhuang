#!/usr/bin/env python3
import argparse
import json
import math
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass


class LoadTestError(RuntimeError):
    pass


@dataclass(frozen=True)
class RequestSample:
    ok: bool
    elapsed_ms: float
    status: int
    code: int | None
    error: str


@dataclass(frozen=True)
class ConcurrencyResult:
    concurrency: int
    total_requests: int
    success_count: int
    fail_count: int
    success_rate: float
    avg_ms: float
    p95_ms: float
    qps: float


def http_get_json(url: str, timeout_seconds: int) -> RequestSample:
    started = time.perf_counter()
    try:
        request = urllib.request.Request(url=url, method="GET")
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            status = response.getcode()
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        status = error.code
        raw = error.read().decode("utf-8")
    except urllib.error.URLError as error:
        elapsed_ms = (time.perf_counter() - started) * 1000
        return RequestSample(
            ok=False,
            elapsed_ms=elapsed_ms,
            status=0,
            code=None,
            error=f"urlerror:{error.reason}",
        )

    elapsed_ms = (time.perf_counter() - started) * 1000
    try:
        body = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        body = {}

    code = body.get("code") if isinstance(body, dict) else None
    ok = status == 200 and code == 0
    return RequestSample(
        ok=ok,
        elapsed_ms=elapsed_ms,
        status=status,
        code=code if isinstance(code, int) else None,
        error="" if ok else f"status={status},code={code}",
    )


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    rank = int(math.ceil((p / 100) * len(sorted_values)))
    index = max(0, min(rank - 1, len(sorted_values) - 1))
    return sorted_values[index]


def run_level(url: str, concurrency: int, requests_per_user: int, timeout_seconds: int) -> ConcurrencyResult:
    total_requests = concurrency * requests_per_user
    if total_requests <= 0:
        raise LoadTestError("total requests must be greater than 0")

    samples: list[RequestSample] = []
    lock = threading.Lock()

    def worker() -> None:
        for _ in range(requests_per_user):
            result = http_get_json(url, timeout_seconds)
            with lock:
                samples.append(result)

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(worker) for _ in range(concurrency)]
        for future in as_completed(futures):
            future.result()
    total_seconds = time.perf_counter() - started

    success_samples = [s for s in samples if s.ok]
    success_count = len(success_samples)
    fail_count = len(samples) - success_count
    success_rate = (success_count / len(samples) * 100) if samples else 0.0
    success_elapsed = [s.elapsed_ms for s in success_samples]
    avg_ms = (sum(success_elapsed) / len(success_elapsed)) if success_elapsed else 0.0
    p95_ms = percentile(success_elapsed, 95) if success_elapsed else 0.0
    qps = (len(samples) / total_seconds) if total_seconds > 0 else 0.0

    return ConcurrencyResult(
        concurrency=concurrency,
        total_requests=len(samples),
        success_count=success_count,
        fail_count=fail_count,
        success_rate=round(success_rate, 2),
        avg_ms=round(avg_ms, 2),
        p95_ms=round(p95_ms, 2),
        qps=round(qps, 2),
    )


def to_markdown(
    base_url: str,
    path: str,
    levels: list[ConcurrencyResult],
    requests_per_user: int,
    duration_note: str,
) -> str:
    lines = [
        "# 并发负载测试报告",
        "",
        f"- 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 目标接口: {base_url.rstrip('/')}{path}",
        f"- 每并发用户请求数: {requests_per_user}",
        f"- 备注: {duration_note}",
        "",
        "## 并发量 vs 响应与吞吐对照表",
        "",
        "| 并发用户数 | 总请求数 | 成功数 | 失败数 | 成功率 | 平均响应时间(ms) | P95(ms) | 吞吐量(QPS) |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in levels:
        lines.append(
            f"| {item.concurrency} | {item.total_requests} | {item.success_count} | {item.fail_count} | {item.success_rate}% | {item.avg_ms} | {item.p95_ms} | {item.qps} |"
        )

    lines.extend(
        [
            "",
            "## 曲线图（Mermaid）",
            "",
            "```mermaid",
            "xychart-beta",
            '    title "Concurrency vs Avg/P95 Response"',
            '    x-axis "Concurrency" [10, 50, 100]',
            '    y-axis "Response(ms)" 0 --> 2000',
            "    line \"Avg\" [" + ", ".join(str(item.avg_ms) for item in levels) + "]",
            "    line \"P95\" [" + ", ".join(str(item.p95_ms) for item in levels) + "]",
            "```",
            "",
            "```mermaid",
            "xychart-beta",
            '    title "Concurrency vs Throughput"',
            '    x-axis "Concurrency" [10, 50, 100]',
            '    y-axis "QPS" 0 --> 5000',
            "    bar \"QPS\" [" + ", ".join(str(item.qps) for item in levels) + "]",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Concurrent load test for forum list API.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080", help="gateway base url")
    parser.add_argument("--path", default="/api/forum/posts?page=0&size=10", help="target GET path")
    parser.add_argument("--concurrency-levels", default="10,50,100", help="comma separated concurrency levels")
    parser.add_argument("--requests-per-user", type=int, default=20, help="requests sent by each virtual user")
    parser.add_argument("--timeout-seconds", type=int, default=20, help="single request timeout")
    parser.add_argument("--report-file", default="docs/concurrent-load-report.md", help="markdown output path")
    args = parser.parse_args()

    try:
        levels = [int(item.strip()) for item in args.concurrency_levels.split(",") if item.strip()]
        if levels != [10, 50, 100]:
            raise LoadTestError("this script expects concurrency levels exactly 10,50,100 to match defense metrics")
        url = f"{args.base_url.rstrip('/')}{args.path}"

        print(f"[INFO] warmup request: {url}")
        warmup = http_get_json(url, args.timeout_seconds)
        if not warmup.ok:
            raise LoadTestError(f"warmup failed: status={warmup.status}, code={warmup.code}, error={warmup.error}")

        results: list[ConcurrencyResult] = []
        for level in levels:
            print(f"[INFO] running concurrency={level}, requests_per_user={args.requests_per_user}")
            stats = run_level(url, level, args.requests_per_user, args.timeout_seconds)
            print(
                f"[INFO] level={level} avg={stats.avg_ms}ms p95={stats.p95_ms}ms "
                f"success_rate={stats.success_rate}% qps={stats.qps}"
            )
            results.append(stats)

        report = to_markdown(
            args.base_url,
            args.path,
            results,
            args.requests_per_user,
            "ThreadPoolExecutor 并发模拟",
        )
        with open(args.report_file, "w", encoding="utf-8") as file:
            file.write(report + "\n")
        print(f"[SUCCESS] report written: {args.report_file}")
        return 0
    except LoadTestError as error:
        print(f"[ERROR] {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

