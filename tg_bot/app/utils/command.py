from aiogram.types import BotCommand


def get_bot_commands() -> list[BotCommand]:
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="convert", description="Конвертировать файлы"),
        BotCommand(command="feedback", description="Оставить отзыв")
    ]
    return commands
