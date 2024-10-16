import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from url_shortener_service.db import DataBase


SHORT_URL = "shortener.com"
LONG_URL = "http://urlshortener.com"
EXPIRATION = 5


@pytest_asyncio.fixture
async def mock_db(mocker):
    mocker.patch("url_shortener_service.db.create_async_engine", autospec=True)
    mock_sessionmaker = mocker.patch(
        "url_shortener_service.db.async_sessionmaker", autospec=True
    )
    mock_session = AsyncMock()
    mock_sessionmaker.return_value = MagicMock(return_value=mock_session)
    db = DataBase()
    async with db as db_instance:
        yield db_instance, mock_session


@pytest.mark.asyncio
async def test_init(mock_db):
    db, _ = mock_db
    isinstance(db, DataBase)


@pytest.mark.asyncio
async def test_aenter(mock_db):
    db, _ = mock_db
    isinstance(db, DataBase)


@pytest.mark.asyncio
async def test_create_recording(mock_db):
    db, mock_session = mock_db
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    await db.create_recording(LONG_URL, SHORT_URL, EXPIRATION)
    assert mock_session.add.call_count == 3
    mock_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_create_recording_error(mock_db):
    db, mock_session = mock_db
    mock_session.add = MagicMock(side_effect=Exception("DB error"))
    mock_session.commit = AsyncMock()
    await db.create_recording(LONG_URL, SHORT_URL, EXPIRATION)
