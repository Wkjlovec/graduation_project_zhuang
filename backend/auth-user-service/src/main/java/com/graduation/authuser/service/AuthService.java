package com.graduation.authuser.service;

import com.graduation.authuser.domain.UserAccount;
import com.graduation.authuser.dto.AuthTokenResponse;
import com.graduation.authuser.dto.LoginRequest;
import com.graduation.authuser.dto.RegisterRequest;
import com.graduation.authuser.dto.UserProfileResponse;
import com.graduation.authuser.exception.BusinessException;
import com.graduation.authuser.repository.UserAccountRepository;
import com.graduation.authuser.security.AuthenticatedUser;
import com.graduation.authuser.security.JwtService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private final UserAccountRepository userAccountRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthService(UserAccountRepository userAccountRepository, PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.userAccountRepository = userAccountRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
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
        String token = jwtService.generate(saved.getId(), saved.getUsername());
        return new AuthTokenResponse(saved.getId(), saved.getUsername(), saved.getNickname(), token, "Bearer");
    }

    @Transactional(readOnly = true)
    public AuthTokenResponse login(LoginRequest request) {
        UserAccount account = userAccountRepository.findByUsername(request.username())
                .orElseThrow(() -> new BusinessException(4011, "username or password is wrong"));
        if (!passwordEncoder.matches(request.password(), account.getPassword())) {
            throw new BusinessException(4011, "username or password is wrong");
        }
        String token = jwtService.generate(account.getId(), account.getUsername());
        return new AuthTokenResponse(account.getId(), account.getUsername(), account.getNickname(), token, "Bearer");
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
}
