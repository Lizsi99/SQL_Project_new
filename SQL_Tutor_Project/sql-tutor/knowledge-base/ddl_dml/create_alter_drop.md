# DDL: CREATE, ALTER, and DROP

DDL (Data Definition Language) defines and modifies database structures — tables, columns, constraints, and indexes.

## CREATE TABLE

```sql
CREATE TABLE employees (
    employee_id   INT           PRIMARY KEY,
    first_name    VARCHAR(50)   NOT NULL,
    last_name     VARCHAR(50)   NOT NULL,
    email         VARCHAR(100)  UNIQUE NOT NULL,
    hire_date     DATE          NOT NULL,
    salary        DECIMAL(10,2) CHECK (salary > 0),
    department_id INT,
    manager_id    INT,

    CONSTRAINT fk_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id),
    CONSTRAINT fk_manager
        FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);
```

## Common Data Types

| Type                    | Description                                     |
|-------------------------|-------------------------------------------------|
| `INT` / `INTEGER`       | Whole numbers                                   |
| `BIGINT`                | Large whole numbers (> 2 billion)               |
| `DECIMAL(p,s)` / `NUMERIC` | Exact decimal (p total digits, s after point) |
| `FLOAT` / `DOUBLE`      | Approximate floating point                      |
| `VARCHAR(n)`            | Variable-length string up to n characters       |
| `CHAR(n)`               | Fixed-length string, padded with spaces         |
| `TEXT`                  | Unlimited-length text (PostgreSQL/MySQL)        |
| `DATE`                  | Date only (YYYY-MM-DD)                          |
| `TIMESTAMP`             | Date and time                                   |
| `BOOLEAN`               | TRUE/FALSE (PostgreSQL); TINYINT(1) in MySQL    |
| `SERIAL` / `AUTO_INCREMENT` | Auto-incrementing integer for primary keys  |

## Constraints

Constraints enforce data integrity at the database level:

### PRIMARY KEY
Uniquely identifies each row. Implies NOT NULL + UNIQUE. Every table should have one.
```sql
employee_id INT PRIMARY KEY
-- or at table level:
CONSTRAINT pk_employees PRIMARY KEY (employee_id)
```

### FOREIGN KEY
References a primary key in another table. Enforces referential integrity.
```sql
department_id INT REFERENCES departments(department_id)
-- or:
CONSTRAINT fk_dept FOREIGN KEY (department_id) REFERENCES departments(department_id)
    ON DELETE SET NULL   -- or CASCADE, RESTRICT, NO ACTION
    ON UPDATE CASCADE
```

### NOT NULL
Prevents NULL values in a column:
```sql
last_name VARCHAR(50) NOT NULL
```

### UNIQUE
Ensures no two rows have the same value (NULLs are allowed and not considered equal in most databases):
```sql
email VARCHAR(100) UNIQUE
```

### CHECK
Enforces a condition on column values:
```sql
salary DECIMAL(10,2) CHECK (salary > 0)
age    INT           CHECK (age BETWEEN 18 AND 120)
```

### DEFAULT
Provides a default value when none is specified on INSERT:
```sql
status      VARCHAR(20) DEFAULT 'active'
created_at  TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
```

## CREATE TABLE AS SELECT

Create and populate a table from a query result:
```sql
CREATE TABLE high_earners AS
SELECT * FROM employees WHERE salary > 80000;
```

## ALTER TABLE

Modify an existing table structure:

```sql
-- Add a column
ALTER TABLE employees ADD COLUMN phone_number VARCHAR(20);

-- Drop a column
ALTER TABLE employees DROP COLUMN phone_number;

-- Rename a column (PostgreSQL)
ALTER TABLE employees RENAME COLUMN phone_number TO mobile;

-- Change data type
ALTER TABLE employees ALTER COLUMN salary TYPE NUMERIC(12, 2);  -- PostgreSQL
ALTER TABLE employees MODIFY COLUMN salary DECIMAL(12,2);       -- MySQL

-- Add a constraint
ALTER TABLE employees ADD CONSTRAINT chk_salary CHECK (salary > 0);

-- Drop a constraint
ALTER TABLE employees DROP CONSTRAINT chk_salary;

-- Rename a table
ALTER TABLE employees RENAME TO staff;         -- PostgreSQL
RENAME TABLE employees TO staff;               -- MySQL
```

## DROP TABLE

Permanently removes a table and all its data:
```sql
DROP TABLE employees;

-- Only drop if it exists (no error if table doesn't exist):
DROP TABLE IF EXISTS employees;

-- CASCADE removes dependent objects (views, foreign keys) too:
DROP TABLE departments CASCADE;   -- PostgreSQL
```

Warning: DROP TABLE is irreversible (unless in a transaction). Always back up or double-check before executing.

## TRUNCATE TABLE

Removes all rows from a table but keeps the structure. Faster than DELETE with no WHERE clause because it doesn't log individual row deletions:
```sql
TRUNCATE TABLE temp_staging;
-- Cannot be rolled back in MySQL; can be rolled back in PostgreSQL within a transaction
```

## TEMP Tables

Temporary tables exist only for the current session:
```sql
CREATE TEMP TABLE temp_results AS
SELECT * FROM employees WHERE department_id = 10;

-- Automatically dropped when the session ends
-- Or explicitly:
DROP TABLE temp_results;
```
