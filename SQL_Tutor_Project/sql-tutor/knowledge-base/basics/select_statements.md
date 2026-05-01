# SELECT Statements

## Basic Syntax

The SELECT statement retrieves data from one or more tables.

```sql
SELECT column1, column2 FROM table_name;
```

Use `*` to select all columns:
```sql
SELECT * FROM employees;
```

## Selecting Specific Columns

Always prefer naming specific columns over `SELECT *` in production queries — it makes intent explicit and avoids fetching unnecessary data.

```sql
SELECT first_name, last_name, salary
FROM employees;
```

## Column Aliases

Use `AS` to rename a column in the result set:
```sql
SELECT first_name AS "First Name", salary * 12 AS annual_salary
FROM employees;
```

The `AS` keyword is optional but improves readability:
```sql
SELECT first_name first_name, last_name last_name FROM employees;
```

## DISTINCT — Remove Duplicates

`DISTINCT` eliminates duplicate rows from results:
```sql
SELECT DISTINCT department_id FROM employees;
```

For multiple columns, the combination must be unique:
```sql
SELECT DISTINCT department_id, job_id FROM employees;
```

## LIMIT and OFFSET — Paginating Results

Restrict how many rows are returned:
```sql
SELECT * FROM employees LIMIT 10;
```

Skip rows with OFFSET (useful for pagination):
```sql
SELECT * FROM employees LIMIT 10 OFFSET 20;  -- rows 21-30
```

In SQL Server the equivalent is `TOP`:
```sql
SELECT TOP 10 * FROM employees;
```

## Expressions and Calculations

You can compute values directly in SELECT:
```sql
SELECT
    first_name,
    salary,
    salary * 1.10 AS salary_with_raise,
    UPPER(last_name) AS last_name_upper
FROM employees;
```

## NULL Values

A NULL value means "unknown" or "missing". It is NOT zero or an empty string.

```sql
SELECT first_name, commission_pct
FROM employees
WHERE commission_pct IS NULL;      -- finds NULLs

WHERE commission_pct IS NOT NULL;  -- excludes NULLs
```

Use COALESCE to substitute a default for NULL:
```sql
SELECT first_name, COALESCE(commission_pct, 0) AS commission
FROM employees;
```

## Common Mistakes

- `SELECT *` in production code hides intent and returns unused columns.
- Comparing to NULL with `=` never returns true — always use `IS NULL`.
- Column aliases defined in SELECT cannot be referenced in WHERE (use a subquery or CTE instead).
