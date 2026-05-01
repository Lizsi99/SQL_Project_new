# WHERE Clauses and Filtering

## Basic Syntax

WHERE filters the rows returned by a query. Only rows where the condition evaluates to TRUE are included.

```sql
SELECT * FROM employees WHERE department_id = 10;
```

## Comparison Operators

| Operator | Meaning           |
|----------|-------------------|
| `=`      | Equal             |
| `<>` or `!=` | Not equal     |
| `<`      | Less than         |
| `>`      | Greater than      |
| `<=`     | Less than or equal|
| `>=`     | Greater than or equal |

```sql
SELECT * FROM employees WHERE salary > 50000;
SELECT * FROM employees WHERE hire_date < '2020-01-01';
```

## Logical Operators: AND, OR, NOT

Combine conditions with AND/OR. Use parentheses to control precedence:

```sql
SELECT * FROM employees
WHERE department_id = 10 AND salary > 60000;

SELECT * FROM employees
WHERE department_id = 10 OR department_id = 20;

SELECT * FROM employees
WHERE NOT department_id = 10;
```

AND has higher precedence than OR. Always use parentheses when mixing them:
```sql
-- Returns employees in dept 10 earning > 60k, OR all of dept 20:
WHERE department_id = 10 AND salary > 60000 OR department_id = 20

-- Clearer intent with parentheses:
WHERE (department_id = 10 OR department_id = 20) AND salary > 60000
```

## BETWEEN — Range Filtering

BETWEEN is inclusive of both endpoints:
```sql
SELECT * FROM employees WHERE salary BETWEEN 40000 AND 80000;
-- equivalent to: salary >= 40000 AND salary <= 80000

SELECT * FROM orders WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31';
```

## IN — Match a List of Values

More concise than multiple OR conditions:
```sql
SELECT * FROM employees WHERE department_id IN (10, 20, 30);
-- equivalent to: department_id = 10 OR department_id = 20 OR department_id = 30

SELECT * FROM products WHERE category NOT IN ('archived', 'discontinued');
```

## LIKE — Pattern Matching

`%` matches any sequence of characters, `_` matches exactly one character:
```sql
SELECT * FROM employees WHERE last_name LIKE 'S%';     -- starts with S
SELECT * FROM employees WHERE email LIKE '%@gmail.com'; -- ends with @gmail.com
SELECT * FROM employees WHERE last_name LIKE '_mith';  -- 5-letter names ending in mith

-- Case sensitivity depends on the database collation
-- PostgreSQL LIKE is case-sensitive; use ILIKE for case-insensitive
SELECT * FROM employees WHERE last_name ILIKE 's%'; -- PostgreSQL only
```

## IS NULL / IS NOT NULL

NULL cannot be compared with `=`. Always use IS NULL:
```sql
SELECT * FROM employees WHERE manager_id IS NULL;     -- top-level managers
SELECT * FROM employees WHERE commission_pct IS NOT NULL; -- commissioned employees
```

## Filtering with Subqueries

WHERE can reference a subquery:
```sql
SELECT * FROM employees
WHERE department_id IN (
    SELECT department_id FROM departments WHERE location_id = 1700
);
```

## HAVING vs WHERE

- WHERE filters rows **before** grouping.
- HAVING filters groups **after** GROUP BY.

```sql
-- Wrong: aggregate function not allowed in WHERE
SELECT department_id, AVG(salary)
FROM employees
WHERE AVG(salary) > 60000  -- ERROR
GROUP BY department_id;

-- Correct: use HAVING for aggregate conditions
SELECT department_id, AVG(salary)
FROM employees
GROUP BY department_id
HAVING AVG(salary) > 60000;
```

## Common Mistakes

- Using `= NULL` instead of `IS NULL` — the comparison always returns UNKNOWN, never TRUE.
- Forgetting operator precedence with AND/OR — always add parentheses when mixing.
- Using LIKE without a wildcard — `WHERE name LIKE 'Smith'` is equivalent to `WHERE name = 'Smith'`.
