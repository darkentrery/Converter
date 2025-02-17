import base64
import io

from aiogram import Bot
from aiogram.types import Message

from app import entity


class ConverterService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def download_file_from_message(self, message: Message) -> str:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        file = await self.bot.get_file(file_id)

        img_bytes = io.BytesIO()
        await self.bot.download_file(file.file_path, img_bytes)
        img_bytes.seek(0)
        return base64.b64encode(img_bytes.getvalue()).decode("utf-8")

    async def check_message_by_format(self, message: Message, from_format: str) -> bool:
        check = False
        match from_format:
            case "jpg":
                if message.photo or message.document.mime_type.startswith("image/"):
                    check = True
            case "word":
                if message.document.file_name.endswith(".docx") or message.document.file_name.endswith(".doc"):
                    check = True
            case "powerpoint":
                if message.document.file_name.endswith(".pptx") or message.document.file_name.endswith(".ppt"):
                    check = True
            case "excel":
                if message.document.file_name.endswith(".xlsx"):
                    check = True
            case "html":
                if message.document.file_name.endswith(".html"):
                    check = True
            case _:
                check = False
        return check
