import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

URL = "postgresql+asyncpg://postgres:nopass@localhost:5432/admin"

async def main():
    engine = create_async_engine(URL)
    async with engine.begin() as conn:
        print("COLUMNS for crm_payments:")
        result = await conn.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'crm_payments'"
        ))
        columns = [row[0] for row in result.fetchall()]
        print(columns)
        
        if 'user_id' in columns:
            print("user_id EXISTS")
        else:
            print("user_id MISSING")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
