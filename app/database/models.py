from sqlalchemy import Integer, String, BigInteger, Text, DateTime, ForeignKey, func,Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    role: Mapped[str] = mapped_column(String(50), default='user')
    username: Mapped[str] = mapped_column(String(255), nullable=True)

class ComplexUpdateHistory(Base):
    __tablename__ = 'complex_update_history'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    complex_id: Mapped[int] = mapped_column(Integer, ForeignKey('residential_complexes.id'))
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[str] = mapped_column(Text, nullable=True)
    new_value: Mapped[str] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    complex = relationship("ResidentialComplex", back_populates="history_updates")

class ResidentialComplex(Base):
    __tablename__ = 'residential_complexes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    district: Mapped[str] = mapped_column(String(255), nullable=False)
    estate_class: Mapped[str] = mapped_column(String(100), nullable=False)
    finish_type: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer, nullable=True)
    avg_area: Mapped[float] = mapped_column(Float, nullable=True)
    ceiling_height: Mapped[float] = mapped_column(Float, nullable=True)
    developer: Mapped[str] = mapped_column(String(255), nullable=True)
    floors: Mapped[str] = mapped_column(String(100))
    amenities: Mapped[str] = mapped_column(Text)
    deadline: Mapped[str] = mapped_column(String(100))
    current_stage: Mapped[str] = mapped_column(Text)
    location_link: Mapped[str] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    photos = relationship("Photo", back_populates="complex", cascade="all, delete-orphan")
    floor_plans = relationship("FloorPlan", back_populates="complex", cascade="all, delete-orphan")
    history_updates = relationship("ComplexUpdateHistory", back_populates="complex", cascade="all, delete-orphan")

class Photo(Base):
    __tablename__ = 'photos'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    complex_id: Mapped[int] = mapped_column(Integer, ForeignKey('residential_complexes.id'))
    telegram_file_id: Mapped[str] = mapped_column(String(255), nullable=False)

    complex = relationship("ResidentialComplex", back_populates="photos")

class FloorPlan(Base):
    __tablename__ = 'floor_plans'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    complex_id: Mapped[int] = mapped_column(Integer, ForeignKey('residential_complexes.id'))
    telegram_file_id: Mapped[str] = mapped_column(String(255), nullable=False)

    complex = relationship("ResidentialComplex", back_populates="floor_plans")