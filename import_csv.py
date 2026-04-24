import asyncio
from sqlalchemy import update
from app.database.engine import async_session
from app.database.models import ResidentialComplex


async def fix_estate_classes():
    class_mapping = {
        'Comfort': 'Комфорт',
        'Business': 'Бизнес',
        'Premium': 'Премиум'
    }

    async with async_session() as session:
        for eng, rus in class_mapping.items():
            stmt = (
                update(ResidentialComplex)
                .where(ResidentialComplex.estate_class == eng)
                .values(estate_class=rus)
            )
            result = await session.execute(stmt)
            print(f"Обновлено {eng} -> {rus}: {result.rowcount} записей")

        await session.commit()


if __name__ == '__main__':
    asyncio.run(fix_estate_classes())