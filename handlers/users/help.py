from aiogram import F
from aiogram.types import CallbackQuery

from keyboard_buttons.inline.menu import back_to_menu
from loader import dp


#help commands
@dp.callback_query(F.data == "help")
async def help_commands(callback: CallbackQuery):
    await callback.message.edit_text("""<b>🆘 Yordam</b>

Quyida botdagi har bir bo‘lim haqida qisqacha ma’lumot berilgan:

📚<b>Darsliklar bo‘limi</b> — Asosiy o‘quv bo‘limi. Bu yerda siz kurslar ro‘yxatini ko‘rasiz, har bir kursda video darslarni tomosha qilib, testlar yechib mavzuni mustahkamlaysiz.

❓ <b>FAQ</b> — Ko‘p so‘raladigan savollar bo‘limi. Botdan qanday foydalanish, testlar qanday ishlaydi va boshqa tez-tez uchraydigan savollar va ularning javoblari.

ℹ️ <b>Biz haqimizda</b> — Ushbu bot va uning maqsadi haqida qisqacha ma’lumot. Nima uchun yaratilgan, kimlar uchun mo‘ljallangan.

📊 <b>Statistika</b> — Sizning o‘qishdagi yutuqlaringiz, nechta dars ko‘rganingiz, nechta test yechganingiz kabi shaxsiy statistika.

💎 <b>Tariflar</b> — Kurslardan foydalanish uchun mavjud tariflar haqida ma’lumot. Ba’zi darslar bepul, ba’zilari esa pullik bo‘lishi mumkin.

📨 <b>Murojaat yuborish</b> — Agar sizda savol, taklif yoki muammo bo‘lsa, shu bo‘lim orqali biz bilan bog‘lanishingiz mumkin.

🆘 <b>Yordam</b> — Ushbu bo‘lim aynan siz hozir ochgan sahifa — botdan qanday foydalanish haqida to‘liq ma’lumot.

⭐️ <b>Fikr bildirish</b> — Bot haqida o‘z fikringizni, takliflaringizni yoki muammolaringizni bildiring. Sizning fikringiz biz uchun muhim!

🤖 <b>AI So‘rovlarim</b> — Sun’iy intellektga asoslangan savol-javob bo‘limi. Bu yerda siz sun‘iy intellektdan so'ragan savollaringiz va javoblaringizni ko'rishingiz mumkin.


Agar sizda boshqa savol yoki tushunarsiz holat bo‘lsa, bemalol “📨 Murojaat yuborish” orqali yozing. Sizga doimo yordam berishga tayyormiz! ✅""", reply_markup=back_to_menu, parse_mode="HTML")