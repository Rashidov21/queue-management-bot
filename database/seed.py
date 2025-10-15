"""
Database seeding script to populate initial data
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import async_session_maker
from database.models import Service


async def seed_services():
    """Seed initial services"""
    async with async_session_maker() as session:
        # Check if services already exist
        from sqlalchemy import select
        result = await session.execute(select(Service))
        existing_services = result.scalars().all()
        
        if existing_services:
            print("✅ Services already exist, skipping seed")
            return
        
        # Create initial services
        services = [
            Service(name="Haircut & Styling", description="Professional haircut and styling services"),
            Service(name="Massage Therapy", description="Relaxing and therapeutic massage sessions"),
            Service(name="Consultation", description="Professional consultation and advice"),
            Service(name="Repair Service", description="Technical repair and maintenance"),
            Service(name="Beauty Treatment", description="Facial and beauty treatments"),
            Service(name="Fitness Training", description="Personal training and fitness sessions"),
            Service(name="Tutoring", description="Educational tutoring and lessons"),
            Service(name="Photography", description="Professional photography services"),
        ]
        
        for service in services:
            session.add(service)
        
        await session.commit()
        print(f"✅ Seeded {len(services)} services")


async def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    await seed_services()
    print("✅ Database seeding completed!")


if __name__ == "__main__":
    asyncio.run(main())
