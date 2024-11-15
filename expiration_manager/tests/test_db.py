import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from expiration_manager.db import DataBase


@pytest_asyncio.fixture
async def mock_db(mocker):
    with patch.dict(
        'os.environ',
        {
            'DB_HOST': 'postgres',
            'DB_NAME': 'mydatabase',
            'DB_USERNAME': 'neojelll',
            'DB_PASSWORD': '123',
            'DB_PORT': '5432',
        },
    ):
        mocker.patch('expiration_manager.db.create_async_engine', autospec=True)
        mock_sessionmaker = mocker.patch(
            'expiration_manager.db.async_sessionmaker', autospec=True
        )
        mock_session = AsyncMock()
        mock_sessionmaker.return_value = MagicMock(return_value=mock_session)
        db = DataBase()
        async with db as db_instance:
            yield db_instance, mock_session


@pytest.mark.asyncio
async def test_init(mock_db):
    db, _ = mock_db
    assert isinstance(db, DataBase)


@pytest.mark.asyncio
async def test_aenter(mock_db):
    db, _ = mock_db
    assert isinstance(db, DataBase)


# @pytest.mark.asyncio
# async def test_delete_after_time(mock_db):
#     db, mock_session = mock_db
#     mock_session.execute = AsyncMock(return_value=MagicMock())
#     mock_all = MagicMock(return_value=[1, 2, 3])
#     mock_session.execute.return_value.scalars.return_value.all = mock_all
#     result = await db.delete_after_time()
#     assert result == 3
#     mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_after_time_error(mock_db):
    db, mock_session = mock_db
    mock_session.execute = AsyncMock(side_effect=Exception('DB error'))
    mock_session.rollback = AsyncMock()
    result = await db.delete_after_time()
    assert result == 0
    mock_session.rollback.assert_awaited_once()
