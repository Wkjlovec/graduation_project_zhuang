package com.graduation.forum.repository;

import com.graduation.forum.domain.ForumSection;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ForumSectionRepository extends JpaRepository<ForumSection, Long> {

    List<ForumSection> findByEnabledTrueOrderBySortOrderAscIdAsc();

    Optional<ForumSection> findByIdAndEnabledTrue(Long id);
}
