from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F
from database.db import execute_query
from config import ADMIN_ID

router = Router()

# Define states for the FSM (Finite State Machine)
class MenuForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_image_path = State()
    waiting_for_item_selection = State()

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

@router.message(F.text == "Add Menu Item")
async def add_menu_item_start(message: types.Message, state: FSMContext):
    await message.answer("Please enter the name of the menu item:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(MenuForm.waiting_for_name)

@router.message(MenuForm.waiting_for_name)
async def add_menu_item_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Please enter the description of the menu item:")
    await state.set_state(MenuForm.waiting_for_description)

@router.message(MenuForm.waiting_for_description)
async def add_menu_item_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Please enter the price of the menu item:")
    await state.set_state(MenuForm.waiting_for_price)

@router.message(MenuForm.waiting_for_price)
async def add_menu_item_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await message.answer("Please enter the image path of the menu item:")
        await state.set_state(MenuForm.waiting_for_image_path)
    except ValueError:
        await message.answer("Invalid price. Please enter a valid number.")

@router.message(MenuForm.waiting_for_image_path)
async def add_menu_item_image_path(message: types.Message, state: FSMContext):
    # Save the image file and get its path
    image_path = f"images/{message.photo[-1].file_id}.jpg"
    await message.photo[-1].download(destination_file=image_path)

    # Store the image path in the database
    data = await state.get_data()
    execute_query(
        "INSERT INTO menu (name, description, price, image_path) VALUES (?, ?, ?, ?)",
        (data["name"], data["description"], data["price"], image_path)
    )
    await message.answer(f"Added {data['name']} to the menu!", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

@router.message(F.text == "Remove Menu Item")
async def remove_menu_item_start(message: types.Message, state: FSMContext):
    # Fetch all menu items from the database
    menu_items = execute_query("SELECT id, name FROM menu", fetch=True)

    if not menu_items:
        await message.answer("No menu items found.", reply_markup=types.ReplyKeyboardRemove())
        return

    # Create a keyboard with menu item names
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item[1])] for item in menu_items],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer("Please select the menu item to remove:", reply_markup=keyboard)
    await state.set_state(MenuForm.waiting_for_item_selection)

@router.message(MenuForm.waiting_for_item_selection)
async def remove_menu_item_selection(message: types.Message, state: FSMContext):
    # Fetch the selected menu item from the database
    menu_item = execute_query("SELECT id FROM menu WHERE name = ?", (message.text,), fetch=True)

    if not menu_item:
        await message.answer("Invalid selection. Please try again.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
        return

    # Remove the menu item from the database
    execute_query(
        "DELETE FROM menu WHERE id = ?",
        (menu_item[0][0],)
    )
    await message.answer(f"Removed {message.text} from the menu.", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

@router.message(F.text == "View Menu")
async def view_menu(message: types.Message):
    # Fetch all menu items from the database
    menu_items = execute_query("SELECT name, description, price, image_path FROM menu", fetch=True)

    if not menu_items:
        await message.answer("No menu items found.")
        return

    # Send each menu item with its details
    for item in menu_items:
        if item[3]:  # Check if image_path is not None
            await message.answer_photo(
                photo=item[3],
                caption=f"**{item[0]}**\n\n{item[1]}\n\nPrice: ${item[2]}",
            )
        else:
            await message.answer(
                f"**{item[0]}**\n\n{item[1]}\n\nPrice: ${item[2]}"
            )