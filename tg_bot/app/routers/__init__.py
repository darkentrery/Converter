import asyncio

from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import BufferedInputFile, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery

from app import entity
from app.logger import logger
from app.service import ConverterService, ApiService, StateService
from app.utils.keybord import get_markup_keyboard, get_inline_keyboard_by_from_format, get_inline_keyboard

router = Router()
lock = asyncio.Lock()


@router.message(CommandStart())
@router.message(F.text == "Меню")
async def start_handler(message: types.Message, api_service: ApiService, state_service: StateService):
    formats = await api_service.get_formats()
    await state_service.set_default()
    await state_service.set_state(entity.UserState.START)
    keyboard = get_inline_keyboard([format.name for format in formats])
    await message.answer("Привет! Выбери формат загружаемого файла:", reply_markup=keyboard)
    await message.answer(".", reply_markup=get_markup_keyboard(["Меню"]))


@router.callback_query(
    # F.text.in_(["jpg"]),
    entity.UserState.START
)
async def choose_from_format(callback: CallbackQuery, api_service: ApiService, state_service: StateService):
    formats = await api_service.get_cross_formats_by_format_name(callback.data)
    keyboard = get_inline_keyboard([format.format_to_name for format in formats])
    await state_service.set_from_format(callback.data)
    await state_service.set_state(entity.UserState.CHOOSE_FROM)
    # await callback.bot.send_message(callback.from_user.id, "Выбери формат желаемого файла", reply_markup=keyboard)
    await callback.message.answer("Выбери формат желаемого файла", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(
    # F.text.in_(["pdf"]),
    entity.UserState.CHOOSE_FROM
)
async def choose_to_format(callback: CallbackQuery, state_service: StateService):
    keyboard = get_inline_keyboard_by_from_format((await state_service.from_format))
    await state_service.set_to_format(callback.data)
    await state_service.set_state(entity.UserState.CHOOSE_TO)
    # await callback.bot.send_message(callback.from_user.id, "Отправь изображения для конвертации в PDF.", reply_markup=keyboard)
    await callback.message.answer("Отправь изображения для конвертации в PDF.", reply_markup=keyboard)
    await callback.answer()


@router.message(
    (F.photo |
     (F.document &
      (
        F.document.mime_type.startswith("image/") |
        F.document.file_name.endswith(".docx") |
        F.document.file_name.endswith(".xlsx") |
        F.document.file_name.endswith(".html")
      )
      )
     ),
    StateFilter(entity.UserState.CHOOSE_TO),
)
async def collect_files(message: types.Message, convert_service: ConverterService, state_service: StateService):
    """Сохраняет изображения в список для текущего пользователя."""
    async with lock:
        file = await convert_service.download_file_from_message(message)
        logger.info(f"{len(await state_service.files)=}")
        await state_service.add_file(file)
        from_format = await state_service.from_format

        keyboard = get_inline_keyboard_by_from_format((await state_service.from_format))
        await message.answer(
            "✅ Изображение добавлено! Отправь ещё или выберите ориентацию страниц для конвертации.",
            reply_markup=keyboard
        )


# @router.message(
#     (F.document & F.document.mime_type.contains("word") & F.document.file_name.endswith(".docx")),
#     StateFilter(entity.UserState.CHOOSE_TO),
# )
# async def collect_files(message: types.Message, state: FSMContext, convert_service: ConverterService):
#     """Сохраняет изображения в список для текущего пользователя."""
#     _state = TypeAdapter(entity.UserData).validate_python((await state.get_data()))
#     file = await convert_service.download_file_from_message(message)
#     _state.files.append(file)
#     await state.update_data(_state.model_dump())
#
#     match _state.from_format:
#         case "word":
#             keyboard = get_markup_keyboard([
#                 entity.Button.READY.value
#             ])
#         case "jpd":
#             keyboard = get_markup_keyboard([
#                 entity.Orientation.LANDSCAPE.value,
#                 entity.Orientation.PORTRAIT.value,
#                 entity.Orientation.MIX.value
#             ])
#         case _:
#             keyboard = get_markup_keyboard([
#                 entity.Button.READY.value
#             ])
#
#     await message.answer(
#         "✅ Изображение добавлено! Отправь ещё или выберите ориентацию страниц для конвертации.",
#         reply_markup=keyboard
#     )
#
#
# @router.message(
#     (F.document & F.document.mime_type.contains("openxmlformats") & F.document.file_name.endswith(".xlsx")),
#     StateFilter(entity.UserState.CHOOSE_TO),
# )
# async def collect_files(message: types.Message, state: FSMContext, convert_service: ConverterService):
#     """Сохраняет изображения в список для текущего пользователя."""
#     _state = TypeAdapter(entity.UserData).validate_python((await state.get_data()))
#     file = await convert_service.download_file_from_message(message)
#     _state.files.append(file)
#     await state.update_data(_state.model_dump())
#     keyboard = get_markup_keyboard([
#         entity.Button.READY.value
#     ])
#
#     await message.answer(
#         "✅ Изображение добавлено! Отправь ещё или выберите ориентацию страниц для конвертации.",
#         reply_markup=keyboard
#     )
#
#
# @router.message(
#     (F.document & F.document.file_name.endswith(".html")),
#     StateFilter(entity.UserState.CHOOSE_TO),
# )
# async def collect_files(message: types.Message, state: FSMContext, convert_service: ConverterService):
#     """Сохраняет изображения в список для текущего пользователя."""
#     _state = TypeAdapter(entity.UserData).validate_python((await state.get_data()))
#     file = await convert_service.download_file_from_message(message)
#     _state.files.append(file)
#     await state.update_data(_state.model_dump())
#     keyboard = get_markup_keyboard([
#         entity.Button.READY.value
#     ])
#
#     await message.answer(
#         "✅ Изображение добавлено! Отправь ещё или выберите ориентацию страниц для конвертации.",
#         reply_markup=keyboard
#     )


@router.callback_query(
    F.data.in_([
        entity.Orientation.LANDSCAPE.value,
        entity.Orientation.PORTRAIT.value,
        entity.Orientation.MIX.value,
        entity.Button.READY.value,
    ]),
    StateFilter(entity.UserState.CHOOSE_TO),
)
async def convert_files(callback: CallbackQuery, api_service: ApiService, state_service: StateService):
    """Создаёт PDF из всех загруженных изображений после выбора ориентации."""
    if not (await state_service.files):
        await callback.message.answer("❌ Ты не отправил ни одного файла!")
        return

    await state_service.set_orientation(callback.data)
    state = await state_service.get_user_state()
    pdf_bytes = await api_service.convert(
        state.from_format,
        state.to_format,
        state.model_dump()
    )

    formats = await api_service.get_formats()
    keyboard = get_inline_keyboard([format.name for format in formats])

    await state_service.set_default()
    orientation = f" (Ориентация: {state.orientation})" if state.orientation else ""

    await callback.message.answer_document(
        BufferedInputFile(pdf_bytes, filename="converted.pdf"),
        caption=f"📄 Твой PDF готов!" + orientation,
        reply_markup=get_markup_keyboard(["Меню"])
    )
    await callback.message.answer("Привет! Выбери формат загружаемого файла:", reply_markup=keyboard)
