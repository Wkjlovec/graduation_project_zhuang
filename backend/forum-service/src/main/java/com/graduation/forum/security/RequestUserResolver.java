package com.graduation.forum.security;

import com.graduation.common.ServiceConstants;
import com.graduation.forum.exception.ForumBusinessException;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.stereotype.Component;

@Component
public class RequestUserResolver {

    public RequestUser resolve(HttpServletRequest request) {
        String userIdHeader = request.getHeader(ServiceConstants.HEADER_USER_ID);
        String usernameHeader = request.getHeader(ServiceConstants.HEADER_USERNAME);
        if (userIdHeader == null || userIdHeader.isBlank()) {
            throw new ForumBusinessException(4010, "missing X-User-Id header");
        }
        if (usernameHeader == null || usernameHeader.isBlank()) {
            throw new ForumBusinessException(4011, "missing X-Username header");
        }
        Long userId = parseUserId(userIdHeader);
        return new RequestUser(userId, usernameHeader);
    }

    private Long parseUserId(String userIdHeader) {
        try {
            return Long.parseLong(userIdHeader);
        } catch (NumberFormatException ex) {
            throw new ForumBusinessException(4012, "invalid X-User-Id header");
        }
    }
}
