-- Active: 1766159591004@@4.tcp.ngrok.io@10242@typy
-- Query: For every table in the current database, get table name, total size (MB), number of rows, and average bytes per row (rounded to nearest integer)

SELECT 
    schemaname || '.' || relname AS table_name,
    n_live_tup AS row_count,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    CASE
        WHEN n_live_tup > 0 THEN
            ROUND(pg_total_relation_size(relid)::numeric / n_live_tup)
        ELSE NULL
    END AS bytes_per_row
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

