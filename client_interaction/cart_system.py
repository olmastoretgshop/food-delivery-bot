from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from database.db import execute_query

router = Router()

@router.callback_query(lambda c: c.data.startswith("increase_"))
async def increase_quantity(callback_query: types.CallbackQuery, state: FSMContext):
    item_name = callback_query.data.replace("increase_", "")

    # Update the quantity in the cart
    data = await state.get_data()
    cart = data.get("cart", {})
    if item_name in cart:
        cart[item_name] += 1
    else:
        cart[item_name] = 1
    await state.update_data(cart=cart)

    # Fetch the item details from the database
    item_details = execute_query("SELECT name, description, price, image_path FROM menu WHERE name = ?", (item_name,), fetch=True)

    if not item_details:
        await callback_query.answer("Invalid item. Please try again.")
        return

    # Create inline buttons for updating quantity
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="-", callback_data=f"decrease_{item_name}")],
            [types.InlineKeyboardButton(text=f"{cart[item_name]}", callback_data=f"quantity_{item_name}")],
            [types.InlineKeyboardButton(text="+", callback_data=f"increase_{item_name}")],
            [types.InlineKeyboardButton(text="Done", callback_data="done_ordering")],
            [types.InlineKeyboardButton(text="Cancel", callback_data=f"cancel_{item_name}")],
        ]
    )

    # Edit the message to update the quantity
    try:
        if item_details[0][3]:  # Check if image_path is not None
            await callback_query.message.edit_caption(
                caption=f"**{item_details[0][0]}**\n\n{item_details[0][1]}\n\nPrice: ${item_details[0][2]}\n\nQuantity: {cart[item_name]}",
                reply_markup=keyboard,
            )
        else:
            await callback_query.message.edit_text(
                f"**{item_details[0][0]}**\n\n{item_details[0][1]}\n\nPrice: ${item_details[0][2]}\n\nQuantity: {cart[item_name]}",
                reply_markup=keyboard,
            )
    except Exception as e:
        print(f"Error editing message: {e}")

    await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith("decrease_"))
async def decrease_quantity(callback_query: types.CallbackQuery, state: FSMContext):
    item_name = callback_query.data.replace("decrease_", "")

    # Update the quantity in the cart
    data = await state.get_data()
    cart = data.get("cart", {})
    if item_name in cart:
        if cart[item_name] > 1:
            cart[item_name] -= 1
        else:
            del cart[item_name]  # Remove the item if quantity is 0
    await state.update_data(cart=cart)

    # Fetch the item details from the database
    item_details = execute_query("SELECT name, description, price, image_path FROM menu WHERE name = ?", (item_name,), fetch=True)

    if not item_details:
        await callback_query.answer("Invalid item. Please try again.")
        return

    # Create inline buttons for updating quantity
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="-", callback_data=f"decrease_{item_name}")],
            [types.InlineKeyboardButton(text=f"{cart.get(item_name, 1)}", callback_data=f"quantity_{item_name}")],
            [types.InlineKeyboardButton(text="+", callback_data=f"increase_{item_name}")],
            [types.InlineKeyboardButton(text="Done", callback_data="done_ordering")],
            [types.InlineKeyboardButton(text="Cancel", callback_data=f"cancel_{item_name}")],
        ]
    )

    # Edit the message to update the quantity
    try:
        if item_details[0][3]:  # Check if image_path is not None
            await callback_query.message.edit_caption(
                caption=f"**{item_details[0][0]}**\n\n{item_details[0][1]}\n\nPrice: ${item_details[0][2]}\n\nQuantity: {cart.get(item_name, 1)}",
                reply_markup=keyboard,
            )
        else:
            await callback_query.message.edit_text(
                f"**{item_details[0][0]}**\n\n{item_details[0][1]}\n\nPrice: ${item_details[0][2]}\n\nQuantity: {cart.get(item_name, 1)}",
                reply_markup=keyboard,
            )
    except Exception as e:
        print(f"Error editing message: {e}")

    await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith("cancel_"))
async def cancel_order(callback_query: types.CallbackQuery, state: FSMContext):
    item_name = callback_query.data.replace("cancel_", "")

    # Remove the item from the cart
    data = await state.get_data()
    cart = data.get("cart", {})
    if item_name in cart:
        del cart[item_name]
    await state.update_data(cart=cart)

    await callback_query.message.delete()
    await callback_query.answer(f"Order for {item_name} canceled.")

@router.callback_query(lambda c: c.data == "done_ordering")
async def done_ordering(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart = data.get("cart", {})

    if not cart:
        await callback_query.answer("Your cart is empty.")
        return

    # Display the cart contents
    total_cost = 0
    message = "Your order:\n\n"
    for item, quantity in cart.items():
        item_details = execute_query("SELECT price FROM menu WHERE name = ?", (item,), fetch=True)
        if item_details:
            price = item_details[0][0]
            total_cost += price * quantity
            message += f"{item} x {quantity} = ${price * quantity:.2f}\n"

    message += f"\nTotal: ${total_cost:.2f}"

    # Create a keyboard for delivery request
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Request Delivery", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await callback_query.message.answer(message, reply_markup=keyboard)
    await callback_query.answer()