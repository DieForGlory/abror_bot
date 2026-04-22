from sqlalchemy import select, update, delete
from app.database.engine import async_session
from app.database.models import ResidentialComplex, Photo, FloorPlan, User, ComplexUpdateHistory
from typing import Any
from sqlalchemy import func

async def get_complexes_by_filter(district: str, estate_class: str):
    async with async_session() as session:
        result = await session.execute(
            select(ResidentialComplex).where(
                ResidentialComplex.district == district,
                ResidentialComplex.estate_class == estate_class
            )
        )
        return result.scalars().all()


async def search_complexes_by_name(query: str):
    async with async_session() as session:
        result = await session.execute(
            select(ResidentialComplex).where(ResidentialComplex.name.icontains(query)).limit(20)
        )
        return result.scalars().all()


async def get_complex_by_id(complex_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(ResidentialComplex).where(ResidentialComplex.id == complex_id)
        )
        return result.scalar_one_or_none()


async def add_complex(data: dict) -> int:
    async with async_session() as session:
        new_complex = ResidentialComplex(**data)
        session.add(new_complex)
        await session.commit()
        await session.refresh(new_complex)
        return new_complex.id


async def add_photo(complex_id: int, file_id: str):
    async with async_session() as session:
        new_photo = Photo(complex_id=complex_id, telegram_file_id=file_id)
        session.add(new_photo)
        await session.commit()


async def add_floor_plan(complex_id: int, file_id: str):
    async with async_session() as session:
        new_plan = FloorPlan(complex_id=complex_id, telegram_file_id=file_id)
        session.add(new_plan)
        await session.commit()
async def delete_floor_plan(plan_id: int):
    async with async_session() as session:
        await session.execute(delete(FloorPlan).where(FloorPlan.id == plan_id))
        await session.commit()
async def get_photos(complex_id: int):
    async with async_session() as session:
        result = await session.execute(select(Photo).where(Photo.complex_id == complex_id))
        return result.scalars().all()

async def delete_photo(photo_id: int):
    async with async_session() as session:
        await session.execute(delete(Photo).where(Photo.id == photo_id))
        await session.commit()

async def update_complex_field(complex_id: int, field_name: str, new_value: Any):
    async with async_session() as session:
        result = await session.execute(select(ResidentialComplex).where(ResidentialComplex.id == complex_id))
        complex_obj = result.scalar_one_or_none()

        if not complex_obj:
            return

        old_value = str(getattr(complex_obj, field_name, ""))

        stmt = update(ResidentialComplex).where(ResidentialComplex.id == complex_id).values({field_name: new_value})
        await session.execute(stmt)

        history_record = ComplexUpdateHistory(
            complex_id=complex_id,
            field_name=field_name,
            old_value=old_value,
            new_value=str(new_value)
        )
        session.add(history_record)

        await session.commit()


async def register_user(tg_id: int, username: str = None):
    async with async_session() as session:
        user = await session.get(User, tg_id)
        if not user:
            session.add(User(telegram_id=tg_id, username=username))
            await session.commit()


async def get_all_user_ids():
    async with async_session() as session:
        result = await session.execute(select(User.telegram_id))
        return result.scalars().all()


async def delete_complex(complex_id: int):
    async with async_session() as session:
        stmt = delete(ResidentialComplex).where(ResidentialComplex.id == complex_id)
        await session.execute(stmt)
        await session.commit()


async def get_floor_plans(complex_id: int):
    async with async_session() as session:
        result = await session.execute(select(FloorPlan).where(FloorPlan.complex_id == complex_id))
        return result.scalars().all()

async def get_analytics_data():
    async with async_session() as session:
        district_query = await session.execute(
            select(
                ResidentialComplex.district,
                func.round(func.avg(ResidentialComplex.price), 2)
            )
            .where(ResidentialComplex.price.isnot(None))
            .group_by(ResidentialComplex.district)
        )
        districts = district_query.all()

        class_query = await session.execute(
            select(
                ResidentialComplex.estate_class,
                func.round(func.avg(ResidentialComplex.price), 2)
            )
            .where(ResidentialComplex.price.isnot(None))
            .group_by(ResidentialComplex.estate_class)
        )
        classes = class_query.all()

        dev_query = await session.execute(
            select(
                ResidentialComplex.developer,
                ResidentialComplex.district,
                ResidentialComplex.estate_class,
                func.round(func.avg(ResidentialComplex.price), 2)
            )
            .where(ResidentialComplex.developer.isnot(None))
            .where(ResidentialComplex.price.isnot(None))
            .group_by(
                ResidentialComplex.developer,
                ResidentialComplex.district,
                ResidentialComplex.estate_class
            )
        )
        developers = dev_query.all()

        return districts, classes, developers