import io
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile, ReplyKeyboardMarkup, KeyboardButton
from PIL import Image

from converter import entity
from converter.config import config
from converter.services.to_pdf import resize_to_a4

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

user_images = {}
user_data: dict[int, entity.UserData] = {}


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = entity.UserData()
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=entity.Button.LPG_TO_PDF.value)]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await message.answer("Привет! Выбери действие:", reply_markup=keyboard)


@dp.message(lambda message: message.text == entity.Button.LPG_TO_PDF.value)
async def start_conversion(message: types.Message):
    chat_id = message.chat.id
    user_data[chat_id] = entity.UserData(step=entity.Step.UPLOADING)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=entity.Button.READY.value), KeyboardButton(text=entity.Button.LPG_TO_PDF.value)]
        ],
        resize_keyboard=True
    )
    await message.answer("Отправь изображения для конвертации в PDF.", reply_markup=keyboard)


@dp.message(lambda message: message.photo or (message.document and message.document.mime_type.startswith("image/")))
async def collect_images(message: types.Message):
    """Сохраняет изображения в список для текущего пользователя."""
    chat_id = message.chat.id
    if user_data.get(chat_id, entity.UserData()).step != entity.Step.UPLOADING:
        return

    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    file = await bot.get_file(file_id)

    img_bytes = io.BytesIO()
    await bot.download_file(file.file_path, img_bytes)
    img_bytes.seek(0)

    user_data[chat_id].images.append(img_bytes)
    await message.answer("✅ Изображение добавлено! Отправь ещё или нажми 'Готово'.")


@dp.message(lambda message: message.text and message.text == entity.Button.READY.value)
async def ask_orientation(message: types.Message):
    """Спрашивает ориентацию перед созданием PDF."""
    user = user_data.get(message.chat.id, entity.UserData())
    if not user.images:
        await message.answer("❌ Ты не отправил ни одного изображения!")
        return

    user.step = entity.Step.ORIENTATION
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=entity.Button.LANDSCAPE.value),
                KeyboardButton(text=entity.Button.PORTRAIT.value),
                KeyboardButton(text=entity.Button.MIX.value),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выбери ориентацию страницы:", reply_markup=keyboard)


@dp.message(lambda message: message.text and message.text in [
    entity.Orientation.LANDSCAPE.value, entity.Orientation.PORTRAIT.value, entity.Orientation.MIX.value
])
async def create_pdf(message: types.Message):
    """Создаёт PDF из всех загруженных изображений после выбора ориентации."""
    chat_id = message.chat.id
    user = user_data.get(message.chat.id, entity.UserData())
    if user.step != entity.Step.ORIENTATION:
        return

    user.orientation = entity.Orientation(message.text)

    images = [resize_to_a4(Image.open(img).convert("RGB"), user.orientation) for img in user_data[chat_id].images]
    pdf_bytes = io.BytesIO()
    images[0].save(pdf_bytes, format="PDF", save_all=True, append_images=images[1:])
    pdf_bytes.seek(0)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Конвертация JPG to PDF")]
        ],
        resize_keyboard=True
    )

    await message.answer_document(
        BufferedInputFile(pdf_bytes.getvalue(), filename="converted.pdf"),
        caption=f"📄 Твой PDF готов! (Ориентация: {user.orientation})",
        reply_markup=keyboard
    )

    user_data[chat_id] = entity.UserData()
