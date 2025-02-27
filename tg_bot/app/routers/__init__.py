import asyncio

from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import BufferedInputFile, CallbackQuery

from app import entity
from app.logger import logger
from app.service import ConverterService, ApiService, StateService
from app.utils.keybord import get_markup_keyboard, get_inline_keyboard_by_from_format, get_inline_keyboard

router = Router()
lock = asyncio.Lock()


@router.message(CommandStart())
async def start_handler(message: types.Message, api_service: ApiService, state_service: StateService, user: entity.User):
    await state_service.set_default()
    await api_service.create_user_action(entity.AddUserAction(
        user_id=user.id,
        action_type=entity.ActionType.START,
        comment=None
    ))
    await message.answer(
        "Привет! Мы рады, что вы выбрали наш сервис! Здесь вы можете конвертировать файлы различных форматов. "
        "Также мы будем рады вашему отзыву, это позволит нам улучшить сервис. \n\n"
        "Для управления сервисом откройте меню и выберите интересующий вас пункт.",
        reply_markup=get_markup_keyboard([
            entity.Button.CONVERT.value,
            entity.Button.FEEDBACK.value,
            entity.Button.DONAT.value
        ])
    )


@router.message(F.text == entity.Button.CONVERT.value)
@router.message(Command("convert"))
async def convert_handler(message: types.Message, api_service: ApiService, state_service: StateService, user: entity.User):
    formats = await api_service.get_formats_with_pair()
    await state_service.set_default()
    await state_service.set_state(entity.UserState.CONVERT)
    keyboard = get_inline_keyboard([format.name for format in formats])
    await api_service.create_user_action(entity.AddUserAction(
        user_id=user.id,
        action_type=entity.ActionType.CONVERT,
        comment=None
    ))
    await message.answer("Привет! Выбери формат загружаемого файла:", reply_markup=keyboard)


@router.message(F.text == entity.Button.FEEDBACK.value)
@router.message(Command("feedback"))
async def feedback_handler(message: types.Message, state_service: StateService):
    await state_service.set_default()
    await state_service.set_state(entity.UserState.FEEDBACK)
    await message.answer(
        "Напишите и отправьте свой отзыв.",
        reply_markup=get_markup_keyboard([
            entity.Button.CONVERT.value,
            entity.Button.FEEDBACK.value,
            entity.Button.DONAT.value,
        ])
    )


@router.message(F.text == entity.Button.DONAT.value)
@router.message(Command("donat"))
async def donat_handler(message: types.Message, state_service: StateService):
    await state_service.set_default()
    await state_service.set_state(entity.UserState.DONAT)
    await message.answer(
        "Ваша поддержка очень важна для нас. Поддержать развитие проекта можно по адресу кошелька ХХХХХ.",
        reply_markup=get_markup_keyboard([
            entity.Button.CONVERT.value,
            entity.Button.FEEDBACK.value,
            entity.Button.DONAT.value,
        ])
    )


@router.message(entity.UserState.FEEDBACK)
async def send_feedback_handler(message: types.Message, api_service: ApiService, state_service: StateService, user: entity.User):
    await state_service.set_default()
    await api_service.create_feedback(entity.AddFeedback(
        user_id=user.id,
        text=message.text
    ))
    await api_service.create_user_action(entity.AddUserAction(
        user_id=user.id,
        action_type=entity.ActionType.FEEDBACK,
        comment=None
    ))
    await message.answer(
        "Спасибо вам за отзыв, вы помогаете нам улучшить работу сервиса.",
        reply_markup=get_markup_keyboard([entity.Button.CONVERT.value, entity.Button.FEEDBACK.value])
    )


@router.callback_query(
    entity.UserState.CONVERT
)
async def choose_from_format_handler(callback: CallbackQuery, api_service: ApiService, state_service: StateService, user: entity.User):
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
async def choose_to_format_handler(callback: CallbackQuery, api_service: ApiService, state_service: StateService, user: entity.User):
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
    extension = callback.data.upper()
    await callback.message.answer(f"Отправь файл для конвертации в {extension}.")
    await callback.answer()


@router.message(
    (F.photo | F.document),
    StateFilter(entity.UserState.CHOOSE_TO),
)
async def collect_files_handler(
        message: types.Message,
        api_service: ApiService,
        convert_service: ConverterService,
        state_service: StateService,
        user: entity.User
):
    """Сохраняет изображения в список для текущего пользователя."""
    async with lock:
        from_format = await state_service.from_format
        to_format = await state_service.to_format
        check = await convert_service.check_message_by_format(message, from_format)
        if not check:
            await message.answer("❌ Ты отправил файл с неверным расширением!")
            return

        file = await convert_service.download_file_from_message(message)
        await state_service.add_file(file)

        keyboard = get_inline_keyboard_by_from_format(from_format, to_format)

        await api_service.create_user_action(entity.AddUserAction(
            user_id=user.id,
            action_type=entity.ActionType.UPLOADING,
            comment=None
        ))
        files = await state_service.files
        text = "✅ Файл отправлен! Нажми готово для конвертации."
        if from_format == "jpg":
            text = f"✅ Отправлено {len(files)} файлов! Отправь ещё или нажми готово для конвертации."
            if to_format == "pdf":
                text = f"✅ Отправлено {len(files)} файлов! Отправь ещё или выберите ориентацию страниц для конвертации."

        if from_format == "jpg" and len(files) > 1:
            last_message = await state_service.last_message
            await convert_service.bot.delete_message(
                chat_id=last_message.chat.id,
                message_id=last_message.message_id,
            )
        message = await message.answer(text, reply_markup=keyboard)
        await state_service.set_last_message(message)


@router.message(
    (~F.photo &
     ~F.document &
     ~F.data.in_([
        entity.Orientation.LANDSCAPE.value,
        entity.Orientation.PORTRAIT.value,
        entity.Orientation.MIX.value,
        entity.Button.READY.value,
    ])),
    StateFilter(entity.UserState.CHOOSE_TO),
)
async def bad_message_handler(message: types.Message):
    """Обработка сообщений с неверным форматом или без файлов"""
    await message.answer("❌ Ты отправил с неверным типом файла или без него!")


@router.callback_query(
    F.data.in_([
        entity.Orientation.LANDSCAPE.value,
        entity.Orientation.PORTRAIT.value,
        entity.Orientation.MIX.value,
        entity.Button.READY.value,
    ]),
    StateFilter(entity.UserState.CHOOSE_TO),
)
async def convert_files_handler(
        callback: CallbackQuery,
        api_service: ApiService,
        convert_service: ConverterService,
        state_service: StateService,
        user: entity.User
):
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
    logger.info(f"{pdf_bytes=}")
    orientation = f" (Ориентация: {state.orientation})" if state.orientation else ""

    await api_service.create_user_action(entity.AddUserAction(
        user_id=user.id,
        action_type=entity.ActionType.GOT_RESULT,
        comment=None
    ))
    text = (f"📄 Твой PDF готов!{orientation}\n"
            f"Спасибо что воспользовались нашим сервисом. Для продолжения работы выберите соответствующий пункт меню.")
    extension = convert_service.get_extension_by_format((await state_service.to_format))
    await state_service.set_default()
    await callback.message.answer_document(
        BufferedInputFile(pdf_bytes, filename=f"converted.{extension}"),
        caption=text,
        reply_markup=get_markup_keyboard([
            entity.Button.CONVERT.value,
            entity.Button.FEEDBACK.value,
            entity.Button.DONAT.value,
        ])
    )
    await callback.answer()
