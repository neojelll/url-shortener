from service.shortener_service import (
    generate_random_string,
    shortener,
    check_short_url,
)
from unittest.mock import AsyncMock
import pytest


@pytest.mark.asyncio
async def test_generate_random_string(mocker):
    result = await generate_random_string(7)
    assert len(result) == 7


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'expected, prefix, random_string_returned',
    [
        ('prefix/abc1', 'prefix', 'abc1'),
        ('abcd123', '', 'abcd123'),
    ],
)
async def test_shortener(mocker, expected, prefix, random_string_returned):
    mocker.patch(
        'service.shortener_service.generate_random_string',
        autospec=True,
        return_value=random_string_returned,
    )
    result = await shortener(prefix)
    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'expected, return_cache, return_db',
    [
        ('abc1', False, None),
        ('abc2', True, None),
        ('abc2', False, 'abc1'),
    ],
)
async def test_check_short_url(mocker, expected, return_cache, return_db):
    mocker.patch(
        'service.shortener_service.shortener',
        autospec=True,
        side_effect=['abc1', 'abc2'],
    )
    mock_cache = AsyncMock()
    mock_cache.check_short_url.return_value = return_cache
    mock_cache.__aenter__.return_value = mock_cache
    mocker.patch(
        'service.shortener_service.Cache',
        autospec=True,
        return_value=mock_cache,
    )

    mock_db = AsyncMock()
    mock_db.check_short_url.return_value = return_db
    mock_db.__aenter__.return_value = mock_db
    mocker.patch(
        'service.shortener_service.DataBase',
        autospec=True,
        return_value=mock_db,
    )

    result = await check_short_url()
    assert result == expected
