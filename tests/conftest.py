import asyncio

import pytest
from gino import create_engine

from gino_factory import GinoFactory
from .models import db, PG_URL, Team, User


@pytest.fixture(scope="session")
async def engine():
    db_engine = await create_engine(PG_URL)
    db.bind = db_engine
    async with db_engine.acquire():
        await db.status(db.text("DROP TABLE IF EXISTS users;"))
        await db.status(db.text("DROP TABLE IF EXISTS teams;"))
        await db.status(db.text("DROP TYPE IF EXISTS usertype;"))
        await db.status(db.text("CREATE TYPE  usertype AS ENUM ('USER', 'ADMIN');"))
        await db.gino.create_all()

        yield db_engine

        await db.status(db.text("DROP TYPE usertype CASCADE"))
        await db.status(db.text("DROP TABLE users"))
        await db.status(db.text("DROP TABLE teams"))

    await db_engine.close()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture(scope='function', autouse=True)
async def clear_db(engine):
    yield
    await db.status(db.text("TRUNCATE users RESTART IDENTITY CASCADE"))
    await db.status(db.text("TRUNCATE users RESTART IDENTITY CASCADE"))


@pytest.fixture
def factory():
    class Factory(GinoFactory):
        pass
    Factory.register(Team)
    Factory.register(User)
    return Factory
