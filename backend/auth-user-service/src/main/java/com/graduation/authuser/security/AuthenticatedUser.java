package com.graduation.authuser.security;

public record AuthenticatedUser(Long userId, String username, String sessionId) {
}
