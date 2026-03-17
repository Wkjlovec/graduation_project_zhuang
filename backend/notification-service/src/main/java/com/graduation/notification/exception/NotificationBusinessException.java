package com.graduation.notification.exception;

public class NotificationBusinessException extends RuntimeException {

    private final int code;

    public NotificationBusinessException(int code, String message) {
        super(message);
        this.code = code;
    }

    public int getCode() {
        return code;
    }
}
