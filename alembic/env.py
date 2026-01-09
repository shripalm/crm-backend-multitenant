import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncio
from logging.config import fileConfig

from sqlalchemy.engine import Connection
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

from app.db.base import Base
from app.core.config import settings


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
# Some environments (or when alembic is invoked differently) may not provide
# a config file name that maps to an INI with logger sections. Guard the
# call to fileConfig to avoid KeyError during import.
if getattr(config, "config_file_name", None):
    try:
        fileConfig(config.config_file_name)
    except Exception:
        # fallback: ignore logging configuration and continue
        pass

target_metadata = Base.metadata

def get_url():
    """Get database URL from environment variable or settings"""
    return os.getenv("DATABASE_URL") or str(settings.DB_URLS['default'])

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    # --- AUTO-RECOVERY LOGIC START ---
    # Detect if the database is on the deleted revision 'a1b2c3d4e5af'
    # and map it to the consolidated revision 'a1b2c3d4e5ae'.
    try:
        # Check current version directly using SQL
        result = connection.execute(text("select version_num from alembic_version"))
        current_ver = result.scalar()
        
        if current_ver == 'a1b2c3d4e5af':
            print("  [RECOVERY] Detected deleted revision 'a1b2c3d4e5af'.")
            print("  [RECOVERY] Automatically patching migration history to 'a1b2c3d4e5ae'...")
            
            # Update the version to the parent/consolidated revision
            connection.execute(text("update alembic_version set version_num = 'a1b2c3d4e5ae'"))
            connection.commit()
            print("  [RECOVERY] Success. Resuming standard migrations.")
            
    except ProgrammingError:
        # Table might not exist yet (init), ignore
        pass
    except Exception as e:
        print(f"  [RECOVERY WARNING] Could not check/patch migration version: {e}")
    # --- AUTO-RECOVERY LOGIC END ---

    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(get_url(), future=True)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

def run_migrations_online():
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
