# ORDER BY, GROUP BY, and Aggregate Functions

## ORDER BY — Sorting Results

Sort results by one or more columns. Default is ascending (ASC):
```sql
SELECT first_name, salary FROM employees ORDER BY salary DESC;
SELECT first_name, last_name FROM employees ORDER BY last_name ASC, first_name ASC;
```

You can order by column position (not recommended — fragile):
```sql
SELECT first_name, salary FROM employees ORDER BY 2 DESC; -- sorts by salary
```

NULL values sort last in ASC order in most databases. Use NULLS FIRST / NULLS LAST in PostgreSQL:
```sql
SELECT first_name, commission_pct FROM employees ORDER BY commission_pct NULLS FIRST;
```

## Aggregate Functions

Aggregate functions operate on sets of rows and return a single value per group.

| Function       | Description                         |
|---------------|-------------------------------------|
| `COUNT(*)`    | Count all rows (including NULLs)    |
| `COUNT(col)`  | Count non-NULL values in column     |
| `SUM(col)`    | Sum of all non-NULL values          |
| `AVG(col)`    | Average of non-NULL values          |
| `MIN(col)`    | Minimum value                       |
| `MAX(col)`    | Maximum value                       |

```sql
SELECT COUNT(*) AS total_employees FROM employees;
SELECT AVG(salary) AS avg_salary, MAX(salary) AS max_salary FROM employees;
```

## GROUP BY — Grouping Rows

GROUP BY groups rows with the same values and applies aggregates per group:

```sql
SELECT department_id, COUNT(*) AS headcount, AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id;
```

Every column in SELECT that is NOT an aggregate must appear in GROUP BY:
```sql
-- Valid:
SELECT department_id, job_id, AVG(salary)
FROM employees
GROUP BY department_id, job_id;

-- Invalid (first_name not in GROUP BY and not aggregated):
SELECT department_id, first_name, AVG(salary)
FROM employees
GROUP BY department_id;  -- ERROR in most databases
```

## HAVING — Filtering Groups

HAVING filters groups after aggregation. Use WHERE to filter rows, HAVING to filter groups:

```sql
-- Departments with more than 5 employees and average salary above 50000
SELECT department_id, COUNT(*) AS headcount, AVG(salary) AS avg_salary
FROM employees
WHERE hire_date > '2015-01-01'         -- filter rows first
GROUP BY department_id
HAVING COUNT(*) > 5                     -- then filter groups
   AND AVG(salary) > 50000;
```

## Query Execution Order

SQL clauses execute in this logical order (not the written order):
1. **FROM** — identify source tables
2. **WHERE** — filter individual rows
3. **GROUP BY** — group remaining rows
4. **HAVING** — filter groups
5. **SELECT** — compute output columns
6. **ORDER BY** — sort final result
7. **LIMIT/OFFSET** — restrict row count

This is why you cannot reference a SELECT alias in WHERE — WHERE runs before SELECT.

```sql
-- This fails: alias 'annual_salary' not yet defined when WHERE runs
SELECT salary * 12 AS annual_salary FROM employees WHERE annual_salary > 60000;

-- Fix with a subquery or CTE:
SELECT * FROM (
    SELECT salary * 12 AS annual_salary FROM employees
) sub
WHERE annual_salary > 60000;
```

## COUNT(*) vs COUNT(column)

```sql
SELECT
    COUNT(*) AS all_rows,          -- counts every row including NULLs
    COUNT(commission_pct) AS commissioned  -- counts only non-NULL values
FROM employees;
```

## DISTINCT with Aggregates

```sql
SELECT COUNT(DISTINCT department_id) AS dept_count FROM employees;
-- counts unique department IDs, not total rows
```

## Common Patterns

```sql
-- Top departments by headcount
SELECT department_id, COUNT(*) AS n
FROM employees
GROUP BY department_id
ORDER BY n DESC
LIMIT 5;

-- Salary statistics per job
SELECT job_id, MIN(salary), MAX(salary), AVG(salary), COUNT(*)
FROM employees
GROUP BY job_id
HAVING COUNT(*) >= 3
ORDER BY AVG(salary) DESC;
```
