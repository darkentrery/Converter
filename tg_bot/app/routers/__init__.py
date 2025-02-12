from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, ReplyKeyboardMarkup, KeyboardButton
from pydantic import TypeAdapter

from app import entity
from app.service import ConverterService, ApiService
from app.utils.keybord import get_markup_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext, api_service: ApiService):
    formats = await api_service.get_formats()
    await state.set_data(entity.UserData().model_dump())
    await state.set_state(entity.UserState.START)
    keyboard = get_markup_keyboard([format.name for format in formats])
    await message.answer("Привет! Выбери формат загружаемого файла:", reply_markup=keyboard)


@router.message(
    # F.text.in_(["jpg"]),
    entity.UserState.START
)
async def choose_from_format(message: types.Message, state: FSMContext, api_service: ApiService):
    formats = await api_service.get_cross_formats_by_format_name(message.text)
    keyboard = get_markup_keyboard([format.format_to_name for format in formats])
    _state = TypeAdapter(entity.UserData).validate_python((await state.get_data()))
    _state.from_format = message.text
    await state.update_data(_state.model_dump())
    await state.set_state(entity.UserState.CHOOSE_FROM)
    await message.answer("Выбери формат желаемого файла", reply_markup=keyboard)


@router.message(
    # F.text.in_(["pdf"]),
    entity.UserState.CHOOSE_FROM
)
async def start_conversion(message: types.Message, state: FSMContext):
    keyboard = get_markup_keyboard([
        entity.Orientation.LANDSCAPE.value,
        entity.Orientation.PORTRAIT.value,
        entity.Orientation.MIX.value
    ])
    _state = TypeAdapter(entity.UserData).validate_python((await state.get_data()))
    _state.to_format = message.text
    await state.update_data(_state.model_dump())
    await state.set_state(entity.UserState.CHOOSE_TO)
    await message.answer("Отправь изображения для конвертации в PDF.", reply_markup=keyboard)


@router.message(
    (F.photo | (F.document & F.document.mime_type.startswith("image/"))),
    StateFilter(entity.UserState.UPLOADING, entity.UserState.CHOOSE_TO),
)
async def collect_images(message: types.Message, state: FSMContext, convert_service: ConverterService):
    """Сохраняет изображения в список для текущего пользователя."""
    img_bytes = await convert_service.download_file_from_message(message)

    _state = TypeAdapter(entity.UserData).validate_python((await state.get_data()))
    _state.images.append(img_bytes)
    await state.update_data(_state.model_dump())
    await state.set_state(entity.UserState.UPLOADING)

    keyboard = get_markup_keyboard([
        entity.Orientation.LANDSCAPE.value,
        entity.Orientation.PORTRAIT.value,
        entity.Orientation.MIX.value
    ])
    await message.answer(
        "✅ Изображение добавлено! Отправь ещё или выберите ориентацию страниц для конвертации.",
        reply_markup=keyboard
    )


@router.message(
    F.text.in_([entity.Orientation.LANDSCAPE.value, entity.Orientation.PORTRAIT.value, entity.Orientation.MIX.value]),
    StateFilter(entity.UserState.UPLOADING, entity.UserState.CHOOSE_TO),
)
async def create_pdf(message: types.Message, state: FSMContext, api_service: ApiService):
    """Создаёт PDF из всех загруженных изображений после выбора ориентации."""
    _state = TypeAdapter(entity.UserData).validate_python((await state.get_data()))
    if not _state.images:
        await message.answer("❌ Ты не отправил ни одного изображения!")
        return

    _state.orientation = message.text
    pdf_bytes = await api_service.convert(
        _state.from_format,
        _state.to_format,
        _state.model_dump(include={"orientation", "images"})
    )

    formats = await api_service.get_formats()
    keyboard = get_markup_keyboard([format.name for format in formats])

    await state.update_data(entity.UserData().model_dump())
    await state.set_state(entity.UserState.START)

    await message.answer_document(
        BufferedInputFile(pdf_bytes, filename="converted.pdf"),
        caption=f"📄 Твой PDF готов! (Ориентация: {_state.orientation})",
        reply_markup=keyboard
    )
