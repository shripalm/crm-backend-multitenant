#!/usr/bin/env python3
"""
Script to print the current alembic version for all client databases.
"""

import asyncio
import os
import sys
from urllib.parse import urlparse, urlunparse
from sqlalchemy.engine import make_url

import asyncpg

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

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

async def get_current_alembic_version(database_url: str) -> str:
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
        print(f"❌ Error fetching alembic version for {database_url}: {str(e)}")
        return None

async def main():
    print("🔍 Checking current alembic versions for all client databases...")
    # Require explicit DB URLs in settings.DB_URLS
    db_urls = getattr(settings, "DB_URLS", None) or {}
    client_versions = {}

    for client in db_urls.keys():
        try:
            client_url = str(db_urls[client])
            parsed = make_url(client_url)
            client_db_url = client_url
            version = await get_current_alembic_version(client_db_url)
            client_versions[client] = version
            print(f"{client}: {version if version else 'Unknown/Error'}")
        except Exception as e:
            print(f"\u274c Skipping client {client}, invalid DB_URLS entry: {e}")

if __name__ == "__main__":
    asyncio.run(main())
