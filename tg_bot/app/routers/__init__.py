import asyncio

from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, ReplyKeyboardMarkup, KeyboardButton
from pydantic import TypeAdapter

from app import entity
from app.logger import logger
from app.service import ConverterService, ApiService
from app.utils.keybord import get_markup_keyboard

router = Router()
lock = asyncio.Lock()


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
async def choose_to_format(message: types.Message, state: FSMContext):
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
    StateFilter(entity.UserState.CHOOSE_TO),
)
async def collect_images(message: types.Message, state: FSMContext, convert_service: ConverterService):
    """Сохраняет изображения в список для текущего пользователя."""
    async with lock:
        _state = TypeAdapter(entity.UserData).validate_python((await state.get_data()))

        file = await convert_service.download_file_from_message(message)
        _state.files.append(file)
        logger.info(f"{len(_state.files)=}")
        await state.update_data(_state.model_dump())

        match _state.from_format:
            case "word":
                keyboard = get_markup_keyboard([
                    entity.Button.READY.value
                ])
            case "jpd":
                keyboard = get_markup_keyboard([
                    entity.Orientation.LANDSCAPE.value,
                    entity.Orientation.PORTRAIT.value,
                    entity.Orientation.MIX.value
                ])
            case _:
                keyboard = get_markup_keyboard([
                    entity.Button.READY.value
                ])
        await message.answer(
            "✅ Изображение добавлено! Отправь ещё или выберите ориентацию страниц для конвертации.",
            reply_markup=keyboard
        )


@router.message(
    (F.document & F.document.mime_type.contains("word") & F.document.file_name.endswith(".docx")),
    StateFilter(entity.UserState.CHOOSE_TO),
)
async def collect_files(message: types.Message, state: FSMContext, convert_service: ConverterService):
    """Сохраняет изображения в список для текущего пользователя."""
    _state = TypeAdapter(entity.UserData).validate_python((await state.get_data()))
    file = await convert_service.download_file_from_message(message)
    _state.files.append(file)
    await state.update_data(_state.model_dump())

    match _state.from_format:
        case "word":
            keyboard = get_markup_keyboard([
                entity.Button.READY.value
            ])
        case "jpd":
            keyboard = get_markup_keyboard([
                entity.Orientation.LANDSCAPE.value,
                entity.Orientation.PORTRAIT.value,
                entity.Orientation.MIX.value
            ])
        case _:
            keyboard = get_markup_keyboard([
                entity.Button.READY.value
            ])

    await message.answer(
        "✅ Изображение добавлено! Отправь ещё или выберите ориентацию страниц для конвертации.",
        reply_markup=keyboard
    )


@router.message(
    (F.document & F.document.mime_type.contains("openxmlformats") & F.document.file_name.endswith(".xlsx")),
    StateFilter(entity.UserState.CHOOSE_TO),
)
async def collect_files(message: types.Message, state: FSMContext, convert_service: ConverterService):
    """Сохраняет изображения в список для текущего пользователя."""
    _state = TypeAdapter(entity.UserData).validate_python((await state.get_data()))
    file = await convert_service.download_file_from_message(message)
    _state.files.append(file)
    await state.update_data(_state.model_dump())
    keyboard = get_markup_keyboard([
        entity.Button.READY.value
    ])

    await message.answer(
        "✅ Изображение добавлено! Отправь ещё или выберите ориентацию страниц для конвертации.",
        reply_markup=keyboard
    )


@router.message(
    F.text.in_([
        entity.Orientation.LANDSCAPE.value,
        entity.Orientation.PORTRAIT.value,
        entity.Orientation.MIX.value,
        entity.Button.READY.value,
    ]),
    StateFilter(entity.UserState.CHOOSE_TO),
)
async def convert_files(message: types.Message, state: FSMContext, api_service: ApiService):
    """Создаёт PDF из всех загруженных изображений после выбора ориентации."""
    _state = TypeAdapter(entity.UserData).validate_python((await state.get_data()))
    if not _state.files:
        await message.answer("❌ Ты не отправил ни одного файла!")
        return

    _state.orientation = message.text
    pdf_bytes = await api_service.convert(
        _state.from_format,
        _state.to_format,
        _state.model_dump()
    )

    formats = await api_service.get_formats()
    keyboard = get_markup_keyboard([format.name for format in formats])

    await state.update_data(entity.UserData().model_dump())
    await state.set_state(entity.UserState.START)
    orientation = f" (Ориентация: {_state.orientation})" if _state.orientation else ""

    await message.answer_document(
        BufferedInputFile(pdf_bytes, filename="converted.pdf"),
        caption=f"📄 Твой PDF готов!" + orientation,
        reply_markup=keyboard
    )
