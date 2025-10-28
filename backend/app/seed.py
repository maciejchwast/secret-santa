import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select

from .config import get_settings
from .db import async_session_factory
from .models import Base, Group, Member


async def seed() -> None:
    async with async_session_factory() as session:
        existing = await session.execute(select(Group).limit(1))
        if existing.scalar_one_or_none():
            print("Database already seeded")
            return

        group = Group(
            name="Demo Secret Santa",
            organizer_email="organizer@example.com",
            budget=50,
            reveal_date=datetime.utcnow() + timedelta(days=30),
            allow_household=False,
            join_pin="123456",
            join_token="demo-token",
        )
        members = [
            Member(name="Alice", email="alice@example.com", household="A"),
            Member(name="Bob", email="bob@example.com", household="B"),
            Member(name="Charlie", email="charlie@example.com", household="A"),
        ]
        for member in members:
            group.members.append(member)
        session.add(group)
        await session.commit()
        print("Seeded demo data")


if __name__ == "__main__":
    asyncio.run(seed())
