# Window Functions

## What Are Window Functions?

Window functions perform calculations across a set of rows related to the current row — without collapsing rows the way GROUP BY does. Each row keeps its identity in the result.

```sql
SELECT
    first_name,
    department_id,
    salary,
    AVG(salary) OVER (PARTITION BY department_id) AS dept_avg
FROM employees;
-- Every row is returned; dept_avg shows the average for that employee's department
```

## Basic Syntax

```sql
function_name(arguments) OVER (
    [PARTITION BY partition_columns]
    [ORDER BY order_columns]
    [ROWS/RANGE BETWEEN frame_start AND frame_end]
)
```

## PARTITION BY

Divides rows into groups (partitions) within which the function computes independently. Think of it as GROUP BY that doesn't collapse rows:

```sql
-- Rank employees within each department
SELECT
    first_name,
    department_id,
    salary,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_rank
FROM employees;
```

Omit PARTITION BY to treat the entire result set as one partition:
```sql
SELECT first_name, salary,
       RANK() OVER (ORDER BY salary DESC) AS overall_rank
FROM employees;
```

## Ranking Functions

### ROW_NUMBER — Unique sequential rank, no ties
```sql
SELECT first_name, salary,
       ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num
FROM employees;
```

### RANK — Ties get same rank; next rank skips numbers
```sql
-- Salaries: 90k, 80k, 80k, 70k → ranks: 1, 2, 2, 4
SELECT first_name, salary,
       RANK() OVER (ORDER BY salary DESC) AS rnk
FROM employees;
```

### DENSE_RANK — Ties get same rank; no gaps
```sql
-- Salaries: 90k, 80k, 80k, 70k → ranks: 1, 2, 2, 3
SELECT first_name, salary,
       DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rnk
FROM employees;
```

### NTILE — Divide rows into N roughly equal buckets
```sql
-- Divide employees into salary quartiles
SELECT first_name, salary,
       NTILE(4) OVER (ORDER BY salary) AS quartile
FROM employees;
```

## Aggregate Window Functions

Use standard aggregates with OVER to compute running or grouped aggregates without collapsing rows:
```sql
SELECT
    first_name,
    hire_date,
    salary,
    SUM(salary) OVER (ORDER BY hire_date) AS running_total,
    AVG(salary) OVER () AS overall_avg,
    salary - AVG(salary) OVER (PARTITION BY department_id) AS diff_from_dept_avg
FROM employees;
```

## LAG and LEAD — Access Adjacent Rows

LAG accesses a previous row; LEAD accesses a following row:
```sql
SELECT
    order_date,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY order_date) AS prev_revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY order_date) AS change
FROM daily_sales;
```

```sql
-- Compare each employee's salary to the next highest earner
SELECT
    first_name, salary,
    LEAD(salary) OVER (ORDER BY salary DESC) AS next_lower_salary
FROM employees;
```

LAG/LEAD accept an optional default for when no previous/next row exists:
```sql
LAG(revenue, 1, 0) OVER (ORDER BY order_date)  -- default 0 for first row
```

## FIRST_VALUE and LAST_VALUE

Retrieve the first or last value in the window frame:
```sql
SELECT
    first_name, department_id, salary,
    FIRST_VALUE(first_name) OVER (
        PARTITION BY department_id ORDER BY salary DESC
    ) AS top_earner_in_dept
FROM employees;
```

LAST_VALUE requires an explicit frame to be useful (default frame only goes to current row):
```sql
LAST_VALUE(first_name) OVER (
    PARTITION BY department_id ORDER BY salary DESC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
) AS lowest_earner_in_dept
```

## Window Frames: ROWS vs RANGE

The frame clause defines which rows are included in the calculation relative to the current row:
```sql
-- Rolling 3-row average (current row + 2 preceding)
SELECT order_date, revenue,
       AVG(revenue) OVER (
           ORDER BY order_date
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       ) AS rolling_3day_avg
FROM daily_sales;
```

Common frame specs:
- `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` — running total (default with ORDER BY)
- `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` — 3-row rolling window
- `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` — entire partition

## Top-N Per Group Pattern

Get the top N rows per group using ROW_NUMBER in a CTE or subquery:
```sql
WITH ranked AS (
    SELECT
        first_name, department_id, salary,
        ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
    FROM employees
)
SELECT first_name, department_id, salary
FROM ranked
WHERE rn <= 3;  -- top 3 earners per department
```

## Key Differences: Window vs GROUP BY

| Feature              | GROUP BY + Aggregate | Window Function       |
|----------------------|----------------------|-----------------------|
| Collapses rows       | Yes                  | No                    |
| Access to other cols | Only aggregated/grouped | Any column in SELECT |
| Relative row access  | No                   | Yes (LAG/LEAD)        |
| Multiple partitions  | One GROUP BY         | Multiple PARTITION BY |
