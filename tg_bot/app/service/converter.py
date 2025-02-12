import io

from PIL import Image
from aiogram import Bot
from aiogram.types import Message

from app import entity
from app.config import config


class ConverterService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def from_jpg_to_pdf(self, orientation: str, images: list[bytes]) -> bytes:
        images = [self.resize_to_a4(Image.open(io.BytesIO(img)).convert("RGB"), orientation) for img in images]
        pdf_bytes = io.BytesIO()
        images[0].save(pdf_bytes, format="PDF", save_all=True, append_images=images[1:])
        pdf_bytes.seek(0)
        return pdf_bytes.getvalue()

    def resize_to_a4(self, image: Image.Image, orientation: str) -> Image.Image:
        """Масштабирует изображение под размер A4, сохраняя пропорции."""
        orientation = orientation if orientation in [entity.Orientation.PORTRAIT.value,
                                                     entity.Orientation.LANDSCAPE.value] else self.get_orientation_depends_size(
            image)
        size = config.A4_LANDSCAPE if orientation == entity.Orientation.LANDSCAPE.value else config.A4_PORTRAIT
        image.thumbnail(size, Image.Resampling.LANCZOS)
        new_img = Image.new("RGB", size, "white")
        x_offset = (size[0] - image.width) // 2
        y_offset = (size[1] - image.height) // 2
        new_img.paste(image, (x_offset, y_offset))
        return new_img

    def get_orientation_depends_size(self, image: Image) -> str:
        if image.width > image.height:
            return entity.Orientation.LANDSCAPE.value
        else:
            return entity.Orientation.PORTRAIT.value

    async def download_file_from_message(self, message: Message) -> bytes:
        file_id = message.photo[-1].file_id if message.photo else message.document.file_id
        file = await self.bot.get_file(file_id)

        img_bytes = io.BytesIO()
        await self.bot.download_file(file.file_path, img_bytes)
        img_bytes.seek(0)
        return img_bytes.getvalue()
