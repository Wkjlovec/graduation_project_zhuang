package com.graduation.authuser.service;

import com.graduation.authuser.exception.BusinessException;
import com.graduation.common.ServiceConstants;
import java.time.Duration;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class LoginAttemptService {

    private final StringRedisTemplate redisTemplate;
    private final long lockSeconds;
    private final int maxFailedAttempts;

    public LoginAttemptService(
            StringRedisTemplate redisTemplate,
            @Value("${security.login.lock-seconds}") long lockSeconds,
            @Value("${security.login.max-failed-attempts}") int maxFailedAttempts
    ) {
        this.redisTemplate = redisTemplate;
        this.lockSeconds = lockSeconds;
        this.maxFailedAttempts = maxFailedAttempts;
    }

    public void checkLocked(String username, String clientIp) {
        String key = buildKey(username, clientIp);
        String attemptsValue = redisTemplate.opsForValue().get(key);
        int attempts = parseAttempts(attemptsValue);
        if (attempts >= maxFailedAttempts) {
            throw new BusinessException(4291, "too many login attempts, try later");
        }
    }

    public void onLoginFailed(String username, String clientIp) {
        String key = buildKey(username, clientIp);
        Long attempts = redisTemplate.opsForValue().increment(key);
        if (attempts != null && attempts == 1L) {
            redisTemplate.expire(key, Duration.ofSeconds(lockSeconds));
        }
    }

    public void onLoginSuccess(String username, String clientIp) {
        redisTemplate.delete(buildKey(username, clientIp));
    }

    private String buildKey(String username, String clientIp) {
        return ServiceConstants.REDIS_KEY_LOGIN_FAIL_PREFIX + username + ":" + clientIp;
    }

    private int parseAttempts(String attemptsValue) {
        if (attemptsValue == null || attemptsValue.isBlank()) {
            return 0;
        }
        try {
            return Integer.parseInt(attemptsValue);
        } catch (NumberFormatException ex) {
            return maxFailedAttempts;
        }
    }
}
