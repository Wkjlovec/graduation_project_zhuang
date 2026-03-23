package com.graduation.authuser.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record LoginRequest(
        @NotBlank
        @Size(min = 4, max = 64)
        String username,
        @NotBlank
        @Size(min = 6, max = 64)
        String password
) {
}
