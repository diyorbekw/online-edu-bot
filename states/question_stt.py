from aiogram.fsm.state import State, StatesGroup


class QuestionsState(StatesGroup):
    answering = State()