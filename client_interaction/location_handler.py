from aiogram import Router, types
from aiogram.filters import Command
from aiogram import F
from database.db import execute_query

router = Router()

@router.message(F.content_type == "location")
async def receive_location(message: types.Message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    telegram_id = message.from_user.id

    # Store the location in the database
    execute_query(
        "UPDATE clients SET location = ? WHERE telegram_id = ?",
        (f"{latitude},{longitude}", telegram_id)
    )

    await message.answer("Thank you! Your location has been saved.")