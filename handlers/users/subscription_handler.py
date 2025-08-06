from aiogram import F
from aiogram.types import CallbackQuery

from loader import dp


@dp.callback_query(F.data == "subscription")
async def help_commands(callback: CallbackQuery):
    await callback.answer("Tariflar bo'limi hozircha tayyor emas", show_alert=True)