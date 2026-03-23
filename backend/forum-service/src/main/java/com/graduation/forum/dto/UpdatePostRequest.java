package com.graduation.forum.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record UpdatePostRequest(
        @NotBlank
        @Size(min = 2, max = 128)
        String title,
        @NotBlank
        @Size(min = 2, max = 5000)
        String content,
        Long sectionId
) {
}
