import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Connect as postgres user to avoid auth issues, targeting admin DB
URL = "postgresql+asyncpg://postgres:nopass@localhost:5432/admin"

async def main():
    engine = create_async_engine(URL)
    async with engine.begin() as conn:
        print("Inspecting columns for crm_payments...")
        result = await conn.execute(text(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'crm_payments'"
        ))
        columns = result.fetchall()
        for col in columns:
            print(f" - {col[0]} ({col[1]})")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
