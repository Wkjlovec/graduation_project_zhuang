package com.graduation.authuser.repository;

import com.graduation.authuser.domain.UserAccount;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserAccountRepository extends JpaRepository<UserAccount, Long> {

    boolean existsByUsername(String username);

    Optional<UserAccount> findByUsername(String username);
}
