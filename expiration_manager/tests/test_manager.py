from expiration_manager.manager import expiration_manager
from unittest.mock import AsyncMock
import pytest


@pytest.mark.asyncio
async def test_expiration_manager(mocker):
    mock_db_class = mocker.patch('expiration_manager.manager.DataBase', autospec=True)
    db_instance = mock_db_class.return_value
    db_instance.__aenter__.return_value = db_instance
    db_instance.delete_after_time = AsyncMock(return_value=5)
    result = await expiration_manager()
    assert result == 5
    db_instance.delete_after_time.assert_awaited_once()
