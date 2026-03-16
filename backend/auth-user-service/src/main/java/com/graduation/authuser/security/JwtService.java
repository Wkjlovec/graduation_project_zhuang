package com.graduation.authuser.security;

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
    private final long expireSeconds;

    public JwtService(
            @Value("${security.jwt.secret}") String jwtSecret,
            @Value("${security.jwt.expire-seconds}") long expireSeconds
    ) {
        if (jwtSecret.length() < 32) {
            throw new IllegalArgumentException("security.jwt.secret must be at least 32 characters");
        }
        this.secretKey = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
        this.expireSeconds = expireSeconds;
    }

    public String generate(Long userId, String username) {
        Instant now = Instant.now();
        return Jwts.builder()
                .subject(username)
                .claim("uid", userId)
                .issuedAt(Date.from(now))
                .expiration(Date.from(now.plusSeconds(expireSeconds)))
                .signWith(secretKey)
                .compact();
    }

    public AuthenticatedUser parse(String token) {
        Claims claims = Jwts.parser()
                .verifyWith(secretKey)
                .build()
                .parseSignedClaims(token)
                .getPayload();
        Long userId = claims.get("uid", Long.class);
        String username = claims.getSubject();
        return new AuthenticatedUser(userId, username);
    }
}
