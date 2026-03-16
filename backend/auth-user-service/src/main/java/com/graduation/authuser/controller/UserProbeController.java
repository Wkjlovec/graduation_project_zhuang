package com.graduation.authuser.controller;

import com.graduation.common.ServiceConstants;
import com.graduation.common.ApiResponse;
import jakarta.servlet.http.HttpServletRequest;
import java.time.OffsetDateTime;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/users")
public class UserProbeController {

    @Value("${spring.application.name}")
    private String serviceName;

    @GetMapping("/ping")
    public ApiResponse<Map<String, String>> ping(HttpServletRequest request) {
        String requestId = request.getHeader(ServiceConstants.HEADER_REQUEST_ID);
        Map<String, String> payload = Map.of(
                "message", "auth-user-service is reachable",
                "service", serviceName,
                "time", OffsetDateTime.now().toString(),
                "requestId", requestId == null ? "" : requestId
        );
        return ApiResponse.ok(payload);
    }
}
