# Transactions and ACID Properties

## What Is a Transaction?

A transaction is a sequence of SQL statements that are treated as a single unit of work. Either all statements succeed (COMMIT), or all are undone (ROLLBACK).

Classic example: transferring money between bank accounts:
```sql
BEGIN;

UPDATE accounts SET balance = balance - 500 WHERE account_id = 1;  -- debit
UPDATE accounts SET balance = balance + 500 WHERE account_id = 2;  -- credit

COMMIT;
-- Both updates happen together, or neither does
```

If an error occurs between the two UPDATEs, ROLLBACK restores both accounts to their original state.

## Transaction Control Statements

```sql
BEGIN;          -- start a transaction (also: START TRANSACTION)
COMMIT;         -- make all changes permanent
ROLLBACK;       -- undo all changes since BEGIN

SAVEPOINT sp1;                -- create a named savepoint
ROLLBACK TO SAVEPOINT sp1;    -- rollback only to this point
RELEASE SAVEPOINT sp1;        -- discard the savepoint
```

### Example with SAVEPOINT
```sql
BEGIN;

INSERT INTO orders (order_id, customer_id) VALUES (101, 42);
SAVEPOINT order_inserted;

INSERT INTO order_items (order_id, product_id, qty) VALUES (101, 5, 3);
-- If this fails:
ROLLBACK TO SAVEPOINT order_inserted;  -- undo only the order_items insert
-- The orders insert is still in the transaction

COMMIT;
```

## ACID Properties

ACID is the set of guarantees a transactional database provides:

### Atomicity
All operations in a transaction succeed or all are rolled back. There is no partial commit.

### Consistency
A transaction brings the database from one valid state to another. Constraints (FK, CHECK, NOT NULL) are enforced at COMMIT.

### Isolation
Concurrent transactions don't interfere with each other. Each transaction sees a consistent snapshot of the data.

### Durability
Once committed, data survives system failures (crashes, power loss). Changes are persisted to durable storage.

## Isolation Levels

Isolation levels control what a transaction can see from other concurrent transactions. Higher isolation = fewer anomalies but more locking/blocking.

| Isolation Level      | Dirty Read | Non-Repeatable Read | Phantom Read |
|----------------------|:----------:|:-------------------:|:------------:|
| READ UNCOMMITTED     | Possible   | Possible            | Possible     |
| READ COMMITTED       | Prevented  | Possible            | Possible     |
| REPEATABLE READ      | Prevented  | Prevented           | Possible     |
| SERIALIZABLE         | Prevented  | Prevented           | Prevented    |

**Anomaly definitions:**
- **Dirty Read**: Reading uncommitted changes from another transaction that may be rolled back.
- **Non-Repeatable Read**: Reading the same row twice in one transaction and getting different values (another transaction committed an UPDATE between reads).
- **Phantom Read**: Running the same query twice and getting different rows (another transaction committed an INSERT/DELETE between reads).

### Setting the Isolation Level

```sql
-- PostgreSQL / MySQL
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;
-- ...

-- PostgreSQL session default:
SET default_transaction_isolation = 'read committed';
```

Most databases default to **READ COMMITTED**. PostgreSQL uses MVCC (Multi-Version Concurrency Control) to implement isolation without exclusive read locks.

## Implicit vs Explicit Transactions

Most databases run in **autocommit** mode by default — every statement is its own transaction, committed immediately:
```sql
UPDATE employees SET salary = 80000 WHERE employee_id = 1;
-- Committed immediately in autocommit mode — cannot be rolled back
```

To group statements, always use an explicit BEGIN/COMMIT block.

## Locking

### Row-Level Locking

`SELECT ... FOR UPDATE` locks selected rows, preventing other transactions from modifying them until the lock is released:
```sql
BEGIN;
SELECT balance FROM accounts WHERE account_id = 1 FOR UPDATE;
-- Other transactions trying to UPDATE account 1 will wait
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
COMMIT;
```

### Deadlocks

A deadlock occurs when two transactions each hold a lock the other needs:
- Transaction A locks row 1, waits for row 2
- Transaction B locks row 2, waits for row 1

The database detects this and automatically kills one transaction (which gets a rollback error). To avoid deadlocks:
- Always acquire locks in the same order across transactions
- Keep transactions short
- Use appropriate isolation levels

## Practical Guidelines

1. **Keep transactions short** — long transactions hold locks longer, causing contention.
2. **Never leave a transaction open** — always COMMIT or ROLLBACK even on error paths.
3. **Wrap destructive operations** — always use a transaction for DELETE or UPDATE affecting many rows.
4. **Test rollback paths** — verify that your application handles transaction failures gracefully.

```sql
-- Safe DELETE pattern
BEGIN;
SELECT COUNT(*) FROM old_records WHERE created_at < '2023-01-01';  -- preview
DELETE FROM old_records WHERE created_at < '2023-01-01';
-- Inspect the count returned, then decide:
COMMIT;   -- or ROLLBACK;
```
