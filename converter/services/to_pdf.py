from PIL import Image

from converter import entity
from converter.config import config


def resize_to_a4(image: Image.Image, orientation: entity.Orientation) -> Image.Image:
    """Масштабирует изображение под размер A4, сохраняя пропорции."""
    orientation = orientation if orientation in [entity.Orientation.PORTRAIT, entity.Orientation.LANDSCAPE] else get_orientation_depends_size(image)
    size = config.A4_LANDSCAPE if orientation == entity.Orientation.LANDSCAPE else config.A4_PORTRAIT
    image.thumbnail(size, Image.Resampling.LANCZOS)
    new_img = Image.new("RGB", size, "white")
    x_offset = (size[0] - image.width) // 2
    y_offset = (size[1] - image.height) // 2
    new_img.paste(image, (x_offset, y_offset))
    return new_img


def get_orientation_depends_size(image: Image) -> entity.Orientation:
    if image.width > image.height:
        return entity.Orientation.LANDSCAPE
    else:
        return entity.Orientation.PORTRAIT
