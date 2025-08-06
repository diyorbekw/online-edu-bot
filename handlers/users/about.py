from aiogram import F
from aiogram.types import CallbackQuery

from keyboard_buttons.inline.menu import back_to_menu
from loader import dp


#about commands
@dp.callback_query(F.data == "about")
async def about_commands(callback: CallbackQuery):
    await callback.message.edit_text(text="""<b>ℹ️ Biz haqimizda</b>

Ushbu bot — ta’lim olishni soddalashtirish va interaktiv tarzda bilimlarni mustahkamlash uchun yaratilgan onlayn platforma.

🎥 Har bir mavzu uchun maxsus tayyorlangan video darslar
📝 Har bir darsdan so'ng testlar va mashqlar
📈 Foydalanuvchi statistikasini yuritish imkoniyati

Bizning maqsadimiz — sifatli ta'limni har kimga, istalgan joyda taqdim etish.""", reply_markup=back_to_menu, parse_mode="HTML")
