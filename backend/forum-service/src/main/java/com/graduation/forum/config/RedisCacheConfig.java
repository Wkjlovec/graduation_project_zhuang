package com.graduation.forum.config;

import com.graduation.forum.service.ForumService;
import java.time.Duration;
import java.util.Map;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.RedisSerializationContext;
import org.springframework.data.redis.serializer.StringRedisSerializer;

@Configuration
public class RedisCacheConfig {

    private static final Duration DEFAULT_TTL = Duration.ofMinutes(10);
    private static final Duration POST_LIST_TTL = Duration.ofMinutes(2);
    private static final Duration POST_DETAIL_TTL = Duration.ofMinutes(5);

    @Bean
    public RedisCacheManager redisCacheManager(RedisConnectionFactory connectionFactory) {
        RedisSerializationContext.SerializationPair<String> keySerialization =
                RedisSerializationContext.SerializationPair.fromSerializer(new StringRedisSerializer());
        RedisSerializationContext.SerializationPair<Object> valueSerialization =
                RedisSerializationContext.SerializationPair.fromSerializer(new GenericJackson2JsonRedisSerializer());
        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
                .serializeKeysWith(keySerialization)
                .serializeValuesWith(valueSerialization)
                .entryTtl(DEFAULT_TTL)
                .disableCachingNullValues();
        Map<String, RedisCacheConfiguration> cacheConfigurations = Map.of(
                ForumService.CACHE_POST_LIST, defaultConfig.entryTtl(POST_LIST_TTL),
                ForumService.CACHE_POST_DETAIL, defaultConfig.entryTtl(POST_DETAIL_TTL)
        );
        return RedisCacheManager.builder(connectionFactory)
                .cacheDefaults(defaultConfig)
                .withInitialCacheConfigurations(cacheConfigurations)
                .build();
    }
}
