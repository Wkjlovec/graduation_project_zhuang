package com.graduation.gateway.filter;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.graduation.common.ApiResponse;
import com.graduation.common.ServiceConstants;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import java.nio.charset.StandardCharsets;
import java.util.List;
import javax.crypto.SecretKey;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.data.redis.core.ReactiveStringRedisTemplate;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Component
public class JwtRelayFilter implements GlobalFilter, Ordered {

    private final SecretKey secretKey;
    private final ObjectMapper objectMapper;
    private final ReactiveStringRedisTemplate redisTemplate;
    private final List<String> permitPathPrefixes = List.of(
            "/api/auth/",
            "/api/users/ping",
            "/actuator",
            "/actuator/"
    );

    public JwtRelayFilter(
            @Value("${security.jwt.secret}") String secret,
            ObjectMapper objectMapper,
            ReactiveStringRedisTemplate redisTemplate
    ) {
        if (secret.length() < 32) {
            throw new IllegalArgumentException("security.jwt.secret must be at least 32 characters");
        }
        this.secretKey = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.objectMapper = objectMapper;
        this.redisTemplate = redisTemplate;
    }

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        if (isPermitRequest(request)) {
            return chain.filter(exchange);
        }
        String authorization = request.getHeaders().getFirst(ServiceConstants.HEADER_AUTHORIZATION);
        if (authorization == null || !authorization.startsWith(ServiceConstants.TOKEN_PREFIX)) {
            return writeUnauthorized(exchange.getResponse(), "missing or invalid Authorization header");
        }
        String token = authorization.substring(ServiceConstants.TOKEN_PREFIX.length());
        try {
            Claims claims = Jwts.parser().verifyWith(secretKey).build().parseSignedClaims(token).getPayload();
            Long userId = claims.get("uid", Long.class);
            String username = claims.getSubject();
            String sessionId = claims.get("sid", String.class);
            String tokenType = claims.get("typ", String.class);
            if (!isValidAccessClaims(userId, username, sessionId, tokenType)) {
                return writeUnauthorized(exchange.getResponse(), "invalid token claims");
            }
            String sessionKey = ServiceConstants.REDIS_KEY_AUTH_SESSION_PREFIX + sessionId;
            return redisTemplate.opsForValue().get(sessionKey)
                    .flatMap(storedUserId -> {
                        if (!storedUserId.equals(String.valueOf(userId))) {
                            return writeUnauthorized(exchange.getResponse(), "session invalidated");
                        }
                        ServerWebExchange mutated = exchange.mutate()
                                .request(builder -> builder.headers(headers -> {
                                    headers.set(ServiceConstants.HEADER_USER_ID, userId.toString());
                                    headers.set(ServiceConstants.HEADER_USERNAME, username);
                                }))
                                .build();
                        return chain.filter(mutated);
                    })
                    .switchIfEmpty(writeUnauthorized(exchange.getResponse(), "session invalidated"));
        } catch (JwtException | IllegalArgumentException ex) {
            return writeUnauthorized(exchange.getResponse(), "token verify failed");
        }
    }

    @Override
    public int getOrder() {
        return -100;
    }

    private boolean isPermitRequest(ServerHttpRequest request) {
        if (HttpMethod.OPTIONS.equals(request.getMethod())) {
            return true;
        }
        String path = request.getURI().getPath();
        if (HttpMethod.GET.equals(request.getMethod()) && isForumReadPath(path)) {
            return true;
        }
        for (String prefix : permitPathPrefixes) {
            if (path.startsWith(prefix)) {
                return true;
            }
        }
        return false;
    }

    private boolean isForumReadPath(String path) {
        return "/api/forum/posts".equals(path) || path.startsWith("/api/forum/posts/");
    }

    private boolean isValidAccessClaims(Long userId, String username, String sessionId, String tokenType) {
        return userId != null
                && username != null
                && !username.isBlank()
                && sessionId != null
                && !sessionId.isBlank()
                && ServiceConstants.JWT_TYPE_ACCESS.equals(tokenType);
    }

    private Mono<Void> writeUnauthorized(ServerHttpResponse response, String message) {
        response.setStatusCode(HttpStatus.UNAUTHORIZED);
        response.getHeaders().setContentType(MediaType.APPLICATION_JSON);
        byte[] body = toBytes(ApiResponse.fail(4010, message));
        DataBuffer buffer = response.bufferFactory().wrap(body);
        return response.writeWith(Mono.just(buffer));
    }

    private byte[] toBytes(ApiResponse<Void> response) {
        try {
            return objectMapper.writeValueAsBytes(response);
        } catch (JsonProcessingException ex) {
            throw new IllegalStateException("failed to serialize unauthorized response", ex);
        }
    }
}
