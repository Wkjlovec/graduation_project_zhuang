package com.graduation.authuser.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record RegisterRequest(
        @NotBlank
        @Size(min = 4, max = 64)
        @Pattern(regexp = "^[a-zA-Z0-9_]+$")
        String username,
        @NotBlank
        @Size(min = 6, max = 64)
        String password,
        @Size(max = 64)
        String nickname
) {
}
