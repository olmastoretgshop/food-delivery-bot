from aiogram import Router, types
from aiogram.filters import Command
from aiogram import F
from database.db import execute_query

router = Router()

@router.message(F.text == "Menu")
async def show_menu(message: types.Message):
    # Fetch menu items from the database
    menu_items = execute_query("SELECT name, description, price, image_path FROM menu", fetch=True)

    if not menu_items:
        await message.answer("No menu items found.")
        return

    # Create a keyboard with menu item names
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item[0])] for item in menu_items],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    # Add "Cancel" and "Request Delivery" buttons
    keyboard.keyboard.append([types.KeyboardButton(text="Cancel")])
    keyboard.keyboard.append([types.KeyboardButton(text="Request Delivery")])

    await message.answer("Here's our menu:", reply_markup=keyboard)

@router.message(lambda message: message.text in [item[0] for item in execute_query("SELECT name FROM menu", fetch=True)])
async def show_item_details(message: types.Message):
    # Fetch the selected menu item from the database
    menu_item = execute_query("SELECT name, description, price, image_path FROM menu WHERE name = ?", (message.text,), fetch=True)

    if not menu_item:
        await message.answer("Invalid selection. Please try again.")
        return

    # Send the item details with an image
    if menu_item[0][3]:  # Check if image_path is not None
        await message.answer_photo(
            photo=menu_item[0][3],
            caption=f"**{menu_item[0][0]}**\n\n{menu_item[0][1]}\n\nPrice: ${menu_item[0][2]}\n\nQuantity: 1",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="-", callback_data=f"decrease_{menu_item[0][0]}")],
                    [types.InlineKeyboardButton(text="1", callback_data=f"quantity_{menu_item[0][0]}")],
                    [types.InlineKeyboardButton(text="+", callback_data=f"increase_{menu_item[0][0]}")],
                    [types.InlineKeyboardButton(text="Done", callback_data="done_ordering")],
                    [types.InlineKeyboardButton(text="Cancel", callback_data=f"cancel_{menu_item[0][0]}")],
                ]
            ),
        )
    else:
        await message.answer(
            f"**{menu_item[0][0]}**\n\n{menu_item[0][1]}\n\nPrice: ${menu_item[0][2]}\n\nQuantity: 1",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="-", callback_data=f"decrease_{menu_item[0][0]}")],
                    [types.InlineKeyboardButton(text="1", callback_data=f"quantity_{menu_item[0][0]}")],
                    [types.InlineKeyboardButton(text="+", callback_data=f"increase_{menu_item[0][0]}")],
                    [types.InlineKeyboardButton(text="Done", callback_data="done_ordering")],
                    [types.InlineKeyboardButton(text="Cancel", callback_data=f"cancel_{menu_item[0][0]}")],
                ]
            ),
        )