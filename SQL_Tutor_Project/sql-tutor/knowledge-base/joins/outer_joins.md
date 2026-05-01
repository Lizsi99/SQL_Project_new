# Outer Joins: LEFT, RIGHT, and FULL OUTER JOIN

## Why Outer Joins?

An INNER JOIN drops rows with no match. Outer joins preserve unmatched rows, filling missing columns with NULL.

## LEFT JOIN (LEFT OUTER JOIN)

Returns **all rows from the left table** and matched rows from the right table. Unmatched right-side columns become NULL.

```sql
SELECT e.first_name, d.department_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id;
```

Employees with no matching department still appear — `department_name` is NULL for them.

### Finding Unmatched Rows with LEFT JOIN

A common pattern: find rows in A with no match in B:
```sql
-- Employees not assigned to any department
SELECT e.first_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
WHERE d.department_id IS NULL;
```

### LEFT JOIN with Multiple Tables

When chaining LEFT JOINs, subsequent joins apply to the running result, not the base table:
```sql
SELECT e.first_name, d.department_name, l.city
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
LEFT JOIN locations l   ON d.location_id   = l.location_id;
-- employees with no department get NULL for both department_name and city
```

## RIGHT JOIN (RIGHT OUTER JOIN)

Returns **all rows from the right table** and matched rows from the left. Less common — a LEFT JOIN with tables swapped achieves the same result and is more readable.

```sql
SELECT e.first_name, d.department_name
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.department_id;
-- All departments appear, even those with no employees
```

Equivalent LEFT JOIN version:
```sql
SELECT e.first_name, d.department_name
FROM departments d
LEFT JOIN employees e ON e.department_id = d.department_id;
```

## FULL OUTER JOIN

Returns **all rows from both tables**. Rows with no match get NULL on the missing side.

```sql
SELECT e.first_name, d.department_name
FROM employees e
FULL OUTER JOIN departments d ON e.department_id = d.department_id;
-- Includes: matched pairs, employees without departments, departments without employees
```

MySQL does not support FULL OUTER JOIN. Simulate it with UNION:
```sql
SELECT e.first_name, d.department_name
FROM employees e LEFT JOIN departments d ON e.department_id = d.department_id
UNION
SELECT e.first_name, d.department_name
FROM employees e RIGHT JOIN departments d ON e.department_id = d.department_id;
```

## Filtering Outer Joins Correctly

Putting a filter on the right table in WHERE converts a LEFT JOIN to an INNER JOIN:
```sql
-- This behaves like INNER JOIN because WHERE drops NULL rows:
SELECT e.first_name, d.department_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
WHERE d.department_name = 'Sales';  -- drops employees with no department

-- To filter only within the joined table, move condition to ON:
SELECT e.first_name, d.department_name
FROM employees e
LEFT JOIN departments d
  ON e.department_id = d.department_id
  AND d.department_name = 'Sales';  -- non-Sales departments show as NULL, but employees remain
```

## Visual Summary

| Join Type         | Left-only rows | Matched rows | Right-only rows |
|-------------------|:-:|:-:|:-:|
| INNER JOIN        | ✗ | ✓ | ✗ |
| LEFT JOIN         | ✓ | ✓ | ✗ |
| RIGHT JOIN        | ✗ | ✓ | ✓ |
| FULL OUTER JOIN   | ✓ | ✓ | ✓ |

## Common Mistakes

- Treating LEFT JOIN like INNER JOIN by adding `WHERE right_table.col = value` — this silently drops unmatched rows.
- Confusing which table is "left" and which is "right" — left is the table in FROM, right is the table in JOIN.
- Forgetting that NULL = NULL is FALSE, so NULL join keys are never matched even in outer joins.
