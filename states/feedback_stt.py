from aiogram.fsm.state import State, StatesGroup


class FeedbackStates(StatesGroup):
    waiting_for_rating = State()
    waiting_for_comment = State()

class FeedbackResponseStates(StatesGroup):
    waiting_for_response = State()