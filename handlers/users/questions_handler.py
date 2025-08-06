from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
import random
from loader import db, dp


@dp.callback_query(F.data.startswith('questions_'))
async def start_questions(callback: CallbackQuery, state: FSMContext):
    try:
        video_id = int(callback.data.split("_")[1]) 
        questions = db.get_questions_by_video_id(video_id)
        
        if not questions:
            await callback.answer("Bu video uchun savollar mavjud emas!", show_alert=True)
            return
        
        await state.update_data(
            questions=questions,
            current_question_index=0,
            correct_answers=0,
            total_questions=len(questions),
            video_id=video_id  
        )
        
        await ask_question(callback, state)
    except (ValueError, IndexError) as e:
        await callback.answer("Xatolik yuz berdi. Iltimos, qayta urunib ko'ring.")
        print(f"Error in start_questions: {e}")

async def ask_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    question_index = data['current_question_index']
    question = data['questions'][question_index]
    
    keyboard_buttons = [
        [InlineKeyboardButton(text=f"{question[2]}", callback_data="answer_A")],
        [InlineKeyboardButton(text=f"{question[3]}", callback_data="answer_B")],
        [InlineKeyboardButton(text=f"{question[4]}", callback_data="answer_C")],
        [InlineKeyboardButton(text=f"{question[5]}", callback_data="answer_D")],
    ]
    
    random.shuffle(keyboard_buttons)
    
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.delete()
    await callback.message.answer(
        text=f"Savol {question_index + 1}/{data['total_questions']}:\n\n{question[1]}",
        reply_markup=keyboard
    )

@dp.callback_query(F.data.startswith('answer_'))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    user_answer = callback.data.split("_")[1]
    data = await state.get_data()
    question_index = data['current_question_index']
    current_question = data['questions'][question_index]
    
    is_correct = user_answer == current_question[6]
    correct_answers = data['correct_answers'] + (1 if is_correct else 0)
    
    await state.update_data(
        correct_answers=correct_answers,
        current_question_index=question_index + 1
    )
    
    data = await state.get_data()
    if data['current_question_index'] < data['total_questions']:
        await ask_question(callback, state)
    else:
        video_id = data.get('video_id')
        if not video_id:
            await callback.message.edit_text("Xatolik yuz berdi: video ID topilmadi")
            await state.clear()
            return
            
        await finish_quiz(callback, state, video_id)

async def finish_quiz(callback: CallbackQuery, state: FSMContext, video_id: int):
    data = await state.get_data()
    percentage = int((data['correct_answers'] / data['total_questions']) * 100)
    
    success = db.add_result(
        telegram_id=callback.from_user.id,
        correct_answers=data['correct_answers'],
        questions_count=data['total_questions'],
        video_id=video_id
    )
    
    if not success:
        await callback.answer("Natijani saqlashda xatolik yuz berdi", show_alert=True)
    
    video = db.get_video_by_id(video_id)
    if not video:
        await callback.message.edit_text(
            text=f"Test yakunlandi!\n\nTo'g'ri javoblar: {data['correct_answers']}/{data['total_questions']}\nNatija: {percentage}%",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="main_menu")]
            ]))
        await state.clear()
        return
    
    lesson_id = video[0][2]
    
    if percentage >= 70:
        next_lesson = db.get_next_lesson(lesson_id)
        
        if next_lesson:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="⬅️ Asosiy Menyu", callback_data="main_menu"),
                    InlineKeyboardButton(text="Keyingi dars ➡️", callback_data=f"lesson_{next_lesson[0]}")
                ],
            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="main_menu")]
            ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Asosiy Menyu", callback_data="main_menu"),
                InlineKeyboardButton(text="🔄 Qayta ko'rish", callback_data=f"lesson_{lesson_id}")
            ],
        ])
    
    await callback.message.edit_text(
        text=f"Test yakunlandi!\n\n"
             f"To'g'ri javoblar: {data['correct_answers']}/{data['total_questions']}\n"
             f"Natija: {percentage}%",
        reply_markup=keyboard
    )
    
    await state.clear()