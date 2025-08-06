from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from keyboard_buttons.default.user_buttons import phone_button
from keyboard_buttons.inline.menu import menu
from loader import db, dp
from states.reg_stt import Registration


@dp.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    # Check if user already exists
    user = db.select_user(telegram_id=message.from_user.id)
    if user:
        await message.answer("""👋 Assalomu alaykum! Onlayn video darslar botiga xush kelibsiz!

<b>📚 Bu bot orqali siz:</b>
— Turli mavzulardagi video darslarni tomosha qilasiz
— Har bir darsdan so'ng test topshiriqlarini bajarasiz
— Mavzuni mustahkamlash uchun qo‘shimcha materiallarga ega bo‘lasiz

▶️ Darslarni boshlash uchun <i>“📚 Darsliklar bo‘limi”</i> tugmasini bosing.

Yordam kerakmi? <i>“🆘 Yordam”</i> bo‘limiga murojaat qiling.
""", reply_markup=menu, parse_mode="HTML")
        return
    
    # Request phone number
    await message.answer(
        "Iltimos, telefon raqamingizni yuboring:",
        reply_markup=phone_button()
    )
    await state.set_state(Registration.waiting_for_phone)

# Handle phone number input
@dp.message(Registration.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone_number = None
    
    # If user sent contact
    if message.contact:
        phone_number = message.contact.phone_number
    # If user typed manually
    elif message.text:
        # Simple phone number validation
        if len(message.text) >= 9 and message.text.replace('+', '').isdigit():
            phone_number = message.text
        else:
            await message.answer("Iltimos, to'g'ri telefon raqam kiriting!")
            return
    
    if phone_number:
        await state.update_data(phone_number=phone_number)
        await message.answer(
            "Iltimos, ism va familiyangizni kiriting:",
            reply_markup=ReplyKeyboardRemove()  # Remove keyboard
        )
        await state.set_state(Registration.waiting_for_full_name)
    else:
        await message.answer("Iltimos, to'g'ri telefon raqam kiriting!")

# Handle full name input
@dp.message(Registration.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()
    if len(full_name.split()) < 2:
        await message.answer("Iltimos, to'liq ism va familiyangizni kiriting!")
        return
    
    data = await state.get_data()
    try:
        db.add_user(
            telegram_id=message.from_user.id,
            full_name=full_name,
            phone_number=data['phone_number']
        )
        await message.answer("""👋 Assalomu alaykum! Onlayn video darslar botiga xush kelibsiz!

<b>📚 Bu bot orqali siz:</b>
— Turli mavzulardagi video darslarni tomosha qilasiz
— Har bir darsdan so'ng test topshiriqlarini bajarasiz
— Mavzuni mustahkamlash uchun qo‘shimcha materiallarga ega bo‘lasiz

▶️ Darslarni boshlash uchun <i>“📚 Darsliklar bo‘limi”</i> tugmasini bosing.

Yordam kerakmi? <i>“🆘 Yordam”</i> bo‘limiga murojaat qiling.
""", reply_markup=menu, parse_mode="HTML")
    except Exception as e:
        print(e)
        await message.answer("Assalomu alaykum! Ro'yxatdan o'tishda xatolik yuz berdi.")
    
    await state.clear()