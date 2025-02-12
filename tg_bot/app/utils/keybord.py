from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_markup_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=item) for item in items]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard
