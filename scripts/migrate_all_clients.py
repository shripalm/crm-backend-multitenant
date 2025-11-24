#!/usr/bin/env python3
"""
Script to run alembic migrations for all client databases.
Creates databases if they don't exist, then runs migrations.
"""

import asyncio
import os
import sys
from urllib.parse import urlparse, urlunparse
import subprocess
from typing import Dict

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = sys.path[0]

from app.core.config import settings


async def verify_database_tables(db_url: str) -> None:
    """
    Verify that tables exist in the database after migration.
    """
    try:
        engine = create_async_engine(db_url)
        async with engine.connect() as conn:
            # Query for existing tables
            result = await conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public';
            """))
            tables = [row[0] for row in result]
            print(f"Found tables in database: {tables}")
    except Exception as e:
        print(f"Error verifying database tables: {str(e)}")
    finally:
        await engine.dispose()

async def create_database_if_not_exists(db_name: str, base_url: str) -> bool:
    """
    Create a database if it doesn't exist.
    
    Args:
        db_name: Name of the database to create
        base_url: Base database URL (without database name)
        
    Returns:
        True if database was created or already exists, False on error
    """
    try:
        # Parse the URL to get connection details
        parsed_url = urlparse(base_url)
        
        # Connect to postgres database to create new database
        conn = await asyncpg.connect(
            host=parsed_url.hostname,
            port=parsed_url.port or 5432,
            user=parsed_url.username,
            password=parsed_url.password,
            database="postgres"  # Connect to default postgres database
        )
        
        # Check if database exists
        result = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        
        if not result:
            # Database doesn't exist, create it
            print(f"Creating database: {db_name}")
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Database {db_name} created successfully")
        else:
            print(f"✅ Database {db_name} already exists")
            
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database {db_name}: {str(e)}")
        return False


def run_alembic_upgrade(database_url: str, config_file: str = 'alembic.ini') -> bool:
    """
    Run alembic upgrade head for a specific database.
    
    Args:
        database_url: Full database URL to run migrations on
        config_file: The alembic config file to use (default: alembic.ini)
        
    Returns:
        True if successful, False on error
    """
    try:
        # Set environment variable for this specific database
        env = os.environ.copy()
        env['DATABASE_URL'] = database_url
        print(database_url)
        env['PYTHONPATH'] = os.getcwd()
        
        print(f"Running alembic upgrade for: {database_url}")
        
        # Run alembic upgrade command using the current Python interpreter
        # and ensure the working directory is the project root so alembic.ini
        # (or the provided config_file) can be located.
        result = subprocess.run(
            [sys.executable, '-m', 'alembic', '-c', config_file, 'upgrade', 'head'],
            env=env,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        if result.returncode == 0:
            print(f"✅ Alembic upgrade completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ Alembic upgrade failed")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running alembic upgrade: {str(e)}")
        return False


def build_database_url(client: str, db_name: str, base_url: str) -> str:
    """
    Build a database URL for a specific client database.
    
    Args:
        client: Client name
        db_name: Database name
        base_url: Base database URL
        
    Returns:
        Full database URL for the client
    """
    parsed_url = urlparse(base_url)
    
    # Replace the database name in the path
    new_path = f"/{db_name}"
    
    # Rebuild the URL with the new database name
    new_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        new_path,
        parsed_url.params,
        parsed_url.query,
        parsed_url.fragment
    ))
    
    return new_url


def get_base_url(database_url: str) -> str:
    """
    Get base URL without the database name for creating databases.
    
    Args:
        database_url: Full database URL
        
    Returns:
        Base URL without database name
    """
    parsed_url = urlparse(database_url)
    # Remove the database name from path
    base_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        "",
        parsed_url.params,
        parsed_url.query,
        parsed_url.fragment
    ))
    return base_url


async def main():
    """
    Main function to migrate all client databases.
    """
    print("🚀 Starting migration for all client databases...")
    # Use explicit DB URLs from settings.DB_URLS
    db_urls = getattr(settings, "DB_URLS", None) or {}
    print(f"Found {len(db_urls)} clients: {list(db_urls.keys())}")
    
    success_count = 0
    total_clients = len(db_urls)
    
    for client, client_url in db_urls.items():
        if client == 'default':
            print(f"⏭️  Skipping {client} database {client_url}")
            total_clients -= 1
            continue
            
        # Special handling for admin database
        if client == 'admin':
            print(f"\n🔄 Processing admin database...")
            try:
                from sqlalchemy.engine import make_url
                parsed = make_url(str(client_url))
                db_name = parsed.database
                base_url = get_base_url(str(client_url))
                
                # Create admin database if it doesn't exist
                if await create_database_if_not_exists(db_name, base_url):
                    # Use admin alembic.ini for admin database
                    env = os.environ.copy()
                    env['DATABASE_URL'] = str(client_url)
                    env['PYTHONPATH'] = os.getcwd()
                    print(f"Running admin migration with DATABASE_URL={str(client_url)}")
                    result = subprocess.run(
                        [sys.executable, '-m', 'alembic', '-c', 'admin_alembic.ini', '--raiseerr', 'upgrade', 'head'],
                        env=env,
                        capture_output=True,
                        text=True,
                        cwd=PROJECT_ROOT
                    )
                    
                    # Always print stdout and stderr for debugging
                    if result.stdout:
                        print("Admin Migration stdout:", result.stdout)
                    if result.stderr:
                        print("Admin Migration stderr:", result.stderr)
                    
                    if result.returncode == 0:
                        print(f"✅ Admin database migration completed successfully")
                        success_count += 1
                        # Verify tables after successful migration
                        await verify_database_tables(str(client_url))
                    else:
                        print(f"❌ Admin database migration failed")
                        print(f"Error: {result.stderr}")
            except Exception as e:
                print(f"❌ Error processing admin database: {str(e)}")
            continue
        try:
            from sqlalchemy.engine import make_url
            parsed = make_url(str(client_url))
            db_name = parsed.database
            base_url = get_base_url(str(client_url))
        except Exception as e:
            print(f"❌ Skipping client {client}, invalid DB_URLS entry: {e}")
            continue

        print(f"\n🔄 Processing client: {client} -> database: {db_name}")
        
        # Create database if it doesn't exist
        if await create_database_if_not_exists(db_name, base_url):
            # Use the full DB URL directly
            client_db_url = str(client_url)
            
            # Run alembic upgrade
            env = os.environ.copy()
            env['DATABASE_URL'] = client_db_url
            env['PYTHONPATH'] = os.getcwd()
            
            print(f"Running client migration with DATABASE_URL={client_db_url}")
            result = subprocess.run(
                [sys.executable, '-m', 'alembic', '--raiseerr', 'upgrade', 'head'],
                env=env,
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )
            
            # Always print stdout and stderr for debugging
            if result.stdout:
                print("Migration stdout:", result.stdout)
            if result.stderr:
                print("Migration stderr:", result.stderr)
            
            if result.returncode == 0:
                success_count += 1
                print(f"✅ Client {client} migration completed successfully")
                if result.stdout:
                    print(f"Output: {result.stdout}")
                # Verify tables after successful migration
                await verify_database_tables(client_db_url)
            else:
                print(f"❌ Client {client} migration failed")
                print(f"Error: {result.stderr}")
        else:
            print(f"❌ Failed to create/access database for client {client}")
    
    # Summary
    print(f"\n📊 Migration Summary:")
    print(f"Total clients (including admin): {total_clients}")
    print(f"Successful migrations: {success_count}")
    print(f"Failed migrations: {total_clients - success_count}")
    
    if success_count == total_clients:
        print("🎉 All databases migrated successfully!")
        sys.exit(0)
    else:
        print("⚠️ Some migrations failed. Please check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
