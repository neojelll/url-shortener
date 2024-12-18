from .logger import configure_logger
from loguru import logger
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from .message_broker import BrokerProducer, BrokerConsumer
from .db import DataBase
from .cache import Cache
from urllib.parse import urlparse
from .schemas import ShortURLRequestForm, UserCreateForm
from fastapi.security import OAuth2PasswordRequestForm
from .auth import verify_password, create_access_token, create_refresh_token
import uuid


configure_logger()


def is_valid_url(url: str) -> bool:
    logger.debug(f'Start is_valid_url, params: {repr(url)}')
    parsed_url = urlparse(url)
    returned = bool(parsed_url.netloc)
    logger.debug(f'Completed is_valid_url, returned: {repr(returned)}')
    return returned


app = FastAPI(title='URL Shortener API')


@app.post('/auth/register')
async def registration(user: UserCreateForm):
    logger.debug(f'Start registration with params: {user}')
    async with DataBase() as db:
        await db.create_user(user)
        logger.debug('Registration was successful')
    return {'message': 'Registration was succsessful'}


@app.post('/auth/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.debug(f'Start login with params: {form_data}')
    async with DataBase() as db:
        user = await db.get_user(form_data.username)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect username')
        elif not await verify_password(form_data.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect password')
        access_token = await create_access_token(data={'sub': user.username})
        refresh_token = await create_refresh_token(data={'sub': user.username})
    return_value = {
        'message': 'loggin was successful',
        'access-token': access_token,
        'refresh-token': refresh_token,
    }
    logger.debug(f'Login was successful, return value: {return_value}')
    return return_value


@app.post('/auth/refresh')
async def refresh(refresh_token: str):
    logger.debug(f'Start refresh access token with params: {refresh_token}')
    async with Cache() as cache:
        username = await cache.check_refresh_token(refresh_token)
        if username is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Could not validate credentials')
    access_token = await create_access_token(data={'sub': username})
    return_value = {'access-token': access_token}
    logger.debug(f'Refresh was successful, return value: {return_value}')
    return return_value


@app.post('/v1/url/shorten')
async def send_data(data: ShortURLRequestForm) -> dict[str, str]:
    logger.debug(f'Start send_data... params: {repr(data)}')
    long_url = data.url

    if not is_valid_url(long_url):
        logger.error('Error send_data: Invalid Url')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid URL'
        )

    task_num = uuid.uuid5(uuid.NAMESPACE_DNS, urlparse(long_url).netloc)
    task = {'task': str(task_num)}

    data_dict: dict = data.model_dump()
    data_dict.update(task)
    logger.debug(f'data_dict: {data_dict}')

    async with BrokerProducer() as broker:
        await broker.send_data(data_dict)

    logger.debug(f'Completed send_data, returned: {repr(task)}')
    return task


@app.get('/v1/url/shorten')
async def get_short_url(task_num: str) -> dict[str, str]:
    logger.debug(f'Start get_short_url, params: {task_num}')
    async with BrokerConsumer() as broker:
        short_url = await broker.consume_data(task_num)
        if short_url is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='URL is not found'
            )
    return_value = {'short_url': f'{short_url}'}
    logger.debug(f'Completed get_short_url, returned: {repr(return_value)}')
    return return_value


@app.get('/{short_url}')
async def redirect_request(short_url: str) -> RedirectResponse:
    logger.debug(f'Start redirect_request, params: {repr(short_url)}')

    async with Cache() as cache:
        check = await cache.check(short_url)

        if check is not None:
            long_url = check
        else:
            async with DataBase() as database:
                long_url = await database.get_long_url(short_url)
                expiration = await database.get_expiration(short_url)

            if long_url is None or expiration is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail='URL is not valid'
                )

            await cache.set(short_url, long_url, expiration)

    logger.debug(f'Completed redirect_request, returned: Redirect to {repr(long_url)}')
    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
