import pytest
from sqlalchemy import inspect
from app.database.base import init_db, engine

@pytest.mark.asyncio  # todo: create the db "wishlist_db" and user "wishlist_user"
async def test_db_tables_creation():
    await init_db()
    inspector = inspect(engine.sync_engine)
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "wishes" in tables
