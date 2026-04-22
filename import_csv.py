import pandas as pd
import asyncio
from app.database.engine import async_session, engine
from app.database.models import ResidentialComplex


async def import_data(file_path: str):
    # Чтение Excel файла
    df = pd.read_excel(file_path)

    # Очистка заголовков
    df.columns = df.columns.str.strip()

    # Фильтрация пустых строк
    df = df.dropna(subset=['Название ЖК'])

    # Приведение типов и очистка данных
    def clean_float(value):
        if pd.isna(value): return None
        try:
            return float(str(value).replace(' м', '').replace(',', '.').strip())
        except:
            return None

    def clean_int(value):
        if pd.isna(value): return None
        try:
            return int(float(str(value).replace(' ', '').strip()))
        except:
            return None

    inserted = 0
    async with async_session() as session:
        for _, row in df.iterrows():
            complex_obj = ResidentialComplex(
                name=str(row.get('Название ЖК')).strip(),
                district=str(row.get('Район', '')).strip(),
                developer=str(row.get('Застройщик', '')).strip(),
                estate_class=str(row.get('Класс ЖК', '')).strip(),
                floors=str(row.get('Этажность', '')).strip(),
                ceiling_height=clean_float(row.get('Высота потолков')),
                finish_type=str(row.get('Вид отделки', '')).strip(),
                deadline=str(row.get('Дата сдачи', '')).strip(),
                avg_area=clean_float(row.get('Средняя площадь')),
                price=clean_int(row.get('Средняя цена')),
                amenities=str(row.get('Описание', '')).strip(),
                current_stage='Данные загружены из базы',
                location_link=None
            )
            session.add(complex_obj)
            inserted += 1

        await session.commit()

    await engine.dispose()
    print(f"Импорт завершен. Добавлено объектов: {inserted}")


if __name__ == '__main__':
    # Файл должен находиться в той же папке, что и скрипт
    file_name = 'domtut_analytics_base_uzs (2).xlsx'
    asyncio.run(import_data(file_name))