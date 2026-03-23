package com.graduation.common;

public record ApiResponse<T>(int code, String message, T data) {

    private static final int SUCCESS_CODE = 0;

    public static <T> ApiResponse<T> ok(T data) {
        return new ApiResponse<>(SUCCESS_CODE, "ok", data);
    }

    public static <T> ApiResponse<T> fail(int code, String message) {
        return new ApiResponse<>(code, message, null);
    }
}
