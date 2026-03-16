package com.graduation.authuser.security;

import com.graduation.common.ApiResponse;
import com.graduation.common.ServiceConstants;
import com.graduation.authuser.service.AuthSessionService;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.jsonwebtoken.JwtException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final AuthSessionService authSessionService;
    private final ObjectMapper objectMapper;
    private final List<String> permitPathPrefixes = List.of(
            "/auth/register",
            "/auth/login",
            "/auth/refresh",
            "/users/ping",
            "/actuator"
    );

    public JwtAuthenticationFilter(JwtService jwtService, AuthSessionService authSessionService, ObjectMapper objectMapper) {
        this.jwtService = jwtService;
        this.authSessionService = authSessionService;
        this.objectMapper = objectMapper;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        if (HttpMethod.OPTIONS.matches(request.getMethod())) {
            chain.doFilter(request, response);
            return;
        }
        if (isPermitPath(request.getRequestURI())) {
            chain.doFilter(request, response);
            return;
        }

        String authorization = request.getHeader(ServiceConstants.HEADER_AUTHORIZATION);
        if (authorization == null || !authorization.startsWith(ServiceConstants.TOKEN_PREFIX)) {
            writeUnauthorized(response, "missing or invalid Authorization header");
            return;
        }

        String token = authorization.substring(ServiceConstants.TOKEN_PREFIX.length());
        try {
            AuthenticatedUser user = jwtService.parseAccessToken(token);
            if (!authSessionService.isSessionActive(user.sessionId(), user.userId())) {
                writeUnauthorized(response, "session invalidated");
                return;
            }
            UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(
                    user, null, AuthorityUtils.NO_AUTHORITIES
            );
            SecurityContextHolder.getContext().setAuthentication(authentication);
            chain.doFilter(request, response);
        } catch (JwtException | IllegalArgumentException ex) {
            writeUnauthorized(response, "token verify failed");
        }
    }

    private boolean isPermitPath(String uri) {
        for (String pathPrefix : permitPathPrefixes) {
            if (uri.startsWith(pathPrefix)) {
                return true;
            }
        }
        return false;
    }

    private void writeUnauthorized(HttpServletResponse response, String message) throws IOException {
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.getWriter().write(objectMapper.writeValueAsString(ApiResponse.fail(4010, message)));
    }
}
