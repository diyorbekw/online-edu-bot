from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from loader import db, dp


def get_category_keyboard():
    categories = db.get_all_categories()
    buttons = [
        [InlineKeyboardButton(text=category[1], callback_data=f"category_{category[0]}")] 
        for category in categories
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    return keyboard

@dp.callback_query(F.data == "categories")
async def category_commands(callback: CallbackQuery):
    await callback.message.edit_text("Darsliklar bo'limi.\nO'zingizga yoqgan mavzuni tanlang va darslarni tomosha qiling!", reply_markup=get_category_keyboard())