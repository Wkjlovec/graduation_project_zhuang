package com.graduation.authuser.controller;

import com.graduation.authuser.dto.UserProfileResponse;
import com.graduation.authuser.security.AuthenticatedUser;
import com.graduation.authuser.service.AuthService;
import com.graduation.common.ApiResponse;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/users")
public class UserController {

    private final AuthService authService;

    public UserController(AuthService authService) {
        this.authService = authService;
    }

    @GetMapping("/me")
    public ApiResponse<UserProfileResponse> me(Authentication authentication) {
        AuthenticatedUser user = (AuthenticatedUser) authentication.getPrincipal();
        return ApiResponse.ok(authService.me(user));
    }
}
