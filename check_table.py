import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

URL = "postgresql+asyncpg://postgres:nopass@localhost:5432/admin"

async def main():
    engine = create_async_engine(URL)
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT to_regclass('public.crm_payments')"))
        table_exists = result.scalar()
        print(f"Table 'crm_payments' exists: {table_exists is not None}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
