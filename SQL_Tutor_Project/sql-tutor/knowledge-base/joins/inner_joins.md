# INNER JOIN

## What is a JOIN?

A JOIN combines rows from two or more tables based on a related column. Without a JOIN, you'd need to run multiple queries and manually match results.

## INNER JOIN Syntax

An INNER JOIN returns only rows where the join condition is TRUE in **both** tables. Non-matching rows are excluded.

```sql
SELECT columns
FROM table_a
INNER JOIN table_b ON table_a.key = table_b.key;
```

The `INNER` keyword is optional — `JOIN` alone defaults to INNER JOIN:
```sql
SELECT e.first_name, e.last_name, d.department_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id;
```

## Table Aliases

Always alias tables when joining to keep queries readable:
```sql
SELECT e.first_name, d.department_name, l.city
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN locations l   ON d.location_id   = l.location_id;
```

## Joining Multiple Tables

Chain multiple JOINs to traverse relationships:
```sql
SELECT
    e.first_name,
    e.last_name,
    d.department_name,
    j.job_title,
    l.city
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN jobs j        ON e.job_id        = j.job_id
JOIN locations l   ON d.location_id   = l.location_id
WHERE l.country_id = 'US';
```

## Joining on Multiple Conditions

Use AND in the ON clause when the join requires multiple columns:
```sql
SELECT *
FROM order_items oi
JOIN product_prices pp
  ON oi.product_id = pp.product_id
 AND oi.order_date BETWEEN pp.valid_from AND pp.valid_to;
```

## USING Clause (shorthand)

When the join column has the same name in both tables, USING is cleaner:
```sql
SELECT e.first_name, d.department_name
FROM employees e
JOIN departments d USING (department_id);
-- equivalent to: ON e.department_id = d.department_id
```

## When Does INNER JOIN Exclude Rows?

Any employee without a matching department_id in the departments table is dropped:
```sql
-- If an employee has department_id = NULL or a value not in departments,
-- they won't appear in the result
SELECT e.first_name, d.department_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id;
```

Use a LEFT JOIN if you want to keep all employees regardless.

## Self Join — Joining a Table to Itself

Useful for hierarchical data like employee-manager relationships:
```sql
SELECT
    e.first_name AS employee,
    m.first_name AS manager
FROM employees e
JOIN employees m ON e.manager_id = m.employee_id;
-- Note: employees without a manager are excluded
```

## Common Mistakes

- **Forgetting the ON condition**: `FROM a JOIN b` without ON produces a Cartesian product.
- **Ambiguous column names**: When the same column name exists in both tables, always prefix it with the table alias.
- **Assuming INNER JOIN keeps NULLs**: NULL = NULL is FALSE in SQL, so rows with NULL join keys are always dropped.

```sql
-- Ambiguous: which table does department_id come from?
SELECT department_id FROM employees JOIN departments ON employees.department_id = departments.department_id;

-- Clear:
SELECT e.department_id FROM employees e JOIN departments d ON e.department_id = d.department_id;
```
