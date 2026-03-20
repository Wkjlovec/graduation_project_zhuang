#!/usr/bin/env python3
import argparse
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class RegressionError(RuntimeError):
    pass


@dataclass
class HttpResult:
    status: int
    body: dict[str, Any]
    raw: str


def http_json(base_url: str, method: str, path: str, payload: dict[str, Any] | None = None, token: str | None = None) -> HttpResult:
    url = f"{base_url}{path}"
    body_data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        body_data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(url=url, data=body_data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            status = response.getcode()
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        status = error.code
        raw = error.read().decode("utf-8")
    except urllib.error.URLError as error:
        raise RegressionError(f"request failed: {method} {path}, reason={error.reason}") from error

    try:
        parsed = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        parsed = {}
    return HttpResult(status=status, body=parsed, raw=raw)


def assert_ok(result: HttpResult, action: str, require_data: bool = True) -> dict[str, Any]:
    code = result.body.get("code")
    if result.status != 200 or code != 0:
        raise RegressionError(f"{action} failed: status={result.status}, body={result.raw}")
    data = result.body.get("data")
    if require_data and data is None:
        raise RegressionError(f"{action} returned empty data")
    return data


def assert_business_code(result: HttpResult, expected_code: int, action: str) -> None:
    code = result.body.get("code")
    if code != expected_code:
        raise RegressionError(
            f"{action} expected code={expected_code}, got status={result.status}, body={result.raw}"
        )


def run_regression(base_url: str, verify_expiry: bool, expiry_wait_seconds: int, report_file: str | None = None) -> None:
    checkpoints: list[str] = []
    suffix = str(int(time.time() * 1000) % 1000000)
    username_a = f"qa_user_a_{suffix}"
    username_b = f"qa_user_b_{suffix}"
    password = "pass123456"

    print("[1/10] loading section list")
    sections = assert_ok(http_json(base_url, "GET", "/api/forum/sections"), "load sections")
    if not sections:
        raise RegressionError("section list is empty")
    checkpoints.append("分区读取")
    section_id = sections[0]["sectionId"]

    print("[2/10] register and login two users")
    register_a_data = assert_ok(
        http_json(
            base_url,
            "POST",
            "/api/auth/register",
            {"username": username_a, "password": password, "nickname": "qa-a"},
        ),
        "register user A",
    )
    register_b_data = assert_ok(
        http_json(
            base_url,
            "POST",
            "/api/auth/register",
            {"username": username_b, "password": password, "nickname": "qa-b"},
        ),
        "register user B",
    )
    token_a = register_a_data["token"]
    token_b = register_b_data["token"]
    refresh_token_b = register_b_data["refreshToken"]
    checkpoints.append("双用户注册登录")

    print("[3/10] full path regression: post -> comment -> search")
    post_data = assert_ok(
        http_json(
            base_url,
            "POST",
            "/api/forum/posts",
            {
                "title": f"regression_post_{suffix}",
                "content": "this is a regression content",
                "sectionId": section_id,
            },
            token=token_a,
        ),
        "create post",
    )
    post_id = post_data["postId"]

    assert_ok(
        http_json(
            base_url,
            "POST",
            f"/api/forum/posts/{post_id}/comments",
            {"content": "first level comment", "parentCommentId": None},
            token=token_b,
        ),
        "create comment",
    )

    search_data = assert_ok(
        http_json(base_url, "GET", f"/api/search/posts?keyword=regression_post_{suffix}&sectionId={section_id}"),
        "search posts",
    )
    if not search_data:
        raise RegressionError("search returned empty list")
    checkpoints.append("发帖评论搜索全链路")

    print("[4/10] home modules regression: notification + media")
    assert_ok(http_json(base_url, "GET", "/api/notifications/home"), "notification home")
    assert_ok(http_json(base_url, "GET", "/api/media/home"), "media home")
    checkpoints.append("通知与推荐模块")

    print("[5/11] my-notification scene: list + mark read")
    my_notifications = assert_ok(http_json(base_url, "GET", "/api/notifications/my", token=token_b), "my notifications")
    unread_items = [item for item in my_notifications if isinstance(item, dict) and not item.get("read", False)]
    if unread_items:
        notification_id = unread_items[0].get("notificationId")
        if notification_id is None:
            raise RegressionError("notification id is missing when trying mark-read")
        assert_ok(
            http_json(base_url, "POST", f"/api/notifications/{notification_id}/read", token=token_b),
            "mark notification read",
        )
    checkpoints.append("我的通知与已读")

    print("[6/11] unauthorized scene: create post without token")
    unauthorized = http_json(
        base_url,
        "POST",
        "/api/forum/posts",
        {"title": "unauthorized", "content": "should fail", "sectionId": section_id},
    )
    assert_business_code(unauthorized, 4010, "unauthorized create post")
    checkpoints.append("无token写操作拦截")

    print("[7/11] no-permission scene: user B delete user A post")
    forbidden = http_json(base_url, "DELETE", f"/api/forum/posts/{post_id}", token=token_b)
    assert_business_code(forbidden, 4031, "forbidden delete post")
    checkpoints.append("无权限操作拦截")

    print("[8/11] concurrency scene: duplicate like")
    like_results: list[HttpResult | None] = [None, None]

    def like_once(index: int) -> None:
        like_results[index] = http_json(base_url, "POST", f"/api/forum/posts/{post_id}/like", token=token_b)

    t1 = threading.Thread(target=like_once, args=(0,))
    t2 = threading.Thread(target=like_once, args=(1,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    codes = sorted([result.body.get("code") for result in like_results if result is not None])
    if codes != [0, 4091]:
        raise RegressionError(f"concurrency like expected [0, 4091], got {codes}")
    checkpoints.append("并发重复点赞稳定性")

    print("[9/11] logout invalidation scene")
    assert_ok(http_json(base_url, "POST", "/api/auth/logout", token=token_a), "logout user A", require_data=False)
    after_logout = http_json(base_url, "GET", "/api/users/me", token=token_a)
    assert_business_code(after_logout, 4010, "access with invalidated token")
    checkpoints.append("登出后会话失效")

    print("[10/11] refresh flow scene")
    refresh_data = assert_ok(
        http_json(base_url, "POST", "/api/auth/refresh", {"refreshToken": refresh_token_b}),
        "refresh token",
    )
    refreshed_token = refresh_data["token"]
    assert_ok(http_json(base_url, "GET", "/api/users/me", token=refreshed_token), "me with refreshed token")
    checkpoints.append("refresh流程")

    print("[11/11] token expiry scene")
    if verify_expiry:
        if expiry_wait_seconds <= 0:
            raise RegressionError("expiry wait seconds must be greater than 0")
        print(f"waiting {expiry_wait_seconds}s for access token expiry verification")
        time.sleep(expiry_wait_seconds)
        expired_access = http_json(base_url, "GET", "/api/users/me", token=refreshed_token)
        assert_business_code(expired_access, 4010, "expired token access")
        checkpoints.append("token过期拦截")
    else:
        print("skip expiry verification (enable with --verify-expiry)")
        checkpoints.append("token过期拦截(跳过)")

    print("system regression passed")
    if report_file:
        write_report(report_file, True, checkpoints, "")


def write_report(report_file: str, success: bool, checkpoints: list[str], error_message: str) -> None:
    lines = [
        "# 系统回归结果",
        "",
        f"- 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 结果: {'通过' if success else '失败'}",
        "",
        "## 覆盖项",
    ]
    for item in checkpoints:
        lines.append(f"- {item}")
    if not success:
        lines.extend(["", "## 失败信息", f"- {error_message}"])
    with open(report_file, "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full-link regression for forum system.")
    parser.add_argument("--base-url", default=os.getenv("BASE_URL", "http://127.0.0.1:8080"), help="gateway base url")
    parser.add_argument("--verify-expiry", action="store_true", help="verify token expiry by waiting")
    parser.add_argument(
        "--expiry-wait-seconds",
        type=int,
        default=int(os.getenv("JWT_EXPIRE_SECONDS", "0")) + 2,
        help="seconds to wait before checking expired token",
    )
    parser.add_argument("--report-file", default="", help="optional markdown output path")
    args = parser.parse_args()

    try:
        run_regression(
            args.base_url,
            args.verify_expiry,
            args.expiry_wait_seconds,
            args.report_file.strip() or None,
        )
    except RegressionError as error:
        print(f"regression failed: {error}")
        if args.report_file.strip():
            write_report(args.report_file.strip(), False, [], str(error))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
