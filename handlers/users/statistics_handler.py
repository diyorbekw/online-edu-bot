from aiogram import F
from aiogram.types import CallbackQuery

from keyboard_buttons.inline.menu import back_to_menu
from loader import db, dp


@dp.callback_query(F.data == "statistics")
async def help_commands(callback: CallbackQuery):
    statistics = db.statistics(telegram_id=int(callback.from_user.id))
    await callback.message.edit_text(statistics, parse_mode='HTML', reply_markup=back_to_menu)