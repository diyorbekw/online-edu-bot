from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from loader import CHANNEL_ID, bot, db, dp

def get_category_keyboard():
    categories = db.get_all_categories()
    buttons = [
        [InlineKeyboardButton(text=category[1], callback_data=f"category_{category[0]}")] 
        for category in categories
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="main_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    return keyboard


@dp.callback_query(F.data.startswith('lesson_'))
async def send_video_handler(callback: CallbackQuery):
    lesson_id = int(callback.data.split("_")[1])
    video = db.get_video_by_lesson_id(lesson_id=lesson_id)
    lesson = db.get_lesson_by_id(lesson_id=lesson_id)
    
    if not video:
        await callback.answer("Video topilmadi!")
        return
    
    end_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_categories_2"),
            InlineKeyboardButton(text="✅ Testni boshlash", callback_data=f"questions_{video[0][0]}")]
        ]
    )
    
    txt = f"""
<b>{lesson[1]}</b>

{lesson[2]}
    """
    
    try:
        await bot.copy_message(
            chat_id=callback.from_user.id,
            from_chat_id=CHANNEL_ID,
            message_id=video[0][1].split("/")[-1], 
            caption=txt,
            parse_mode='HTML',
            reply_markup=end_button
        )
        await callback.message.delete()
    except Exception as e:
        await callback.answer(f"Xatolik yuz berdi: {str(e)}")
        
@dp.callback_query(F.data == "back_to_categories_2")
async def back_to_categories_2(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        text="Darsliklar bo'limi.\nO'zingizga yoqgan mavzuni tanlang va darslarni tomosha qiling!",
        reply_markup=get_category_keyboard()
    )
