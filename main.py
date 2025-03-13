from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database.db import init_db
from client_interaction.browse_and_order import router as browse_and_order_router
from client_interaction.cart_system import router as cart_system_router
from client_interaction.client_data import router as client_data_router
from client_interaction.location_handler import router as location_handler_router
from manager_interaction.manage_menu import router as manage_menu_router
import asyncio

# Initialize the database
init_db()

# Initialize the bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Include routers
dp.include_router(client_data_router)
dp.include_router(browse_and_order_router)
dp.include_router(cart_system_router)
dp.include_router(location_handler_router)
dp.include_router(manage_menu_router)

# Start the bot
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())