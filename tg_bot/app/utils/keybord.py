from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from app import entity


def get_markup_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=item) for item in items]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_inline_keyboard(items: list[str]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=item, callback_data=item)] for item in items
        ]
    )
    return keyboard


def get_inline_keyboard_by_from_format(from_format: str, to_format: str) -> InlineKeyboardMarkup:
    match from_format:
        case "word":
            keyboard = get_inline_keyboard([
                entity.Button.READY.value
            ])
        case "jpg":
            if to_format == "pdf":
                keyboard = get_inline_keyboard([
                    entity.Orientation.LANDSCAPE.value,
                    entity.Orientation.PORTRAIT.value,
                    entity.Orientation.MIX.value
                ])
            else:
                keyboard = get_inline_keyboard([
                    entity.Button.READY.value
                ])
        case _:
            keyboard = get_inline_keyboard([
                entity.Button.READY.value
            ])
    return keyboard


def get_main_markup_keyboard() -> ReplyKeyboardMarkup:
    return get_markup_keyboard([
        entity.Button.CONVERT.value,
        entity.Button.FEEDBACK.value,
        entity.Button.DONAT.value,
    ])
