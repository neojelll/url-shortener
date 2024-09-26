import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from api.db import DataBase, LongUrl, UrlMapping

SHORT_URL = "shortener.com"
LONG_URL = "http://shortener.com/long"
EXPIRATION = 300

@pytest_asyncio.fixture
async def mock_db(mocker):
    mocker.patch('api.db.create_async_engine', autospec=True)
    mock_sessionmaker = mocker.patch('api.db.async_sessionmaker', autospec=True)
    mock_session = AsyncMock()
    mock_sessionmaker.return_value = AsyncMock(return_value=mock_session)
    db = DataBase()
    async with db as db_instance:
        yield db_instance, mock_session

def setup_execute1_result(mock_session, return_value):
    execute_result = MagicMock()
    mock_session.execute.return_value = execute_result
    execute_result.scalars.return_value.first.return_value = return_value
    return execute_result

def setup_execute2_result(mock_session, return_value):
    execute_result = MagicMock()
    mock_session.execute.return_value = execute_result
    execute_result.scalars.return_value.first.return_value = return_value
    return execute_result

@pytest.mark.asyncio
async def test_init(mock_db):
    db, _ = mock_db
    assert isinstance(db, DataBase)

@pytest.mark.asyncio
async def test_aenter(mock_db):
    db, _ = mock_db
    assert isinstance(db, DataBase)

@pytest.mark.asyncio
@pytest.mark.parametrize("short_url, mock_return, expected", [
    (SHORT_URL, LongUrl(long_value=LONG_URL), LONG_URL),
    ("non_existent_short_url", None, None),
])
async def test_get_long_url(mock_db, short_url, mock_return, expected):
    db, mock_session = mock_db
    setup_execute1_result(mock_session, mock_return)
    result = await db.get_long_url(short_url)
    assert result == expected
    mock_session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_long_url_exception(mock_db):
    db, mock_session = mock_db
    mock_session.execute.side_effect = Exception("Database error")
    result = await db.get_long_url("short_url_with_exception")
    assert result is None
    mock_session.execute.assert_awaited_once()

@pytest.mark.asyncio
@pytest.mark.parametrize("short_url, mock_return, expected", [
    (SHORT_URL, UrlMapping(expiration=EXPIRATION), EXPIRATION),
    ("non_existent_short_url", None, None),
])
async def test_get_expiration(mock_db, short_url, mock_return, expected):
    db, mock_session = mock_db
    setup_execute2_result(mock_session, mock_return)
    result = await db.get_expiration(short_url)
    assert result == expected
    mock_session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_expiration_exception(mock_db):
    db, mock_session = mock_db
    mock_session.execute.side_effect = Exception("Database error")
    result = await db.get_long_url("short_url_with_exception")
    assert result is None
    mock_session.execute.assert_awaited_once()
