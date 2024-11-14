import os
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F, html
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from dotenv import load_dotenv
from loguru import logger
from .logger import configure_logger
from .validate import is_valid_message


configure_logger()

load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ['TELEGRAM_BOT_API_KEY'])

dp = Dispatcher()


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Помощь'))

    await message.answer(
        f"Привет, {html.bold(html.quote(message.from_user.full_name))}!\n\nЧтобы узнать как сократить свою ссылку нажми на кнопку 'Помощь' внизу",  # type: ignore
        parse_mode=ParseMode.HTML,
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.message(F.text.lower() == 'помощь')
async def send_documentation(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='GitHub', url='https://github.com/neojelll/url-shortener'
        )
    )

    await message.reply(
        "Чтобы сократить ссылку достаточно просто напросто отправить ссылку сюда в чат, также есть необязательные параметры prefix, expiration\n\nprefix - prefix ссылки(короткий набор символов)(по умолчанию отсуствует)\n\nexpiration - время действия ссылки в часах(число)(по умолчанию 24 часа)\n\nЧтобы предать параметры достаточно просто отправить через пробел первый параметр а через еще один пробел второй(передавать параметры нужно строго в порядке url prefix expiration)(чтобы пропустить параметр prefix но указать expiration вместо prefix напишите '-' пропуск префикса)\n\nПримеры использования:\n\nБез параметров: http://example.com/url\n\nС префиксом но без времени действия: http://example.com/url prefix\n\nС временем действия но без префикса: http://example.com/url - 24\n\nС префиксом и временем действия: http://example.com prefix 24\n\nGithub репозиторий сервиса:",
        reply_markup=builder.as_markup(),
    )


@dp.message(F.text)
async def shorten(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='GitHub issues', url='https://github.com/neojelll/url-shortener/issues'
        )
    )

    try:
        logger.debug(f'start response with params: {message.text}')

        result = await is_valid_message(message.text)  # type: ignore

        if isinstance(result, str):
            await message.reply(result)
            return

        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://my_project-api-1:8000/v1/url/shorten',
                json=result,
            ) as response:
                if response.status == 400:
                    await message.reply('Вы ввели некоректный url, попробуйте еще раз')
                    return

                result_post = await response.json()
                task_num = result_post['task']

            async with session.get(
                f'http://my_project-api-1:8000/v1/url/shorten?task_num={task_num}'
            ) as response:
                result_get = await response.json()

            await message.reply(
                f'{os.environ['DOMAIN_NAME']}/{result_get["short_url"]}'
            )

            logger.debug('Completed response')
    except Exception as e:
        logger.error(f'Error when response: {e}')

        await message.reply(
            'Ошибка на стороне сервиса, можете перейти по кнопке ниже и написать о проблеме или попробовать позже',
            reply_markup=builder.as_markup(),
        )


async def main():
    await dp.start_polling(bot)
