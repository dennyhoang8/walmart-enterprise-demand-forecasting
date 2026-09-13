-- List warehouse tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Inspect primary and foreign-key constraints
SELECT
    table_name,
    constraint_name,
    constraint_type
FROM information_schema.table_constraints
WHERE table_schema = 'public'
ORDER BY table_name, constraint_type;

-- Verify indexes
SELECT
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;