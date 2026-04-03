from aiogram.fsm.state import State, StatesGroup

class AddComplex(StatesGroup):
    name = State()
    district = State()
    estate_class = State()
    finish_type = State()
    price = State()
    floors = State()
    amenities = State()
    deadline = State()
    current_stage = State()
    location_link = State()
    photos = State()
    floor_plans = State()

class EditComplex(StatesGroup):
    choice_district = State()
    choice_class = State()
    choice_complex = State()
    action_select = State()
    choice_field = State()
    input_value = State()

class RequestReview(StatesGroup):
    name = State()
    comment = State()

class UserSearch(StatesGroup):
    input_name = State()