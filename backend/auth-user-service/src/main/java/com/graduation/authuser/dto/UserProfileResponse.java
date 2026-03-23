package com.graduation.authuser.dto;

import java.time.OffsetDateTime;

public record UserProfileResponse(
        Long userId,
        String username,
        String nickname,
        OffsetDateTime createdAt
) {
}
