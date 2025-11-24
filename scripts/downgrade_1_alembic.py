#!/usr/bin/env python3
"""
Script to downgrade one alembic migration for all client databases,
and print the latest alembic version after downgrade.
"""

import asyncio
import os
import sys
from urllib.parse import urlparse, urlunparse
from sqlalchemy.engine import make_url
import subprocess

import asyncpg

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


async def create_database_if_not_exists(db_name: str, base_url: str) -> bool:
    try:
        parsed_url = urlparse(base_url)
        conn = await asyncpg.connect(
            host=parsed_url.hostname,
            port=parsed_url.port or 5432,
            user=parsed_url.username,
            password=parsed_url.password,
            database="postgres"
        )
        result = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        if not result:
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


def run_alembic_downgrade_one(database_url: str) -> bool:
    """
    Run alembic downgrade -1 for a specific database.
    """
    try:
        env = os.environ.copy()
        env['DATABASE_URL'] = database_url
        env['PYTHONPATH'] = os.getcwd()
        print(f"Running alembic downgrade -1 for: {database_url}")
        result = subprocess.run(
            ['python', '-m', 'alembic', 'downgrade', '-1'],
            env=env,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            print(f"✅ Alembic downgrade completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ Alembic downgrade failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running alembic downgrade: {str(e)}")
        return False


async def get_current_alembic_version(database_url: str) -> str:
    """
    Get the current alembic version from the alembic_version table.
    """
    parsed_url = urlparse(database_url)
    try:
        conn = await asyncpg.connect(
            host=parsed_url.hostname,
            port=parsed_url.port or 5432,
            user=parsed_url.username,
            password=parsed_url.password,
            database=parsed_url.path.lstrip("/")
        )
        version = await conn.fetchval("SELECT version_num FROM alembic_version")
        await conn.close()
        return version
    except Exception as e:
        print(f"❌ Error fetching alembic version: {str(e)}")
        return None


def build_database_url(client: str, db_name: str, base_url: str) -> str:
    parsed_url = urlparse(base_url)
    new_path = f"/{db_name}"
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
    parsed_url = urlparse(database_url)
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
    print("🚀 Starting downgrade for all client databases...")
    # Use explicit DB URLs from settings.DB_URLS
    db_urls = getattr(settings, "DB_URLS", None) or {}
    print(f"Found {len(db_urls)} clients: {list(db_urls.keys())}")
    success_count = 0
    total_clients = len(db_urls)
    client_versions = {}

    for client, client_url in db_urls.items():
        if client in ['admin', 'default']:
            print(f"⏭️  Skipping {client} database {client_url}")
            continue
        try:
            parsed = make_url(str(client_url))
            db_name = parsed.database
            base_url = get_base_url(str(client_url))
        except Exception as e:
            print(f"❌ Skipping client {client}, invalid DB_URLS entry: {e}")
            client_versions[client] = None
            continue

        print(f"\n🔄 Processing client: {client} -> database: {db_name}")
        if await create_database_if_not_exists(db_name, base_url):
            client_db_url = str(client_url)
            if run_alembic_downgrade_one(client_db_url):
                version = await get_current_alembic_version(client_db_url)
                client_versions[client] = version
                print(f"✅ Client {client} downgrade completed successfully. Latest version: {version}")
                success_count += 1
            else:
                print(f"❌ Client {client} downgrade failed")
                client_versions[client] = None
        else:
            print(f"❌ Failed to create/access database for client {client}")
            client_versions[client] = None

    print(f"\n📊 Downgrade Summary:")
    print(f"Total clients: {total_clients}")
    print(f"Successful downgrades: {success_count}")
    print(f"Failed downgrades: {total_clients - success_count}")
    print("\n🔖 Latest Alembic versions after downgrade:")
    for client, version in client_versions.items():
        print(f"  {client}: {version if version else 'Unknown/Error'}")

    if success_count == total_clients:
        print("🎉 All client databases downgraded successfully!")
        sys.exit(0)
    else:
        print("⚠️ Some downgrades failed. Please check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
