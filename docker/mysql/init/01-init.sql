-- =============================================
-- IDPS MySQL Database Initialization Script
-- =============================================

-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- =============================================
-- 1. 车辆信息表
-- =============================================
CREATE TABLE IF NOT EXISTS `vehicles` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `vin` VARCHAR(17) NOT NULL UNIQUE COMMENT '车辆识别代码',
    `device_fingerprint` VARCHAR(64) NOT NULL COMMENT '设备指纹(SHA256)',
    `manufacturer` VARCHAR(100) DEFAULT NULL COMMENT '制造商',
    `model` VARCHAR(100) DEFAULT NULL COMMENT '车型',
    `year` SMALLINT UNSIGNED DEFAULT NULL COMMENT '年份',
    `status` ENUM('active', 'inactive', 'blocked') DEFAULT 'inactive' COMMENT '状态',
    `last_heartbeat_at` DATETIME DEFAULT NULL COMMENT '最后心跳时间',
    `last_ip` VARCHAR(45) DEFAULT NULL COMMENT '最后连接IP',
    `software_version` VARCHAR(50) DEFAULT NULL COMMENT '软件版本',
    `registered_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_vin` (`vin`),
    INDEX `idx_status` (`status`),
    INDEX `idx_last_heartbeat` (`last_heartbeat_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='车辆信息表';

-- =============================================
-- 2. 规则版本表
-- =============================================
CREATE TABLE IF NOT EXISTS `rule_versions` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `rule_type` ENUM('network', 'firewall', 'host') NOT NULL COMMENT '规则类型',
    `version` VARCHAR(20) NOT NULL COMMENT '版本号(如: 1.0.0)',
    `file_path` VARCHAR(255) NOT NULL COMMENT '规则文件路径',
    `file_size` BIGINT UNSIGNED NOT NULL COMMENT '文件大小(字节)',
    `checksum` VARCHAR(64) NOT NULL COMMENT '文件校验和(SHA256)',
    `signature` TEXT DEFAULT NULL COMMENT '文件签名',
    `description` TEXT DEFAULT NULL COMMENT '版本描述',
    `status` ENUM('draft', 'published', 'archived') DEFAULT 'draft' COMMENT '状态',
    `published_at` DATETIME DEFAULT NULL COMMENT '发布时间',
    `created_by` VARCHAR(100) DEFAULT NULL COMMENT '创建人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY `uk_type_version` (`rule_type`, `version`),
    INDEX `idx_rule_type` (`rule_type`),
    INDEX `idx_status` (`status`),
    INDEX `idx_published_at` (`published_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='规则版本表';

-- =============================================
-- 3. 规则下发记录表
-- =============================================
CREATE TABLE IF NOT EXISTS `rule_deployments` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `rule_version_id` BIGINT UNSIGNED NOT NULL COMMENT '规则版本ID',
    `vin` VARCHAR(17) NOT NULL COMMENT '车辆VIN',
    `status` ENUM('pending', 'downloading', 'success', 'failed') DEFAULT 'pending' COMMENT '下发状态',
    `deployed_at` DATETIME DEFAULT NULL COMMENT '下发时间',
    `completed_at` DATETIME DEFAULT NULL COMMENT '完成时间',
    `error_message` TEXT DEFAULT NULL COMMENT '错误信息',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_rule_version` (`rule_version_id`),
    INDEX `idx_vin` (`vin`),
    INDEX `idx_status` (`status`),
    INDEX `idx_deployed_at` (`deployed_at`),
    FOREIGN KEY (`rule_version_id`) REFERENCES `rule_versions`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='规则下发记录表';

-- =============================================
-- 4. 用户表（管理后台用户）
-- =============================================
CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `role` ENUM('admin', 'operator', 'viewer') DEFAULT 'viewer' COMMENT '角色',
    `status` ENUM('active', 'inactive', 'locked') DEFAULT 'active' COMMENT '状态',
    `last_login_at` DATETIME DEFAULT NULL COMMENT '最后登录时间',
    `last_login_ip` VARCHAR(45) DEFAULT NULL COMMENT '最后登录IP',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_username` (`username`),
    INDEX `idx_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- =============================================
-- 5. 审计日志表
-- =============================================
CREATE TABLE IF NOT EXISTS `audit_logs` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `user_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '用户ID',
    `action` VARCHAR(50) NOT NULL COMMENT '操作类型',
    `resource_type` VARCHAR(50) DEFAULT NULL COMMENT '资源类型',
    `resource_id` VARCHAR(100) DEFAULT NULL COMMENT '资源ID',
    `details` JSON DEFAULT NULL COMMENT '详细信息',
    `ip_address` VARCHAR(45) DEFAULT NULL COMMENT 'IP地址',
    `user_agent` VARCHAR(255) DEFAULT NULL COMMENT 'User Agent',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_action` (`action`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审计日志表';

-- =============================================
-- 插入默认管理员用户
-- 用户名: admin
-- 密码: Admin@123456 (请在生产环境中修改)
-- =============================================
INSERT INTO `users` (`username`, `password_hash`, `email`, `role`, `status`)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MRp7gK', 'admin@idps.local', 'admin', 'active')
ON DUPLICATE KEY UPDATE `username` = `username`;

SET FOREIGN_KEY_CHECKS = 1;

-- =============================================
-- End of MySQL Initialization Script
-- =============================================
