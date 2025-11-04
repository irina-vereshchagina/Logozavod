from aiogram.fsm.state import StatesGroup, State

class GenerationStates(StatesGroup):
    waiting_for_idea = State()
