package com.graduation.common;

public final class ServiceConstants {

    public static final String JWT_TYPE_ACCESS = "access";
    public static final String JWT_TYPE_REFRESH = "refresh";
    public static final String HEADER_REQUEST_ID = "X-Request-Id";
    public static final String HEADER_AUTHORIZATION = "Authorization";
    public static final String HEADER_USER_ID = "X-User-Id";
    public static final String HEADER_USERNAME = "X-Username";
    public static final String TOKEN_PREFIX = "Bearer ";
    public static final String REDIS_KEY_AUTH_SESSION_PREFIX = "auth:session:";
    public static final String REDIS_KEY_LOGIN_FAIL_PREFIX = "auth:login:fail:";

    private ServiceConstants() {
    }
}
