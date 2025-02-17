import asyncio

from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import BufferedInputFile, CallbackQuery

from app import entity
from app.logger import logger
from app.service import ConverterService, ApiService, StateService
from app.utils.keybord import get_markup_keyboard, get_inline_keyboard_by_from_format, get_inline_keyboard

router = Router()
lock = asyncio.Lock()


@router.message(CommandStart())
@router.message(F.text == "Меню")
async def start_handler(message: types.Message, api_service: ApiService, state_service: StateService, user: entity.User):
    formats = await api_service.get_formats_with_pair()
    await state_service.set_default()
    await state_service.set_state(entity.UserState.START)
    keyboard = get_inline_keyboard([format.name for format in formats])
    await api_service.create_user_action(entity.AddUserAction(
        user_id=user.id,
        action_type=entity.ActionType.START,
        comment=None
    ))
    await message.answer("Привет! Выбери формат загружаемого файла:", reply_markup=keyboard)
    await message.answer(".", reply_markup=get_markup_keyboard(["Меню"]))


@router.callback_query(
    entity.UserState.START
)
async def choose_from_format(callback: CallbackQuery, api_service: ApiService, state_service: StateService, user: entity.User):
    formats = await api_service.get_cross_formats_by_format_name(callback.data)
    keyboard = get_inline_keyboard([format.format_to_name for format in formats])
    await state_service.set_from_format(callback.data)
    await state_service.set_state(entity.UserState.CHOOSE_FROM)
    await api_service.create_user_action(entity.AddUserAction(
        user_id=user.id,
        action_type=entity.ActionType.CHOOSE_FROM,
        comment=callback.data
    ))
    await callback.message.answer("Выбери формат желаемого файла", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(
    entity.UserState.CHOOSE_FROM
)
async def choose_to_format(callback: CallbackQuery, api_service: ApiService, state_service: StateService, user: entity.User):
    format_from = await state_service.from_format
    formats = await api_service.get_cross_formats_by_format_name(format_from)
    if callback.data not in [format.format_to_name for format in formats]:
        await callback.answer(f"❌ Выбранный формат не поддерживается для конвертации из {format_from}!")
        return

    await state_service.set_to_format(callback.data)
    await state_service.set_state(entity.UserState.CHOOSE_TO)
    await api_service.create_user_action(entity.AddUserAction(
        user_id=user.id,
        action_type=entity.ActionType.CHOOSE_TO,
        comment=callback.data
    ))
    await callback.message.answer("Отправь файл для конвертации в PDF.")
    await callback.answer()


@router.message(
    (F.photo |
     (F.document &
      (
        F.document.mime_type.startswith("image/") |
        F.document.file_name.endswith(".docx") |
        F.document.file_name.endswith(".pptx") |
        F.document.file_name.endswith(".xlsx") |
        F.document.file_name.endswith(".html")
      )
      )
     ),
    StateFilter(entity.UserState.CHOOSE_TO),
)
async def collect_files(
        message: types.Message,
        api_service: ApiService,
        convert_service: ConverterService,
        state_service: StateService,
        user: entity.User
):
    """Сохраняет изображения в список для текущего пользователя."""
    async with lock:
        from_format = await state_service.from_format
        check = await convert_service.check_message_by_format(message, from_format)
        if not check:
            await message.answer("❌ Ты отправил файл с неверным расширением!")
            return

        file = await convert_service.download_file_from_message(message)
        await state_service.add_file(file)

        keyboard = get_inline_keyboard_by_from_format(from_format)

        await api_service.create_user_action(entity.AddUserAction(
            user_id=user.id,
            action_type=entity.ActionType.UPLOADING,
            comment=None
        ))
        text = "✅ Файл отправлен! Нажми готово для конвертации."
        if from_format == "jpg":
            text = "✅ Файл отправлен! Отправь ещё или выберите ориентацию страниц для конвертации."
        await message.answer(text, reply_markup=keyboard)


@router.callback_query(
    F.data.in_([
        entity.Orientation.LANDSCAPE.value,
        entity.Orientation.PORTRAIT.value,
        entity.Orientation.MIX.value,
        entity.Button.READY.value,
    ]),
    StateFilter(entity.UserState.CHOOSE_TO),
)
async def convert_files(callback: CallbackQuery, api_service: ApiService, state_service: StateService, user: entity.User):
    """Создаёт PDF из всех загруженных изображений после выбора ориентации."""
    if not (await state_service.files):
        await callback.answer("❌ Ты не отправил ни одного файла!")
        return

    await state_service.set_orientation(callback.data)
    state = await state_service.get_user_state()
    pdf_bytes = await api_service.convert(
        state.from_format,
        state.to_format,
        state.model_dump()
    )

    await state_service.set_default()
    orientation = f" (Ориентация: {state.orientation})" if state.orientation else ""

    await api_service.create_user_action(entity.AddUserAction(
        user_id=user.id,
        action_type=entity.ActionType.GOT_RESULT,
        comment=None
    ))
    text = (f"📄 Твой PDF готов!{orientation}\n"
            f"Спасибо что воспользовались нашим сервисом. Для продолжения работа выберите соответствующий пункт меню.")
    await callback.message.answer_document(
        BufferedInputFile(pdf_bytes, filename="converted.pdf"),
        caption=text,
        reply_markup=get_markup_keyboard(["Меню"])
    )
    await callback.answer()
