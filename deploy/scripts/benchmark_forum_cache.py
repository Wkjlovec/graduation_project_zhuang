#!/usr/bin/env python3
import argparse
import json
import math
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class BenchmarkError(RuntimeError):
    pass


@dataclass(frozen=True)
class RequestResult:
    elapsed_ms: float
    status: int
    body: dict[str, Any]
    raw: str


@dataclass(frozen=True)
class BenchmarkStats:
    cold_ms: float
    warm_avg_ms: float
    warm_min_ms: float
    warm_max_ms: float
    warm_p95_ms: float
    improvement_percent: float
    warm_runs: int


def http_json(base_url: str, path: str, timeout_seconds: int) -> RequestResult:
    url = f"{base_url.rstrip('/')}{path}"
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
            status = response.getcode()
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        status = error.code
        raw = error.read().decode("utf-8")
    except urllib.error.URLError as error:
        raise BenchmarkError(f"request failed: GET {path}, reason={error.reason}") from error

    elapsed_ms = (time.perf_counter() - started) * 1000
    try:
        parsed = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        parsed = {}
    return RequestResult(elapsed_ms=elapsed_ms, status=status, body=parsed, raw=raw)


def assert_success(result: RequestResult, action: str) -> None:
    code = result.body.get("code")
    if result.status != 200 or code != 0:
        raise BenchmarkError(f"{action} failed: status={result.status}, body={result.raw}")


def percentile(values: list[float], p: int) -> float:
    if not values:
        raise BenchmarkError("warm run list is empty")
    if p < 0 or p > 100:
        raise BenchmarkError("percentile must be between 0 and 100")
    sorted_values = sorted(values)
    rank = int(math.ceil((p / 100) * len(sorted_values)))
    index = max(0, min(rank - 1, len(sorted_values) - 1))
    return sorted_values[index]


def calc_stats(cold_ms: float, warm_values: list[float]) -> BenchmarkStats:
    warm_avg_ms = sum(warm_values) / len(warm_values)
    warm_min_ms = min(warm_values)
    warm_max_ms = max(warm_values)
    warm_p95_ms = percentile(warm_values, 95)
    improvement = ((cold_ms - warm_avg_ms) / cold_ms * 100) if cold_ms > 0 else 0.0
    return BenchmarkStats(
        cold_ms=round(cold_ms, 2),
        warm_avg_ms=round(warm_avg_ms, 2),
        warm_min_ms=round(warm_min_ms, 2),
        warm_max_ms=round(warm_max_ms, 2),
        warm_p95_ms=round(warm_p95_ms, 2),
        improvement_percent=round(improvement, 2),
        warm_runs=len(warm_values),
    )


def build_report(
    success: bool,
    base_url: str,
    path: str,
    stats: BenchmarkStats | None,
    error_message: str,
) -> str:
    lines = [
        "# 缓存响应时间对比",
        "",
        f"- 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 目标: {base_url.rstrip('/')}{path}",
        f"- 结果: {'通过' if success else '失败'}",
        "",
    ]
    if success and stats is not None:
        lines.extend(
            [
                "## 结果数据（毫秒）",
                "",
                "| 指标 | 数值 |",
                "|---|---:|",
                f"| 首次请求（冷） | {stats.cold_ms} |",
                f"| 后续请求均值（热，n={stats.warm_runs}） | {stats.warm_avg_ms} |",
                f"| 后续请求最小值 | {stats.warm_min_ms} |",
                f"| 后续请求最大值 | {stats.warm_max_ms} |",
                f"| 后续请求 P95 | {stats.warm_p95_ms} |",
                f"| 相对提升 | {stats.improvement_percent}% |",
                "",
            ]
        )
    else:
        lines.extend(["## 失败信息", f"- {error_message}", ""])
    return "\n".join(lines)


def write_report(report_file: str, content: str) -> None:
    with open(report_file, "w", encoding="utf-8") as file:
        file.write(content + "\n")


def run(base_url: str, path: str, warm_runs: int, timeout_seconds: int, report_file: str | None) -> None:
    if warm_runs <= 0:
        raise BenchmarkError("warm-runs must be greater than 0")

    cold = http_json(base_url, path, timeout_seconds)
    assert_success(cold, "cold request")
    warm_values: list[float] = []
    for index in range(warm_runs):
        warm = http_json(base_url, path, timeout_seconds)
        assert_success(warm, f"warm request #{index + 1}")
        warm_values.append(warm.elapsed_ms)

    stats = calc_stats(cold.elapsed_ms, warm_values)
    print(f"cold={stats.cold_ms}ms warm_avg={stats.warm_avg_ms}ms improvement={stats.improvement_percent}%")
    if report_file:
        write_report(report_file, build_report(True, base_url, path, stats, ""))


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark forum list API cold/warm response times.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080", help="gateway base url")
    parser.add_argument("--path", default="/api/forum/posts?page=0&size=10", help="benchmark target path")
    parser.add_argument("--warm-runs", type=int, default=20, help="number of warm requests")
    parser.add_argument("--timeout-seconds", type=int, default=20, help="single request timeout")
    parser.add_argument("--report-file", default="", help="optional markdown output path")
    args = parser.parse_args()
    report_file = args.report_file.strip() or None

    try:
        run(args.base_url, args.path, args.warm_runs, args.timeout_seconds, report_file)
    except BenchmarkError as error:
        print(f"benchmark failed: {error}")
        if report_file:
            write_report(
                report_file,
                build_report(False, args.base_url, args.path, None, str(error)),
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
