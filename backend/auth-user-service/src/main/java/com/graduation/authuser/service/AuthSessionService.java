package com.graduation.authuser.service;

import com.graduation.common.ServiceConstants;
import java.time.Duration;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class AuthSessionService {

    private final StringRedisTemplate redisTemplate;

    public AuthSessionService(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public void saveSession(String sessionId, Long userId, long ttlSeconds) {
        String key = buildSessionKey(sessionId);
        redisTemplate.opsForValue().set(key, String.valueOf(userId), Duration.ofSeconds(ttlSeconds));
    }

    public boolean isSessionActive(String sessionId, Long userId) {
        String key = buildSessionKey(sessionId);
        String value = redisTemplate.opsForValue().get(key);
        return value != null && value.equals(String.valueOf(userId));
    }

    public void deleteSession(String sessionId) {
        redisTemplate.delete(buildSessionKey(sessionId));
    }

    private String buildSessionKey(String sessionId) {
        return ServiceConstants.REDIS_KEY_AUTH_SESSION_PREFIX + sessionId;
    }
}
