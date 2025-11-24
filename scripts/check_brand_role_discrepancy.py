"""
Script to check discrepancies in brands for each database/client.
"""

import os
import sys
import asyncio
from app.core.statics import statics
from app.core.config import settings
import asyncpg
import json



async def fetch_features_from_table(conn, table, column):
    query = f"SELECT {column} FROM {table} WHERE {column} IS NOT NULL"
    rows = await conn.fetch(query)
    features = set()
    for row in rows:
        val = row[column]
        if isinstance(val, list):
            features.update(val)
        elif isinstance(val, str):
            try:
                arr = json.loads(val)
                if isinstance(arr, list):
                    features.update(arr)
            except Exception:
                pass  # Ignore if not a valid JSON array
    return features

async def check_feature_discrepancies_async(db_url):
    statics_features = set(statics["features"])
    # Convert asyncpg URL to psycopg2 for asyncpg
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(db_url)
    try:
        brands_features = await fetch_features_from_table(conn, "brand", "features")
        
        result = []
        # Only report invalid features
        invalid_in_brands = brands_features - statics_features

        if invalid_in_brands:
            result.append(f"❌ Invalid features in brands (not in statics): {invalid_in_brands}")
        else:
            result.append("✅ No feature discrepancies found. All subsets are valid.")

        return result
    finally:
        await conn.close()

from sqlalchemy.engine import make_url

async def main():
    # Use explicit DB URLs from settings.DB_URLS
    db_urls = getattr(settings, "DB_URLS", None) or {}
    print("\n🚀 Checking feature discrepancies for all client databases...")
    print(f"Found {len(db_urls)} clients: {list(db_urls.keys())}")

    for client, client_url in db_urls.items():
        try:
            parsed = make_url(str(client_url))
            db_name = parsed.database
            client_db_url = str(client_url)
        except Exception as e:
            print(f"❌ Skipping client {client}, invalid DB_URLS entry: {e}")
            continue

        print(f"\n🔄 Processing client: {client} -> database: {db_name}")
        try:
            results = await check_feature_discrepancies_async(client_db_url)
            print(f"Results for client '{client}':")
            for line in results:
                print(line)
        except Exception as e:
            print(f"❌ Error checking client '{client}': {e}")

if __name__ == "__main__":
    asyncio.run(main())
