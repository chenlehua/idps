-- =============================================
-- IDPS ClickHouse Database Initialization Script
-- =============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS idps;

-- =============================================
-- 1. 网络入侵检测日志表
-- =============================================
CREATE TABLE IF NOT EXISTS idps.network_ids_logs
(
    `timestamp` DateTime64(3) COMMENT '时间戳',
    `vin` String COMMENT '车辆VIN',
    `event_type` LowCardinality(String) COMMENT '事件类型(alert, http, dns, tls等)',
    `severity` UInt8 COMMENT '严重程度(1-4)',
    `src_ip` IPv4 COMMENT '源IP',
    `src_port` UInt16 COMMENT '源端口',
    `dest_ip` IPv4 COMMENT '目标IP',
    `dest_port` UInt16 COMMENT '目标端口',
    `protocol` LowCardinality(String) COMMENT '协议',
    `signature_id` UInt32 COMMENT '签名ID',
    `signature` String COMMENT '签名描述',
    `category` LowCardinality(String) COMMENT '分类',
    `payload` String COMMENT '负载数据',
    `raw_log` String COMMENT '原始日志(JSON)',
    `created_date` Date DEFAULT toDate(timestamp) COMMENT '创建日期(用于分区)'
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_date)
ORDER BY (vin, timestamp, event_type)
TTL created_date + INTERVAL 90 DAY
SETTINGS index_granularity = 8192
COMMENT '网络入侵检测日志表';

-- =============================================
-- 2. 防火墙日志表
-- =============================================
CREATE TABLE IF NOT EXISTS idps.firewall_logs
(
    `timestamp` DateTime64(3) COMMENT '时间戳',
    `vin` String COMMENT '车辆VIN',
    `action` LowCardinality(String) COMMENT '动作(allow, drop, reject)',
    `src_ip` IPv4 COMMENT '源IP',
    `src_port` UInt16 COMMENT '源端口',
    `dest_ip` IPv4 COMMENT '目标IP',
    `dest_port` UInt16 COMMENT '目标端口',
    `protocol` LowCardinality(String) COMMENT '协议',
    `interface` LowCardinality(String) COMMENT '网络接口',
    `rule_id` UInt32 COMMENT '规则ID',
    `bytes` UInt64 COMMENT '字节数',
    `packets` UInt32 COMMENT '包数',
    `reason` String COMMENT '原因',
    `created_date` Date DEFAULT toDate(timestamp) COMMENT '创建日期(用于分区)'
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_date)
ORDER BY (vin, timestamp, action)
TTL created_date + INTERVAL 90 DAY
SETTINGS index_granularity = 8192
COMMENT '防火墙日志表';

-- =============================================
-- 3. 主机入侵检测日志表
-- =============================================
CREATE TABLE IF NOT EXISTS idps.host_ids_logs
(
    `timestamp` DateTime64(3) COMMENT '时间戳',
    `vin` String COMMENT '车辆VIN',
    `log_type` LowCardinality(String) COMMENT '日志类型(audit, file, process, root)',
    `severity` UInt8 COMMENT '严重程度(1-4)',
    `event` String COMMENT '事件描述',
    `file_path` String COMMENT '文件路径',
    `process_name` String COMMENT '进程名称',
    `process_id` UInt32 COMMENT '进程ID',
    `user` String COMMENT '用户',
    `command` String COMMENT '命令',
    `details` String COMMENT '详细信息(JSON)',
    `created_date` Date DEFAULT toDate(timestamp) COMMENT '创建日期(用于分区)'
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_date)
ORDER BY (vin, timestamp, log_type)
TTL created_date + INTERVAL 90 DAY
SETTINGS index_granularity = 8192
COMMENT '主机入侵检测日志表';

-- =============================================
-- 4. 性能监控数据表
-- =============================================
CREATE TABLE IF NOT EXISTS idps.performance_metrics
(
    `timestamp` DateTime COMMENT '时间戳',
    `vin` String COMMENT '车辆VIN',
    `cpu_usage` Float32 COMMENT 'CPU使用率(%)',
    `memory_usage` Float32 COMMENT '内存使用率(%)',
    `disk_usage` Float32 COMMENT '磁盘使用率(%)',
    `network_rx_bytes` UInt64 COMMENT '网络接收字节数',
    `network_tx_bytes` UInt64 COMMENT '网络发送字节数',
    `iops_read` UInt32 COMMENT '磁盘读IOPS',
    `iops_write` UInt32 COMMENT '磁盘写IOPS',
    `created_date` Date DEFAULT toDate(timestamp) COMMENT '创建日期(用于分区)'
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_date)
ORDER BY (vin, timestamp)
TTL created_date + INTERVAL 30 DAY
SETTINGS index_granularity = 8192
COMMENT '性能监控数据表';

-- =============================================
-- 创建物化视图用于实时统计
-- =============================================

-- 每小时网络告警统计
CREATE MATERIALIZED VIEW IF NOT EXISTS idps.network_alerts_hourly
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (vin, hour, severity)
AS SELECT
    toStartOfHour(timestamp) AS hour,
    vin,
    severity,
    count() AS alert_count
FROM idps.network_ids_logs
WHERE event_type = 'alert'
GROUP BY hour, vin, severity;

-- 每日车辆日志统计
CREATE MATERIALIZED VIEW IF NOT EXISTS idps.vehicle_log_stats_daily
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (vin, date)
AS SELECT
    toDate(timestamp) AS date,
    vin,
    count() AS total_logs,
    countIf(severity >= 3) AS high_severity_count
FROM idps.network_ids_logs
GROUP BY date, vin;

-- =============================================
-- End of ClickHouse Initialization Script
-- =============================================
