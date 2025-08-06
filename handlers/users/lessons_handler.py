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

def get_lessons_keyboard(category_id: int):
    lessons = db.get_lesson_by_category(category_id=category_id)
    buttons = [
        [InlineKeyboardButton(text=lesson[1], callback_data=f"lesson_{lesson[0]}")] 
        for lesson in lessons
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_categories")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    return keyboard

@dp.callback_query(F.data.startswith('category_'))
async def show_lessons(callback: CallbackQuery):
    try:
        category_id = int(callback.data.split("_")[1])
        category_data = db.get_category_by_id(category_id)
        if category_data:
            category_description = category_data[2]
            lessons_keyboard = get_lessons_keyboard(category_id)
            await callback.message.edit_text(text=category_description, reply_markup=lessons_keyboard)
    except (ValueError, IndexError):
        await callback.answer("Xatolik yuz berdi! Iltimos, qayta urunib ko'ring.")

@dp.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Darsliklar bo'limi.\nO'zingizga yoqgan mavzuni tanlang va darslarni tomosha qiling!",
        reply_markup=get_category_keyboard()
    )