# Indexes and Query Performance

## What Is an Index?

An index is a data structure that allows the database engine to find rows faster without scanning the entire table. Think of it like a book index — instead of reading every page, you jump directly to the relevant entries.

Without an index, the database does a **full table scan** (reads every row). On millions of rows this is slow.

## Creating Indexes

```sql
-- Single-column index
CREATE INDEX idx_employees_last_name ON employees (last_name);

-- Unique index (also enforces uniqueness constraint)
CREATE UNIQUE INDEX idx_employees_email ON employees (email);

-- Multi-column (composite) index
CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);

-- Drop an index
DROP INDEX idx_employees_last_name;
```

## Types of Indexes

### B-Tree Index (default)
Best for equality and range queries. Supports `=`, `<`, `>`, `BETWEEN`, `LIKE 'abc%'` (prefix patterns only).

```sql
-- Uses the index:
WHERE last_name = 'Smith'
WHERE salary BETWEEN 50000 AND 80000
WHERE last_name LIKE 'Sm%'

-- Does NOT use the index:
WHERE last_name LIKE '%mith'    -- leading wildcard
WHERE UPPER(last_name) = 'SMITH'  -- function on the column
```

### Hash Index
Best for equality only (`=`). Faster than B-tree for exact lookups but useless for range queries.

### Full-Text Index
For text search (`MATCH ... AGAINST` in MySQL, `tsvector/tsquery` in PostgreSQL). Supports searching words within long text fields.

### Partial Index (PostgreSQL)
Index only a subset of rows — saves space and is faster for selective queries:
```sql
CREATE INDEX idx_active_orders ON orders (customer_id)
WHERE status = 'active';
```

## When to Add an Index

Add an index when:
- The column is frequently used in WHERE, JOIN ON, or ORDER BY
- The column has high cardinality (many distinct values — e.g., email, user_id)
- The table is large (millions of rows)

Avoid indexes on:
- Small tables (full scan is faster than index lookup)
- Columns with very low cardinality (e.g., boolean flag — only 2 distinct values)
- Columns that are written frequently (indexes slow down INSERT/UPDATE/DELETE)

## EXPLAIN / EXPLAIN ANALYZE

Use EXPLAIN to see how the database plans to execute a query:

```sql
-- PostgreSQL
EXPLAIN SELECT * FROM employees WHERE department_id = 10;
EXPLAIN ANALYZE SELECT * FROM employees WHERE department_id = 10;  -- actually runs it

-- MySQL
EXPLAIN SELECT * FROM employees WHERE department_id = 10;

-- SQL Server
SET STATISTICS IO ON;
SELECT * FROM employees WHERE department_id = 10;
```

Key things to look for in the execution plan:
- **Seq Scan / Table Scan**: full table scan — may need an index
- **Index Scan**: using an index — good
- **Index Only Scan**: reads only the index, never touches the table — fastest
- **Nested Loop / Hash Join / Merge Join**: join strategies — hash join is usually fastest for large tables
- **rows / estimated vs actual**: large discrepancies indicate stale statistics

## Composite Index Column Order

A composite index `(a, b, c)` can be used for queries filtering on `a`, `a+b`, or `a+b+c`. It **cannot** be used for `b` alone or `c` alone.

```sql
CREATE INDEX idx_orders ON orders (customer_id, status, order_date);

-- Uses index:
WHERE customer_id = 5
WHERE customer_id = 5 AND status = 'active'
WHERE customer_id = 5 AND status = 'active' AND order_date > '2024-01-01'

-- Does NOT use index efficiently:
WHERE status = 'active'               -- skips leading column
WHERE order_date > '2024-01-01'       -- skips both leading columns
```

## Covering Index

An index that includes all columns referenced by a query allows an **index-only scan** — the fastest possible access:
```sql
-- Query only needs customer_id, order_date, total
SELECT customer_id, order_date, total FROM orders WHERE customer_id = 42;

-- This index "covers" the query:
CREATE INDEX idx_covering ON orders (customer_id, order_date, total);
```

## Common Performance Anti-Patterns

```sql
-- Wrapping indexed column in a function defeats the index:
WHERE YEAR(order_date) = 2024         -- instead use:
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'

-- Implicit type conversion:
WHERE employee_id = '123'             -- if employee_id is INT, string comparison may prevent index use

-- OR conditions on different columns may prevent index use:
WHERE first_name = 'John' OR last_name = 'Smith'  -- consider UNION instead

-- SELECT * forces more data to be read; select only needed columns
```

## Query Optimization Checklist

1. Run EXPLAIN and identify full table scans on large tables
2. Add indexes on JOIN columns and WHERE-clause columns with high selectivity
3. Rewrite functions on indexed columns to range conditions
4. Use covering indexes for frequently run read-heavy queries
5. Keep statistics up to date (`ANALYZE` in PostgreSQL, `UPDATE STATISTICS` in SQL Server)
6. Consider query rewrites: EXISTS vs IN, CTE vs subquery, proper JOIN order
