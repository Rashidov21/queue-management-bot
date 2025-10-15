from aiogram.fsm.state import State, StatesGroup


class RoleSelection(StatesGroup):
    waiting_for_role = State()


class ProviderRegistration(StatesGroup):
    waiting_for_name = State()
    waiting_for_service = State()
    waiting_for_location = State()
    waiting_for_phone = State()
    waiting_for_working_days = State()
    waiting_for_start_time = State()
    waiting_for_end_time = State()
    waiting_for_slot_duration = State()


class ClientBooking(StatesGroup):
    waiting_for_service = State()
    waiting_for_provider = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_confirmation = State()


class ProviderSchedule(StatesGroup):
    waiting_for_day_selection = State()
    waiting_for_start_time = State()
    waiting_for_end_time = State()
    waiting_for_duration = State()
