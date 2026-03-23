package com.graduation.authuser.security;

import com.graduation.common.ServiceConstants;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Date;
import javax.crypto.SecretKey;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class JwtService {

    private final SecretKey secretKey;
    private final long accessExpireSeconds;
    private final long refreshExpireSeconds;

    public JwtService(
            @Value("${security.jwt.secret}") String jwtSecret,
            @Value("${security.jwt.expire-seconds}") long accessExpireSeconds,
            @Value("${security.jwt.refresh-expire-seconds}") long refreshExpireSeconds
    ) {
        if (jwtSecret.length() < 32) {
            throw new IllegalArgumentException("security.jwt.secret must be at least 32 characters");
        }
        this.secretKey = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
        this.accessExpireSeconds = accessExpireSeconds;
        this.refreshExpireSeconds = refreshExpireSeconds;
    }

    public String generateAccessToken(Long userId, String username, String sessionId) {
        return generateToken(userId, username, sessionId, ServiceConstants.JWT_TYPE_ACCESS, accessExpireSeconds);
    }

    public String generateRefreshToken(Long userId, String username, String sessionId) {
        return generateToken(userId, username, sessionId, ServiceConstants.JWT_TYPE_REFRESH, refreshExpireSeconds);
    }

    public long getRefreshExpireSeconds() {
        return refreshExpireSeconds;
    }

    public AuthenticatedUser parseAccessToken(String token) {
        return parse(token, ServiceConstants.JWT_TYPE_ACCESS);
    }

    public AuthenticatedUser parseRefreshToken(String token) {
        return parse(token, ServiceConstants.JWT_TYPE_REFRESH);
    }

    private String generateToken(Long userId, String username, String sessionId, String tokenType, long ttlSeconds) {
        Instant now = Instant.now();
        return Jwts.builder()
                .subject(username)
                .claim("uid", userId)
                .claim("sid", sessionId)
                .claim("typ", tokenType)
                .issuedAt(Date.from(now))
                .expiration(Date.from(now.plusSeconds(ttlSeconds)))
                .signWith(secretKey)
                .compact();
    }

    private AuthenticatedUser parse(String token, String expectedType) {
        Claims claims = Jwts.parser()
                .verifyWith(secretKey)
                .build()
                .parseSignedClaims(token)
                .getPayload();
        Long userId = claims.get("uid", Long.class);
        String username = claims.getSubject();
        String sessionId = claims.get("sid", String.class);
        String tokenType = claims.get("typ", String.class);
        if (!expectedType.equals(tokenType)) {
            throw new IllegalArgumentException("invalid token type");
        }
        return new AuthenticatedUser(userId, username, sessionId);
    }
}
