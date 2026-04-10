import asyncio
from sqlalchemy import select
from app.database.engine import async_session
from app.database.models import ResidentialComplex


async def main():
    async with async_session() as session:
        result = await session.execute(
            select(ResidentialComplex.id, ResidentialComplex.name, ResidentialComplex.price)
        )
        complexes = result.all()

        print("Список ЖК и их цены в БД:")
        print("-" * 50)
        for c_id, name, price in complexes:
            print(f"ID: {c_id:<3} | {name:<30} | Цена: {price}")
        print("-" * 50)


if __name__ == '__main__':
    asyncio.run(main())