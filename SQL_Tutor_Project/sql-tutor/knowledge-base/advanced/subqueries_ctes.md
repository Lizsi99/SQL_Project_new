# Subqueries and Common Table Expressions (CTEs)

## What is a Subquery?

A subquery is a SELECT statement nested inside another query. It can appear in SELECT, FROM, WHERE, or HAVING.

## Subquery in WHERE (non-correlated)

A non-correlated subquery runs once and its result is used by the outer query:
```sql
-- Employees earning more than the average salary
SELECT first_name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);
```

```sql
-- Employees in departments located in London
SELECT first_name
FROM employees
WHERE department_id IN (
    SELECT department_id
    FROM departments
    WHERE location_id = (SELECT location_id FROM locations WHERE city = 'London')
);
```

## Subquery in FROM (Derived Table / Inline View)

Use a subquery as a temporary table — must be aliased:
```sql
SELECT dept_avg.department_id, dept_avg.avg_sal
FROM (
    SELECT department_id, AVG(salary) AS avg_sal
    FROM employees
    GROUP BY department_id
) dept_avg
WHERE dept_avg.avg_sal > 60000;
```

## Subquery in SELECT (Scalar Subquery)

A scalar subquery returns exactly one row and one column:
```sql
SELECT
    first_name,
    salary,
    (SELECT AVG(salary) FROM employees) AS company_avg,
    salary - (SELECT AVG(salary) FROM employees) AS diff_from_avg
FROM employees;
```

Warning: scalar subqueries in SELECT run once per row — use a JOIN or CTE for better performance on large tables.

## Correlated Subquery

A correlated subquery references a column from the outer query. It re-executes for every row of the outer query:
```sql
-- Employees who earn more than the average in their own department
SELECT first_name, salary, department_id
FROM employees e_outer
WHERE salary > (
    SELECT AVG(salary)
    FROM employees e_inner
    WHERE e_inner.department_id = e_outer.department_id  -- correlation
);
```

Correlated subqueries are powerful but can be slow on large datasets. Consider rewriting with a JOIN + window function.

## EXISTS and NOT EXISTS

EXISTS returns TRUE if the subquery returns at least one row (doesn't matter what value):
```sql
-- Departments that have at least one employee
SELECT department_name
FROM departments d
WHERE EXISTS (
    SELECT 1 FROM employees e WHERE e.department_id = d.department_id
);

-- Departments with no employees
SELECT department_name
FROM departments d
WHERE NOT EXISTS (
    SELECT 1 FROM employees e WHERE e.department_id = d.department_id
);
```

EXISTS is often more efficient than IN for large datasets because it short-circuits on the first match.

## Common Table Expressions (CTEs)

A CTE defines a named temporary result set using the WITH clause. It improves readability and can be referenced multiple times.

```sql
WITH dept_averages AS (
    SELECT department_id, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department_id
)
SELECT e.first_name, e.salary, da.avg_salary
FROM employees e
JOIN dept_averages da ON e.department_id = da.department_id
WHERE e.salary > da.avg_salary;
```

## Multiple CTEs

Chain multiple CTEs separated by commas:
```sql
WITH
high_earners AS (
    SELECT employee_id, department_id
    FROM employees
    WHERE salary > 80000
),
dept_counts AS (
    SELECT department_id, COUNT(*) AS high_earner_count
    FROM high_earners
    GROUP BY department_id
)
SELECT d.department_name, dc.high_earner_count
FROM departments d
JOIN dept_counts dc ON d.department_id = dc.department_id
ORDER BY dc.high_earner_count DESC;
```

## Recursive CTEs

Recursive CTEs can traverse hierarchical or tree-structured data:
```sql
-- Traverse the management hierarchy from top to bottom
WITH RECURSIVE org_chart AS (
    -- Base case: top-level employee (no manager)
    SELECT employee_id, first_name, manager_id, 0 AS level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: find direct reports of each level
    SELECT e.employee_id, e.first_name, e.manager_id, oc.level + 1
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.employee_id
)
SELECT level, first_name FROM org_chart ORDER BY level, first_name;
```

## CTE vs Subquery — When to Use Which

| Aspect            | CTE                          | Subquery                          |
|-------------------|------------------------------|-----------------------------------|
| Readability       | Better for complex queries   | OK for simple, single-use cases   |
| Reuse             | Reference multiple times     | Must repeat                       |
| Recursive queries | Supported (WITH RECURSIVE)   | Not possible                      |
| Performance       | Similar (optimizer may inline)| Similar                          |
| Debugging         | Easier (test each CTE alone)  | Harder to isolate                 |

Prefer CTEs for any query with more than one level of nesting.
