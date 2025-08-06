from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from filters.admin import IsBotAdminFilter
from keyboard_buttons.inline.menu import back_to_menu, menu
from loader import ADMINS, GROUP, bot, db, dp


class FeedbackStates(StatesGroup):
    waiting_for_rating = State()
    waiting_for_comment = State()

class FeedbackResponseStates(StatesGroup):
    waiting_for_response = State()

def feedback_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1", callback_data="rating_1"),
            InlineKeyboardButton(text="2", callback_data="rating_2"),
            InlineKeyboardButton(text="3", callback_data="rating_3"),
            InlineKeyboardButton(text="4", callback_data="rating_4"),
            InlineKeyboardButton(text="5", callback_data="rating_5")
        ],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")],
    ])

@dp.callback_query(F.data == "feedback")
async def start_feedback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FeedbackStates.waiting_for_rating)
    await callback.message.edit_text(
        "⭐ <b>Xizmatimizni qanday baholaysiz?</b>\n\n"
        "Iltimos, 1 dan 5 gacha bo'lgan baholardan birini tanlang:",
        reply_markup=feedback_kb(),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(FeedbackStates.waiting_for_rating, F.data.startswith("rating_"))
async def process_rating(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[1])
    await state.update_data(rating=rating)
    await state.set_state(FeedbackStates.waiting_for_comment)
    
    await callback.message.edit_text(
        "✍️ <b>Fikr-mulohazalaringizni yozib qoldiring:</b>\n\n"
        "Xizmatimiz sifatiga o'z fikringizni qoldirishingiz mumkin (500 belgigacha).",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="cancel_feedback")]
        ])
    )
    await callback.answer()

@dp.message(FeedbackStates.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    if len(message.text) > 500:
        await message.answer("❗ Iltimos, 500 ta belgidan oshmaslikka harakat qiling!")
        return
    
    data = await state.get_data()
    rating = data.get('rating', 0)
    user = db.select_user(telegram_id=message.from_user.id)
    
    feedback_text = (
        "📝 <b>Yangi fikr-mulohaza!</b>\n\n"
        f"👤 <b>Foydalanuvchi:</b> {user[2] if user else message.from_user.full_name}\n"
        f"🆔 <b>ID:</b> {message.from_user.id}\n"
        f"⭐ <b>Bahosi:</b> {'★' * rating + '☆' * (5 - rating)}\n"
        f"✍️ <b>Fikri:</b>\n{message.text}"
    )
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Javob berish", callback_data=f"reply_feedback:{message.from_user.id}")]
    ])
    
    try:
        await bot.send_message(
            chat_id=GROUP,
            text=feedback_text,
            parse_mode="HTML",
            reply_markup=reply_markup,
            message_thread_id=6
        )
        
        await message.answer(
            "✅ <b>Fikr-mulohazangiz uchun rahmat!</b>\n\n"
            "Sizning bahoyingiz va sharhingiz biz uchun juda muhim.",
            parse_mode="HTML",
            reply_markup=back_to_menu
        )
        
    except Exception as e:
        print(f"Feedbackni guruhga yuborishda xato: {e}")
        await message.answer(
            "❗ Fikr-mulohazangiz yuborilmadi. Iltimos, keyinroq urunib ko'ring.",
            parse_mode="HTML"
        )
    
    await state.clear()

@dp.callback_query(F.data.startswith("reply_feedback:"))
async def start_feedback_response(callback: CallbackQuery, state: FSMContext):
    if not await IsBotAdminFilter(user_ids=ADMINS)(callback):
        await callback.answer("❌ Sizda bunday amalni bajarish huquqi yo'q!", show_alert=True)
        return
    
    user_id = int(callback.data.split(":")[1])
    await state.set_state(FeedbackResponseStates.waiting_for_response)
    await state.update_data(
        target_user_id=user_id,
        feedback_message_id=callback.message.message_id,
        admin_chat_id=callback.message.chat.id  # Guruh chat ID sini saqlaymiz
    )
    
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    
@dp.message(FeedbackResponseStates.waiting_for_response)
async def send_feedback_response(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('target_user_id')
    feedback_message_id = data.get('feedback_message_id')
    admin_chat_id = data.get('admin_chat_id')  # Guruh chat ID sini olamiz
    
    if not user_id:
        await message.answer("❗ Xatolik yuz berdi. Iltimos, qaytadan urunib ko'ring.")
        await state.clear()
        return
    
    try:
        # Foydalanuvchiga javob yuborish
        await bot.send_message(
            chat_id=user_id,
            text=f"📩 <b>Administrator javobi:</b>\n\n{message.text}",
            parse_mode="HTML"
        )
        
        # Adminga tasdiqlash xabari
        await message.answer(
            f"✅ Javobingiz foydalanuvchiga yuborildi (ID: {user_id})",
        )
        
        # Guruhdagi feedback xabarini yangilash
        if admin_chat_id and feedback_message_id:
            try:
                await bot.edit_message_reply_markup(
                    chat_id=admin_chat_id,
                    message_id=feedback_message_id,
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ Javob berildi", 
                            callback_data="already_responded"
                        )]
                    ])
                )
            except Exception as e:
                print(f"Guruh xabarini yangilashda xato: {e}")
        
    except Exception as e:
        print(f"Javob yuborishda xato: {e}")
        await message.answer(
            "❗ Javob yuborilmadi. Foydalanuvchi botni bloklagan bo'lishi mumkin.",
            parse_mode="HTML"
        )
    
    await state.clear()

@dp.callback_query(F.data == "cancel_feedback")
async def cancel_feedback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        """👋 Assalomu alaykum! Onlayn video darslar botiga xush kelibsiz!""",
        reply_markup=menu,
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "already_responded")
async def already_responded(callback: CallbackQuery):
    await callback.answer("⚠️ Bu feedbackga allaqachon javob berilgan!", show_alert=True)