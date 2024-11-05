import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F, html
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.enums import ParseMode
from .logger import configure_logger
from loguru import logger

configure_logger()

TOKEN = '7624468761:AAGuKY34mTFl1L5EEL0vF9DXs3iLkl6KLno'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)

dp = Dispatcher()


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
	builder = ReplyKeyboardBuilder()
	builder.add(types.KeyboardButton(text='Help'))
	await message.answer(
		f"Hello, {html.bold(html.quote(message.from_user.full_name))}!\nSend the link you need to shorten with a simple message", #type: ignore
		parse_mode=ParseMode.HTML,
		reply_markup=builder.as_markup(resize_keyboard=True)
		)
	

@dp.message(F.text.lower() == 'help')
async def send_documentation(message: types.Message):
	builder = InlineKeyboardBuilder()
	builder.row(types.InlineKeyboardButton(
        text="GitHub", url="https://github.com/neojelll/url-shortener")
    )
	await message.reply('-there will be documentation here-\nTo shorten the link, send the link via chat message', reply_markup=builder.as_markup())


@dp.message(F.text)
async def shorten(message: types.Message):
	try:
		logger.debug('start response...')
		async with aiohttp.ClientSession() as session:
			async with session.post('http://my_project-api-1:8000/v1/url/shorten', json={'url': message.text}) as response:
				result = await response.json()
				await message.reply(result['task'])
	except Exception as e:
		logger.error(f'Error when response: {e}')
		await message.reply('Server error')


async def main():
	await dp.start_polling(bot)
