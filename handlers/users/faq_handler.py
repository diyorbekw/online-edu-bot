from aiogram import F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from loader import db, dp

FAQ_PAGE_SIZE = 5 

def get_faq_keyboard(page: int = 1):
    faqs = db.get_all_faqs(page=page, limit=FAQ_PAGE_SIZE)
    total_faqs = db.count_faqs()[0]
    total_pages = (total_faqs + FAQ_PAGE_SIZE - 1) // FAQ_PAGE_SIZE
    
    buttons = []
    for faq in faqs:
        buttons.append([InlineKeyboardButton(
            text=faq[1], 
            callback_data=f"faq_detail_{faq[0]}"  
        )])
    
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=f"faq_page_{page-1}"
        ))
    if page < total_pages:
        pagination_buttons.append(InlineKeyboardButton(
            text="➡️",
            callback_data=f"faq_page_{page+1}"
        ))
    
    if pagination_buttons:
        buttons.append(pagination_buttons)
    
    buttons.append([InlineKeyboardButton(
        text="🔙 Orqaga",
        callback_data="main_menu"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.callback_query(F.data == "faq")
async def show_faq_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Ko'p beriladigan savollar:",
        reply_markup=get_faq_keyboard()
    )

@dp.callback_query(F.data.startswith("faq_page_"))
async def process_faq_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    await callback.message.edit_text(
        text="Ko'p beriladigan savollar:",
        reply_markup=get_faq_keyboard(page=page)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("faq_detail_"))
async def process_faq_detail(callback: CallbackQuery):
    faq_id = int(callback.data.split("_")[2])
    answer = db.get_faq_answer(faq_id)
    
    if answer:
        await callback.message.edit_text(
            f"❓ Savol: {callback.message.reply_markup.inline_keyboard[0][0].text}\n\n"
            f"💡 Javob: {answer[0]}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 FAQ ro'yxatiga qaytish", callback_data="faq_page_1")]
            ])
        )
    else:
        await callback.answer("Javob topilmadi!", show_alert=True)
    
    await callback.answer()