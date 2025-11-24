import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from app.core.config import settings
from sqlalchemy.engine import make_url

async def create_admin_database():
    print("Checking DB_URLS configuration...")
    
    # Get admin database URL
    admin_url = settings.DB_URLS.get('admin')
    if not admin_url:
        print("Error: No admin database URL configured in settings.DB_URLS")
        print("Available URLs:", list(settings.DB_URLS.keys()))
        return False
    
    print(f"Found admin URL configuration: {str(admin_url).split('@')[0]}@****")

    url = make_url(str(admin_url))
    
    # Convert SQLAlchemy URL to asyncpg format
    # Replace postgresql+asyncpg:// with postgresql://
    dsn = str(url).replace('postgresql+asyncpg://', 'postgresql://')
    
    # Create connection parameters for system database
    params = dict(
        user=url.username,
        password=url.password,
        host=url.host,
        port=url.port or 5432,
        database='postgres'  # Connect to default system database
    )
    
    try:
        # Connect to postgres database
        conn = await asyncpg.connect(**params)
        
        # Check if database exists
        result = await conn.fetch(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            url.database
        )
        
        if not result:
            # Create database if it doesn't exist
            await conn.execute(f'CREATE DATABASE "{url.database}"')
            print(f"Created database {url.database}")
        else:
            print(f"Database {url.database} already exists")
            
        await conn.close()
        return True
        
    except Exception as e:
        print(f"Error creating admin database: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(create_admin_database())