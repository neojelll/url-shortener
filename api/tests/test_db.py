import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from api.db import DataBase, LongUrl, UrlMapping
from datetime import datetime

SHORT_URL = 'shortener.com'
LONG_URL = 'http://shortener.com/long'
DATETIME1 = datetime(2024, 9, 27, 15, 12, 17)
DATETIME2 = datetime(2024, 9, 27, 16, 12, 17)
EXPIRATION = 300
TASK_NUM = 'disdsdpal129391203912'


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
        mock_session = AsyncMock()
        mocker.patch('api.db.create_async_engine', autospec=True)
        mocker.patch(
            'api.db.async_sessionmaker',
            autospec=True,
            return_value=MagicMock(return_value=mock_session),
        )
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
@pytest.mark.parametrize(
    'short_url, mock_return, expected',
    [
        (SHORT_URL, LongUrl(long_value=LONG_URL), LONG_URL),
        ('non_existent_short_url', None, None),
    ],
)
async def test_get_long_url(mock_db, short_url, mock_return, expected):
    db, mock_session = mock_db
    setup_execute1_result(mock_session, mock_return)
    result = await db.get_long_url(short_url)
    assert result == expected
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_long_url_exception(mock_db):
    db, mock_session = mock_db
    mock_session.execute.side_effect = Exception('Database error')
    result = await db.get_long_url('short_url_with_exception')
    assert result is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_expiration_hit(mocker, mock_db):
    db, mock_session = mock_db
    setup_execute2_result(
        mock_session, UrlMapping(expiration=EXPIRATION, date=DATETIME1)
    )
    dt = mocker.patch('api.db.datetime', autospec=True)
    dt.now.return_value = DATETIME2
    result = await db.get_expiration(SHORT_URL)
    assert result == (EXPIRATION + DATETIME1.time().hour) - DATETIME2.time().hour
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_expiration_miss(mock_db):
    db, mock_session = mock_db
    setup_execute2_result(mock_session, None)
    result = await db.get_expiration('non_existent_short_url')
    assert result is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_expiration_exception(mock_db):
    db, mock_session = mock_db
    mock_session.execute.side_effect = Exception('Database error')
    result = await db.get_expiration('short_url_with_exception')
    assert result is None
    mock_session.execute.assert_awaited_once()
