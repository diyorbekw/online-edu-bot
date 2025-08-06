from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📚 Darsliklar bo'limi", callback_data="categories"),
        ],
        [
            InlineKeyboardButton(text="❓ FAQ", callback_data="faq"),
            InlineKeyboardButton(text="ℹ️ Biz haqimizda", callback_data="about"),
        ],
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="statistics"),
            InlineKeyboardButton(text="💎 Tariflar", callback_data="subscription"),
        ],
        [
            InlineKeyboardButton(text="⭐ Fikr bildirish", callback_data="feedback"),
            InlineKeyboardButton(text="🆘 Qo'llanma", callback_data="help"),
        ],
    ]
)

back_to_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Bosh menyuga", callback_data="main_menu")
        ]
    ]
)