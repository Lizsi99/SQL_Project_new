# DML: INSERT, UPDATE, and DELETE

DML (Data Manipulation Language) modifies data within tables. These statements change the rows (not the structure) of a table.

## INSERT INTO

### Insert a single row
```sql
INSERT INTO employees (employee_id, first_name, last_name, email, hire_date, salary)
VALUES (1001, 'Alice', 'Johnson', 'alice@example.com', '2024-03-15', 72000.00);
```

Always list the columns explicitly — if the table structure changes, an unqualified INSERT will fail or insert values into wrong columns.

### Insert multiple rows at once
```sql
INSERT INTO departments (department_id, department_name, location_id)
VALUES
    (10, 'Engineering',  1700),
    (20, 'Marketing',    1800),
    (30, 'Human Resources', 1700);
```

### INSERT with DEFAULT
Omit a column to use its default value, or use the DEFAULT keyword:
```sql
INSERT INTO employees (employee_id, first_name, last_name, email, hire_date, salary, status)
VALUES (1002, 'Bob', 'Smith', 'bob@example.com', '2024-04-01', 65000, DEFAULT);
-- status gets the DEFAULT value defined in CREATE TABLE
```

### INSERT INTO ... SELECT
Populate a table from a query result:
```sql
INSERT INTO employees_archive
SELECT * FROM employees WHERE hire_date < '2020-01-01';
```

### UPSERT (INSERT OR UPDATE)

Insert a row; update it if a conflict occurs on a unique key:

PostgreSQL:
```sql
INSERT INTO user_scores (user_id, score)
VALUES (42, 9500)
ON CONFLICT (user_id) DO UPDATE SET score = EXCLUDED.score;
```

MySQL:
```sql
INSERT INTO user_scores (user_id, score)
VALUES (42, 9500)
ON DUPLICATE KEY UPDATE score = VALUES(score);
```

## UPDATE

### Update specific rows
```sql
UPDATE employees
SET salary = salary * 1.10,       -- 10% raise
    last_updated = CURRENT_TIMESTAMP
WHERE department_id = 10
  AND hire_date < '2022-01-01';
```

Always include a WHERE clause — without it, every row is updated:
```sql
-- DANGEROUS: updates ALL rows
UPDATE employees SET salary = 0;
```

### Update with a JOIN (UPDATE ... FROM)
PostgreSQL syntax:
```sql
UPDATE employees e
SET salary = e.salary * 1.05
FROM departments d
WHERE e.department_id = d.department_id
  AND d.department_name = 'Engineering';
```

MySQL syntax:
```sql
UPDATE employees e
JOIN departments d ON e.department_id = d.department_id
SET e.salary = e.salary * 1.05
WHERE d.department_name = 'Engineering';
```

### Update with a subquery
```sql
UPDATE employees
SET department_id = (
    SELECT department_id FROM departments WHERE department_name = 'Sales'
)
WHERE job_id = 'SA_REP';
```

## DELETE

### Delete specific rows
```sql
DELETE FROM employees WHERE employee_id = 1001;
```

Without WHERE, all rows are deleted (table structure remains):
```sql
-- DANGEROUS: deletes every row
DELETE FROM employees;
```

### DELETE with a subquery
```sql
-- Delete employees from departments with no budget
DELETE FROM employees
WHERE department_id IN (
    SELECT department_id FROM departments WHERE budget IS NULL
);
```

### DELETE with JOIN (MySQL)
```sql
DELETE e
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE d.department_name = 'Closed';
```

### RETURNING clause (PostgreSQL)
See what was changed:
```sql
DELETE FROM employees
WHERE hire_date < '2010-01-01'
RETURNING employee_id, first_name, last_name;
```

```sql
UPDATE employees SET salary = salary * 1.1 WHERE department_id = 10
RETURNING employee_id, salary;
```

## Safe Update/Delete Workflow

1. **Preview first** — run a SELECT with the same WHERE clause before changing data:
```sql
-- Preview what will be deleted:
SELECT * FROM employees WHERE hire_date < '2015-01-01';
-- Then delete:
DELETE FROM employees WHERE hire_date < '2015-01-01';
```

2. **Use transactions** — wrap destructive operations in a transaction so you can roll back:
```sql
BEGIN;
DELETE FROM employees WHERE department_id = 99;
-- Review the count: SELECT COUNT(*) FROM employees;
ROLLBACK;   -- undo if something is wrong
-- or:
COMMIT;     -- make it permanent
```

## Row Count After DML

Most databases return the number of affected rows automatically. Retrieve it explicitly:
```sql
-- PostgreSQL: after DELETE/UPDATE, check with GET DIAGNOSTICS
-- Or simply use RETURNING to count:
WITH deleted AS (
    DELETE FROM old_logs WHERE created_at < NOW() - INTERVAL '90 days'
    RETURNING 1
)
SELECT COUNT(*) AS rows_deleted FROM deleted;
```
