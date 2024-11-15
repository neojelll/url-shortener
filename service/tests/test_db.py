import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from service.db import DataBase


SHORT_URL = 'shortener.com'
LONG_URL = 'http://urlshortener.com'
EXPIRATION = 5


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
        mocker.patch('service.db.create_async_engine', autospec=True)
        mock_sessionmaker = mocker.patch('service.db.async_sessionmaker', autospec=True)
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
    mock_session.add = MagicMock(side_effect=Exception('DB error'))
    mock_session.commit = AsyncMock()
    await db.create_recording(LONG_URL, SHORT_URL, EXPIRATION)


@pytest.mark.asyncio
@pytest.mark.parametrize('expected, short_url', [(None, None), (SHORT_URL, SHORT_URL)])
async def test_check_short_url(mock_db, expected, short_url):
    db, mock_session = mock_db
    execute_result = MagicMock()
    mock_session.execute.return_value = execute_result
    execute_result.scalars.return_value.first.return_value = short_url
    result = await db.check_short_url(SHORT_URL)
    assert result == expected
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_short_url_error(mock_db):
    db, mock_session = mock_db
    mock_session.execute.side_effect = Exception('DB error')
    result = await db.check_short_url(SHORT_URL)
    assert result is None
    mock_session.execute.assert_awaited_once()
