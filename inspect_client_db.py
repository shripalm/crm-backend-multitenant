import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

# Attempt to get a client DB URL. 
# Usually DB_URLS has a 'default' or specific client keys.
# I'll iterate or guess.
async def main():
    print("Checking available keys in DB_URLS:", settings.DB_URLS.keys())
    
    # Try 'default' or the first non-admin key
    client_key = next((k for k in settings.DB_URLS.keys() if k != 'admin'), None)
    if not client_key:
        print("No client DB found in DB_URLS")
        return

    url = str(settings.DB_URLS[client_key])
    # Replace host for local access if needed (assuming docker logic)
    if "@db:" in url:
        url = url.replace("@db:", "@localhost:")
    
    print(f"Inspecting Client DB ({client_key})...")
    
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        print("COLUMNS for crm_payments:")
        result = await conn.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'crm_payments'"
        ))
        columns = [row[0] for row in result.fetchall()]
        print(columns)
        
        if not columns:
            print("Table crm_payments DOES NOT EXIST in this DB")
        elif 'user_id' in columns:
            print("user_id EXISTS")
        else:
            print("user_id MISSING")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
