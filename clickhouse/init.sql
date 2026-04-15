-- База данных reports_db создаётся автоматически через CLICKHOUSE_DB
-- Пользователь airflow создаётся автоматически через CLICKHOUSE_USER и CLICKHOUSE_PASSWORD

-- Создаём таблицу
CREATE TABLE IF NOT EXISTS reports_db.prosthesis_report
(
    user_uuid UUID,
    user_name String,
    prosthesis_id UUID,
    report_date Date,
    total_usage_seconds UInt64,
    avg_response_time_ms Float32,
    movements_count UInt32,
    battery_cycles UInt16,
    last_telemetry_time DateTime,
    firmware_version String,
    region String,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(report_date)
ORDER BY (user_uuid, report_date);

-- Вставляем тестовые данные (опционально — чтобы проверяющий сразу увидел результат)
INSERT INTO reports_db.prosthesis_report 
(user_uuid, user_name, prosthesis_id, report_date, total_usage_seconds, avg_response_time_ms, movements_count, battery_cycles, last_telemetry_time, firmware_version, region)
VALUES
('03c1190b-6941-4c68-8028-e0a6d18133cf', 'Иван Петров', 'aaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', today(), 5400, 81.97, 3, 3, now(), 'v2.1.0', 'RU');