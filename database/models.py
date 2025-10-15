from sqlalchemy import Column, Integer, String, DateTime, Boolean, Time, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # "provider" or "client"
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    provider_profile = relationship("Provider", back_populates="user", uselist=False)
    bookings = relationship("Booking", back_populates="client")


class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    providers = relationship("Provider", back_populates="service")


class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    location = Column(String(255), nullable=True)
    working_days = Column(JSON, nullable=True)  # List of days [0,1,2,3,4,5,6]
    working_hours_start = Column(Time, nullable=True)
    working_hours_end = Column(Time, nullable=True)
    slot_duration = Column(Integer, default=30)  # Duration in minutes
    is_accepting = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="provider_profile")
    service = relationship("Service", back_populates="providers")
    slots = relationship("Slot", back_populates="provider")


class Slot(Base):
    __tablename__ = "slots"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD format
    time = Column(String(5), nullable=False)  # HH:MM format
    status = Column(String(20), default="available")  # "available", "booked", "unavailable"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    provider = relationship("Provider", back_populates="slots")
    booking = relationship("Booking", back_populates="slot", uselist=False)


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("slots.id"), nullable=False)
    status = Column(String(20), default="active")  # "active", "cancelled", "completed"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    client = relationship("User", back_populates="bookings")
    slot = relationship("Slot", back_populates="booking")
