package com.graduation.media.service;

import com.graduation.media.dto.MediaHomeResponse;
import com.graduation.media.dto.MediaRecommendationItem;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class MediaRecommendationService {

    private static final List<MediaRecommendationItem> MUSIC_LIST = List.of(
            new MediaRecommendationItem("music", "晴天", "周杰伦", "学习间隙放松心情"),
            new MediaRecommendationItem("music", "夜曲", "周杰伦", "适合夜间编程与写作"),
            new MediaRecommendationItem("music", "Numb", "Linkin Park", "提振效率，进入专注状态")
    );

    private static final List<MediaRecommendationItem> BOOK_LIST = List.of(
            new MediaRecommendationItem("book", "代码整洁之道", "Robert C. Martin", "提升代码可维护性"),
            new MediaRecommendationItem("book", "深入理解计算机系统", "Randal E. Bryant", "夯实底层基础"),
            new MediaRecommendationItem("book", "设计数据密集型应用", "Martin Kleppmann", "适合理解系统设计")
    );

    public MediaHomeResponse home() {
        return new MediaHomeResponse(MUSIC_LIST, BOOK_LIST);
    }

    public List<MediaRecommendationItem> recommendations(String type) {
        if ("music".equalsIgnoreCase(type)) {
            return MUSIC_LIST;
        }
        if ("book".equalsIgnoreCase(type)) {
            return BOOK_LIST;
        }
        return List.of(
                MUSIC_LIST.get(0), MUSIC_LIST.get(1),
                BOOK_LIST.get(0), BOOK_LIST.get(1)
        );
    }
}
