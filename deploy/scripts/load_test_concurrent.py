#!/usr/bin/env python3
import argparse
import math
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass


@dataclass
class RequestResult:
    success: bool
    elapsed_ms: float


@dataclass
class RoundStats:
    concurrency: int
    total_requests: int
    success_count: int
    fail_count: int
    success_rate: float
    avg_ms: float
    p95_ms: float
    qps: float


def single_request(url: str, timeout: int) -> RequestResult:
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
            elapsed = (time.perf_counter() - start) * 1000
            return RequestResult(success=(resp.status == 200), elapsed_ms=round(elapsed, 2))
    except Exception:
        elapsed = (time.perf_counter() - start) * 1000
        return RequestResult(success=False, elapsed_ms=round(elapsed, 2))


def percentile(values: list[float], pct: int) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = math.ceil(len(sorted_vals) * pct / 100) - 1
    return sorted_vals[max(0, idx)]


def run_round(url: str, concurrency: int, requests_per_user: int, timeout: int) -> RoundStats:
    total = concurrency * requests_per_user
    results: list[RequestResult] = []

    start_time = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(single_request, url, timeout) for _ in range(total)]
        for f in as_completed(futures):
            results.append(f.result())
    wall_time = time.perf_counter() - start_time

    success_results = [r for r in results if r.success]
    fail_count = total - len(success_results)
    success_times = [r.elapsed_ms for r in success_results]

    avg_ms = round(sum(success_times) / len(success_times), 2) if success_times else 0.0
    p95_ms = round(percentile(success_times, 95), 2) if success_times else 0.0
    qps = round(total / wall_time, 2) if wall_time > 0 else 0.0
    success_rate = round(len(success_results) / total * 100, 2) if total > 0 else 0.0

    return RoundStats(
        concurrency=concurrency,
        total_requests=total,
        success_count=len(success_results),
        fail_count=fail_count,
        success_rate=success_rate,
        avg_ms=avg_ms,
        p95_ms=p95_ms,
        qps=qps,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Concurrent load test for forum API.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080", help="gateway base url")
    parser.add_argument("--path", default="/api/forum/posts?page=0&size=10", help="target path")
    parser.add_argument("--requests-per-user", type=int, default=20, help="requests each virtual user sends")
    parser.add_argument("--timeout", type=int, default=20, help="single request timeout in seconds")
    args = parser.parse_args()

    url = f"{args.base_url.rstrip('/')}{args.path}"
    concurrency_levels = [10, 50, 100]

    # warmup
    print("预热请求...", end=" ")
    warmup = single_request(url, args.timeout)
    print(f"{'成功' if warmup.success else '失败'} ({warmup.elapsed_ms} ms)")
    print()

    def pad_right(s: str, width: int) -> str:
        w = sum(2 if ord(c) > 127 else 1 for c in s)
        return s + " " * (width - w)

    cols = [("并发数", 10), ("总请求", 10), ("成功", 10), ("失败", 10), ("成功率", 10), ("平均(ms)", 12), ("P95(ms)", 12), ("QPS", 10)]
    width = sum(c[1] for c in cols) + 4
    print("=" * width)
    print("  并发负载测试结果")
    print("=" * width)
    header = "  " + "".join(pad_right(name, w) for name, w in cols)
    print(header)
    print("-" * width)

    all_stats: list[RoundStats] = []
    for level in concurrency_levels:
        stats = run_round(url, level, args.requests_per_user, args.timeout)
        all_stats.append(stats)
        vals = [str(stats.concurrency), str(stats.total_requests), str(stats.success_count),
                str(stats.fail_count), f"{stats.success_rate}%", str(stats.avg_ms),
                str(stats.p95_ms), str(stats.qps)]
        row = "  " + "".join(pad_right(v, cols[i][1]) for i, v in enumerate(vals))
        print(row)

    print("=" * width)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
