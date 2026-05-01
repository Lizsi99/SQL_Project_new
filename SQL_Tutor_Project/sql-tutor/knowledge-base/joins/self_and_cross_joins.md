# Self Joins and CROSS JOIN

## Self Join

A self join joins a table to itself. There is no special syntax — just alias the table twice.

### Use Case: Hierarchical Data (Employee-Manager)

```sql
SELECT
    e.first_name  AS employee_name,
    m.first_name  AS manager_name
FROM employees e
JOIN employees m ON e.manager_id = m.employee_id
ORDER BY manager_name, employee_name;
```

Here, `e` is the employee row and `m` is the manager row — both from the same table.

### Finding Employees with the Same Manager

```sql
SELECT a.first_name AS employee_a, b.first_name AS employee_b, a.manager_id
FROM employees a
JOIN employees b
  ON a.manager_id = b.manager_id
 AND a.employee_id < b.employee_id   -- avoid duplicate pairs (A,B) and (B,A)
ORDER BY a.manager_id;
```

### Use Case: Comparing Rows Within the Same Table

Find all pairs of products in the same category with different prices:
```sql
SELECT a.product_name, b.product_name, a.category_id
FROM products a
JOIN products b
  ON a.category_id = b.category_id
 AND a.product_id < b.product_id;
```

### Self Join with LEFT JOIN

Include top-level employees (those with no manager):
```sql
SELECT
    e.first_name  AS employee_name,
    m.first_name  AS manager_name   -- NULL for top-level employees
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id;
```

## CROSS JOIN — Cartesian Product

A CROSS JOIN returns every combination of rows from both tables (M rows × N rows = M×N result rows). There is no ON condition.

```sql
SELECT colors.color, sizes.size
FROM colors
CROSS JOIN sizes;
```

If `colors` has 3 rows and `sizes` has 4 rows, the result has 12 rows.

### Use Case: Generating Combinations

```sql
-- Generate a test schedule: all teams vs all dates
SELECT t.team_name, d.game_date
FROM teams t
CROSS JOIN schedule_dates d
ORDER BY d.game_date, t.team_name;
```

### Use Case: Creating a Number/Date Series

Cross join small sequences to build larger ranges:
```sql
-- Create numbers 1–100 (PostgreSQL example using generate_series is cleaner, but cross join works universally)
SELECT (tens.n * 10 + units.n) AS num
FROM (VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) tens(n)
CROSS JOIN (VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10)) units(n)
ORDER BY num;
```

### Accidental CROSS JOIN Warning

A CROSS JOIN without a WHERE condition on a large table can return billions of rows and crash your session:
```sql
-- Dangerous: if employees has 1000 rows and products has 5000, this returns 5,000,000 rows
SELECT * FROM employees, products;   -- implicit cross join syntax
```

Always include a meaningful WHERE or ON condition when joining tables.

## Summary

| Join Type   | Syntax                              | Result                               |
|-------------|-------------------------------------|--------------------------------------|
| Self Join   | `FROM t a JOIN t b ON a.x = b.y`   | Rows matched across copies of one table |
| CROSS JOIN  | `FROM a CROSS JOIN b`               | Every combination of rows (a × b)   |
