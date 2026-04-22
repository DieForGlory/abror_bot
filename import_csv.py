import csv
import asyncio
from app.database.engine import async_session
from app.database.models import ResidentialComplex


async def import_data(file_path: str):
    async with async_session() as session:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Очистка и преобразование высоты потолков (например, "3 м" -> 3.0)
                ceiling_raw = row.get('Высота потолков', '').replace(' м', '').replace(',', '.').strip()
                ceiling_height = float(ceiling_raw) if ceiling_raw else None

                # Преобразование цены
                price_raw = row.get('Средняя цена', '').strip()
                price = int(float(price_raw)) if price_raw else None

                # Преобразование площади
                area_raw = row.get('Средняя площадь', '').replace(',', '.').strip()
                avg_area = float(area_raw) if area_raw else None

                # Создание объекта
                complex_obj = ResidentialComplex(
                    name=row.get('Название ЖК', ''),
                    district=row.get('Район', ''),
                    estate_class=row.get('Класс ЖК', ''),
                    finish_type=row.get('Вид отделки', ''),
                    price=price,
                    avg_area=avg_area,
                    ceiling_height=ceiling_height,
                    developer=row.get('Застройщик', ''),
                    floors=row.get('Этажность', ''),
                    amenities=row.get('Описание', ''),  # Описание загружается в amenities
                    deadline=row.get('Дата сдачи', ''),
                    current_stage='',
                    location_link=None
                )
                session.add(complex_obj)

        await session.commit()


if __name__ == '__main__':
    # Указать точное имя файла
    csv_file_path = 'domtut_analytics_base_uzs (2).xlsx'
    asyncio.run(import_data(csv_file_path))