from aiogram import F
from aiogram.types import CallbackQuery

from keyboard_buttons.inline.menu import menu
from loader import dp


@dp.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: CallbackQuery):
    await callback.message.edit_text("""👋 Assalomu alaykum! Onlayn video darslar botiga xush kelibsiz!

<b>📚 Bu bot orqali siz:</b>
— Turli mavzulardagi video darslarni tomosha qilasiz
— Har bir darsdan so'ng test topshiriqlarini bajarasiz
— Mavzuni mustahkamlash uchun qo‘shimcha materiallarga ega bo‘lasiz

▶️ Darslarni boshlash uchun <i>“📚 Darsliklar bo‘limi”</i> tugmasini bosing.

Yordam kerakmi? <i>“🆘 Yordam”</i> bo‘limiga murojaat qiling.
""", reply_markup=menu, parse_mode="HTML")