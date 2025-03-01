from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from more_itertools import chunked

from app import entity
from app.config import config


def get_markup_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    chunks = list(chunked(items, 2))
    buttons = [[KeyboardButton(text=item) for item in chunk] for chunk in chunks]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_inline_keyboard(items: list[str]) -> InlineKeyboardMarkup:
    chunks = list(chunked(items, 2))
    buttons = [[InlineKeyboardButton(text=item, callback_data=item) for item in chunk] for chunk in chunks]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
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


def get_main_markup_keyboard(user: entity.User) -> ReplyKeyboardMarkup:
    buttons = [
        entity.Button.CONVERT.value,
        entity.Button.FEEDBACK.value,
        entity.Button.DONAT.value,
    ]
    if str(user.tg_id) in config.admins:
        buttons.append(entity.Button.STATISTIC.value)
    return get_markup_keyboard(buttons)
