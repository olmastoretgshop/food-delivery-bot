from aiogram import Router, types
from aiogram.filters import Command
from aiogram import F
from database.db import execute_query
from config import ADMIN_ID

router = Router()

@router.message(Command("start"))
async def collect_client_data(message: types.Message):
    # Check if the user is the admin
    if message.from_user.id == ADMIN_ID:
        # Provide admin options
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Client Interaction")],
                [types.KeyboardButton(text="Admin Interaction")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await message.answer("Welcome, Admin! Please choose an interaction mode:", reply_markup=keyboard)
        return

    # Extract client details from the message
    user = message.from_user
    telegram_id = user.id
    username = user.username
    name = user.full_name

    # Store client data in the database
    execute_query(
        "INSERT OR IGNORE INTO clients (telegram_id, username, name) VALUES (?, ?, ?)",
        (telegram_id, username, name)
    )

    # Ask for phone number
    await message.answer(
        "Please share your phone number using the 'Share Contact' button.",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="Share Contact", request_contact=True)]],
            one_time_keyboard=True
        )
    )

@router.message(F.text == "Client Interaction")
async def client_interaction(message: types.Message):
    # Provide client options
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Menu")],
            [types.KeyboardButton(text="Cart")],
            [types.KeyboardButton(text="Location")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer("You are now in Client Interaction mode. What would you like to do?", reply_markup=keyboard)

@router.message(F.text == "Admin Interaction")
async def admin_interaction(message: types.Message):
    # Provide admin options
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Add Menu Item")],
            [types.KeyboardButton(text="Remove Menu Item")],
            [types.KeyboardButton(text="View Menu")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer("You are now in Admin Interaction mode. What would you like to do?", reply_markup=keyboard)

@router.message(F.content_type == "contact")
async def store_phone_number(message: types.Message):
    # Extract phone number from the message
    phone_number = message.contact.phone_number
    telegram_id = message.from_user.id

    # Update the client's phone number in the database
    execute_query(
        "UPDATE clients SET phone_number = ? WHERE telegram_id = ?",
        (phone_number, telegram_id)
    )

    await message.answer("Thank you! Your phone number has been saved.")

    # Provide client options
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Menu")],
            [types.KeyboardButton(text="Cart")],
            [types.KeyboardButton(text="Location")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer("What would you like to do?", reply_markup=keyboard)