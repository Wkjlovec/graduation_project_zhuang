package com.graduation.authuser.service;

import com.graduation.authuser.domain.UserAccount;
import com.graduation.authuser.dto.AuthTokenResponse;
import com.graduation.authuser.dto.LoginRequest;
import com.graduation.authuser.dto.RefreshTokenRequest;
import com.graduation.authuser.dto.RegisterRequest;
import com.graduation.authuser.dto.UserProfileResponse;
import com.graduation.authuser.exception.BusinessException;
import com.graduation.authuser.repository.UserAccountRepository;
import com.graduation.authuser.security.AuthenticatedUser;
import com.graduation.authuser.security.JwtService;
import com.graduation.common.ServiceConstants;
import java.util.UUID;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private final UserAccountRepository userAccountRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AuthSessionService authSessionService;
    private final LoginAttemptService loginAttemptService;

    public AuthService(
            UserAccountRepository userAccountRepository,
            PasswordEncoder passwordEncoder,
            JwtService jwtService,
            AuthSessionService authSessionService,
            LoginAttemptService loginAttemptService
    ) {
        this.userAccountRepository = userAccountRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
        this.authSessionService = authSessionService;
        this.loginAttemptService = loginAttemptService;
    }

    @Transactional
    public AuthTokenResponse register(RegisterRequest request) {
        if (userAccountRepository.existsByUsername(request.username())) {
            throw new BusinessException(4003, "username already exists");
        }
        UserAccount account = new UserAccount();
        account.setUsername(request.username());
        account.setPassword(passwordEncoder.encode(request.password()));
        account.setNickname(resolveNickname(request));
        UserAccount saved = userAccountRepository.save(account);
        return issueTokens(saved);
    }

    @Transactional
    public AuthTokenResponse login(LoginRequest request, String clientIp) {
        loginAttemptService.checkLocked(request.username(), clientIp);
        UserAccount account = userAccountRepository.findByUsername(request.username())
                .orElseThrow(() -> {
                    loginAttemptService.onLoginFailed(request.username(), clientIp);
                    return new BusinessException(4011, "username or password is wrong");
                });
        if (!passwordEncoder.matches(request.password(), account.getPassword())) {
            loginAttemptService.onLoginFailed(request.username(), clientIp);
            throw new BusinessException(4011, "username or password is wrong");
        }
        loginAttemptService.onLoginSuccess(request.username(), clientIp);
        return issueTokens(account);
    }

    @Transactional
    public AuthTokenResponse refresh(RefreshTokenRequest request) {
        AuthenticatedUser userFromRefresh;
        try {
            userFromRefresh = jwtService.parseRefreshToken(request.refreshToken());
        } catch (RuntimeException ex) {
            throw new BusinessException(4012, "refresh token expired or invalidated");
        }
        if (!authSessionService.isSessionActive(userFromRefresh.sessionId(), userFromRefresh.userId())) {
            throw new BusinessException(4012, "refresh token expired or invalidated");
        }
        UserAccount account = userAccountRepository.findById(userFromRefresh.userId())
                .orElseThrow(() -> new BusinessException(4041, "user not found"));
        authSessionService.deleteSession(userFromRefresh.sessionId());
        return issueTokens(account);
    }

    public void logout(AuthenticatedUser user) {
        if (user.sessionId() != null && !user.sessionId().isBlank()) {
            authSessionService.deleteSession(user.sessionId());
        }
    }

    @Transactional(readOnly = true)
    public UserProfileResponse me(AuthenticatedUser user) {
        UserAccount account = userAccountRepository.findById(user.userId())
                .orElseThrow(() -> new BusinessException(4041, "user not found"));
        return new UserProfileResponse(account.getId(), account.getUsername(), account.getNickname(), account.getCreatedAt());
    }

    private String resolveNickname(RegisterRequest request) {
        String nickname = request.nickname();
        if (nickname == null || nickname.isBlank()) {
            return request.username();
        }
        return nickname;
    }

    private AuthTokenResponse issueTokens(UserAccount account) {
        String sessionId = UUID.randomUUID().toString();
        authSessionService.saveSession(sessionId, account.getId(), jwtService.getRefreshExpireSeconds());
        String accessToken = jwtService.generateAccessToken(account.getId(), account.getUsername(), sessionId);
        String refreshToken = jwtService.generateRefreshToken(account.getId(), account.getUsername(), sessionId);
        return new AuthTokenResponse(
                account.getId(),
                account.getUsername(),
                account.getNickname(),
                accessToken,
                ServiceConstants.TOKEN_PREFIX.trim(),
                refreshToken,
                ServiceConstants.JWT_TYPE_REFRESH
        );
    }
}
