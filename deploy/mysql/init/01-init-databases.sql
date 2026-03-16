CREATE DATABASE IF NOT EXISTS forum_system
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'forum_user'@'%' IDENTIFIED BY 'forum_pass_123';
GRANT ALL PRIVILEGES ON forum_system.* TO 'forum_user'@'%';
FLUSH PRIVILEGES;
