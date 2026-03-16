package com.graduation.authuser.dto;

public record AuthTokenResponse(
        Long userId,
        String username,
        String nickname,
        String token,
        String tokenType
) {
}
