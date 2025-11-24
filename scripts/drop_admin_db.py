#!/usr/bin/env python3
import asyncio
import os
import sys
from urllib.parse import urlparse
import asyncpg

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

async def drop_database(db_name: str, base_url: str) -> bool:
    """
    Drop a database if it exists.
    Args:
        db_name: Name of the database to drop
        base_url: Base database URL (without database name)
    Returns:
        True if database was dropped or did not exist, False on error
    """
    try:
        parsed_url = urlparse(base_url)
        conn = await asyncpg.connect(
            host=parsed_url.hostname,
            port=parsed_url.port or 5432,
            user=parsed_url.username,
            password=parsed_url.password,
            database="postgres"
        )
        # Terminate all connections to the database
        await conn.execute(f"""
            SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}' AND pid <> pg_backend_pid();
        """)
        # Drop the database
        await conn.execute(f'DROP DATABASE IF EXISTS "{db_name}" WITH (FORCE);')
        print(f"✅ Dropped database: {db_name}")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Error dropping database {db_name}: {str(e)}")
        return False


def get_base_url(database_url: str) -> str:
    parsed_url = urlparse(database_url)
    base_url = parsed_url._replace(path="").geturl()
    return base_url


async def main():
    print("🚨 Dropping all client databases...")
    # Use explicit DB URLs from settings.DB_URLS
    db_urls = getattr(settings, "DB_URLS", None) or {}

    print(f"Found {len(db_urls)} clients: {list(db_urls.keys())}")
    success_count = 0
    total_clients = len(db_urls)

    for client, client_url in db_urls.items():
        try:
            if client not in ['admin']:
                print(f"⏭️  Skipping {client} database {client_url}")
                continue
            from sqlalchemy.engine import make_url
            parsed = make_url(str(client_url))
            db_name = parsed.database
            base_url = get_base_url(str(client_url))
        except Exception as e:
            print(f"❌ Skipping client {client}, invalid DB_URLS entry: {e}")
            continue

        print(f"\n🔄 Dropping for client: {client} -> database: {db_name}")
        if await drop_database(db_name, base_url):
            success_count += 1
        else:
            print(f"❌ Failed to drop database for client {client}")
    print(f"\n📊 Drop Summary:")
    print(f"Total clients: {total_clients}")
    print(f"Successful drops: {success_count}")
    print(f"Failed drops: {total_clients - success_count}")
    if success_count == total_clients:
        print("🎉 All client databases dropped successfully!")
        sys.exit(0)
    else:
        print("⚠️ Some drops failed. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
