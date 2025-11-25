# Database Migration Scripts

This directory contains scripts to run alembic migrations for all client databases.

## Scripts

### 1. `migrate_all_clients.sh` (Recommended)

A bash script that creates databases if they don't exist and runs alembic migrations for each client.

**Usage:**
```bash
# From the project root
./scripts/migrate_all_clients.sh
```

**Features:**
- ✅ Creates databases if they don't exist
- ✅ Runs `alembic upgrade head` for each client database
- ✅ Colored output for better readability
- ✅ Error handling and summary reporting
- ✅ Uses existing environment variables from `.env`

**Requirements:**
- `psql` command-line tool (for creating databases)
- `.env` file with `DATABASE_URL` configured
- All Python dependencies installed (`pip install -r requirements.txt`)

### 2. `migrate_all_clients.py`

A Python script that does the same as the bash script but with more advanced error handling.

**Usage:**
```bash
# From the project root
python scripts/migrate_all_clients.py
```

**Features:**
- ✅ Creates databases if they don't exist using asyncpg
- ✅ Runs `alembic upgrade head` for each client database
- ✅ Detailed error reporting
- ✅ Summary statistics

## Client Database Mapping

The scripts read the client-to-database mapping from `app/core/config.py`:

```python
CLIENT_DB_MAP: dict[str, str] = {
    "godrej": "app_db",
    "meesho": "meesho_db",
}
```

## Adding New Clients

To add a new client:

1. Update the `CLIENT_DB_MAP` in `app/core/config.py`
2. For the bash script, also update the `CLIENT_DB_MAP` array in `migrate_all_clients.sh`
3. Run the migration script

## Troubleshooting

### Database Connection Issues
- Ensure your `.env` file has the correct `DATABASE_URL`
- Verify database server is running
- Check firewall settings if connecting to remote database

### Permission Issues
- Ensure the database user has permission to create databases
- For PostgreSQL, the user needs `CREATEDB` privilege

### Migration Failures
- Check alembic revision files in `alembic/versions/`
- Verify model imports in `app/db/base.py`
- Run migrations individually to isolate issues:
  ```bash
  DATABASE_URL=postgresql+asyncpg://user:pass@host:port/specific_db python -m alembic upgrade head
  ```

## Manual Database Creation

If you need to create a database manually:

```bash
# Using psql
psql -h <host> -p <port> -U <user> -d postgres -c "CREATE DATABASE \"database_name\""

# Or using Python
python -c "
import asyncio
import asyncpg

async def create_db():
    conn = await asyncpg.connect('postgresql://user:pass@host:port/postgres')
    await conn.execute('CREATE DATABASE \"database_name\"')
    await conn.close()

asyncio.run(create_db())
"
```
