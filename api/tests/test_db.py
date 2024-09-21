from unittest.mock import AsyncMock
from api.db import DataBase, LongUrl
import pytest


SHORT_URL = "shortener.com"
LONG_URL = "http://shortener.com/long"


@pytest.mark.asyncio
async def test_init(mocker):
    mock_session = AsyncMock()

    mocker.patch("api.db.create_async_engine", autospec=True)
    mocker.patch("api.db.async_sessionmaker", autospec=True, return_value=mock_session)

    instance = DataBase()

    assert isinstance(instance, DataBase)


@pytest.mark.asyncio
async def test_aenter(mocker):
    mock_session = AsyncMock()
	
    mocker.patch("api.db.create_async_engine", autospec=True)
    mocker.patch("api.db.async_sessionmaker", autospec=True, return_value=mock_session)

    instance = DataBase()

    async with instance as entered_instance:
        assert instance is entered_instance


@pytest.mark.asyncio
async def test_get_long_url_hit(mocker):
    mock_session = AsyncMock()
	
    mocker.patch("api.db.create_async_engine", autospec=True)
    mocker.patch("api.db.async_sessionmaker", autospec=True, return_value=mock_session)

    instance = DataBase()
    
    instance.session = AsyncMock()

    long_url_mock = AsyncMock()
    long_url_mock.scalars.return_value.first.return_value = LongUrl(long_value=LONG_URL)

    instance.session.execute.return_value = long_url_mock

    result = await instance.get_long_url(SHORT_URL)

    assert result == LONG_URL
    instance.session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_long_url_miss(mocker):
    mock_session = AsyncMock()
	
    mocker.patch("api.db.create_async_engine", autospec=True)
    mocker.patch("api.db.async_sessionmaker", autospec=True, return_value=mock_session)

    instance = DataBase()

    instance.session = AsyncMock()

    long_url_mock = AsyncMock()
    long_url_mock.scalars.return_value.first.return_value = None
    instance.session.execute.return_value = long_url_mock
    
    result = await instance.get_long_url("short_value_non_existent")
    
    assert result is None
    instance.session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_long_url_exception(mocker):
    mock_session = AsyncMock()
	
    mocker.patch("api.db.create_async_engine", autospec=True)
    mocker.patch("api.db.async_sessionmaker", autospec=True, return_value=mock_session)

    instance = DataBase()

    instance.session = AsyncMock()
    
    instance.session.execute.side_effect = Exception("Database error")
    
    result = await instance.get_long_url("short_value_with_exception")
    
    assert result is None
    instance.session.execute.assert_awaited_once()
