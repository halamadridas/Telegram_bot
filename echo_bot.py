import os
import json
import http.client
import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionSender
from aiogram.filters import Command

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Telegram bot
bot = Bot(token="your_bot_token")
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# RapidAPI setup
RAPIDAPI_HOST = "your_host"
RAPIDAPI_KEY = " your_key"  # Ensure this environment variable is set


@router.message(Command(commands=["start", "help"]))
async def welcome(message: Message):
    await message.answer("Hello! I am GPT Chat BOT. You can ask me anything :)")


@router.message()
async def gpt(message: Message):
    try:
        # Show typing action while processing
        async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
            # Prepare the request to RapidAPI
            conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
            payload = json.dumps({
                "messages": [
                    {"role": "user", "content": message.text}
                ],
                "model": "gpt-4o",  # Replace with the appropriate model
                "max_tokens": 1024,
                "temperature": 0.5
            })
            headers = {
                'x-rapidapi-key': RAPIDAPI_KEY,
                'x-rapidapi-host': RAPIDAPI_HOST,
                'Content-Type': "application/json"
            }
            conn.request("POST", "/v1/chat/completions", payload, headers)

            # Fetch and process the response
            res = conn.getresponse()
            data = res.read()
            response = json.loads(data.decode("utf-8"))
            print(response)

            # Safely extract the bot's response message
            bot_reply = (
                response.get('choices', [{}])[0]
                .get('message', {})
                .get('content', "Sorry, I couldn't generate a proper response.")
            )

            # Send the response to the user
            await message.answer(bot_reply, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        await message.answer(f"An error occurred: {e}")


async def main():
    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
