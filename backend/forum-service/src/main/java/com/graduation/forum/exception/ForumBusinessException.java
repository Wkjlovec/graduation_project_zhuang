package com.graduation.forum.exception;

public class ForumBusinessException extends RuntimeException {

    private final int code;

    public ForumBusinessException(int code, String message) {
        super(message);
        this.code = code;
    }

    public int getCode() {
        return code;
    }
}
