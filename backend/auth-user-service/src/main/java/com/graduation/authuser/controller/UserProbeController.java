package com.graduation.authuser.controller;

import com.graduation.common.ServiceConstants;
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
    public Map<String, String> ping(HttpServletRequest request) {
        String requestId = request.getHeader(ServiceConstants.HEADER_REQUEST_ID);
        return Map.of(
                "message", "auth-user-service is reachable",
                "service", serviceName,
                "time", OffsetDateTime.now().toString(),
                "requestId", requestId == null ? "" : requestId
        );
    }
}
