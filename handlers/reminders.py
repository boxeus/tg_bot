from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from keyboards.keyboards import kb_remind_notes, kb_empty_remind_notes, kb_delete_remind_notes, kb_back_to_remind_menu
from database.database import add_reminder, get_reminder_once, delete_reminder, get_remind_notes, get_reminder_daily
from scheduler import scheduler
from bot import bot

from datetime import datetime
from zoneinfo import ZoneInfo


router = Router()
calendar = SimpleCalendar()

#---------------------------------------------Состоняния--------------------------------------------------
class ReminderState(StatesGroup):
    # Once
    text = State()           #состояние для ввода текста
    date = State()           #состояние для ввода даты
    time = State()           #состояние для ввода времени
    #Daily
    daily_text = State()
    daily_time = State()
    #delete_reminer
    delete_once = State()
    delete_daily = State()
#------------------------------------------- главное меню напоминаний --------------------------------------------
@router.callback_query(F.data == "remind_notes")
async def remind_notes(callback : CallbackQuery):
    await callback.message.edit_text(text="Напоминания", reply_markup=kb_remind_notes)

#==================================================================================================================
#------------------------------------отработка кнопки одноразовое напоминание --------------------------------------
#==================================================================================================================

@router.callback_query(F.data == "once_reminder")
#состояния text
async def once_reminder(callback: CallbackQuery, state : FSMContext):
    await state.set_state(ReminderState.text)
    await callback.message.answer("Введи текст напоминания:")

@router.message(ReminderState.text)
#сохранение текста в FSM/смена состояние text->date
async def once_reminder_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(ReminderState.date)
    await message.answer("Выбери дату:", reply_markup=await calendar.start_calendar())

@router.callback_query(SimpleCalendarCallback.filter(), ReminderState.date)
#сохр. даты в FSM/смена состоян date->time
async def once_reminder_date(callback : CallbackQuery, state: FSMContext, callback_data: SimpleCalendarCallback):
    selected, date=await calendar.process_selection(callback,callback_data)
    if selected:
        await state.update_data(date = date.strftime("%d.%m.%Y"))
        await state.set_state(ReminderState.time)
        await callback.message.edit_text("Введите время в формате ЧЧ:ММ\n\nНапример: 06:35")


@router.message(ReminderState.time)
#перенос данных FSM->db/конец состояния
async def once_reminder_time(message: Message, state: FSMContext):
    if not check_time(message.text):          #функция проверки ввода времени
        await message.answer("Введи время в правильном формате:")
        return
    hours, minutes = message.text.split(":")

    time = f"{int(hours):02}:{int(minutes):02}"

    await state.update_data(time=time)
    # await state.update_data(time=message.text)

    user_data = await state.get_data()
    user_id = message.from_user.id
    reminder_text = user_data.get("text")
    reminder_date = user_data.get("date")
    reminder_time = user_data.get("time")
    reminder_type = "once"
    add_reminder(user_id, reminder_text, reminder_type, reminder_date, reminder_time)
    await state.clear()
    await message.answer("Напоминание успешно создано ✅",reply_markup=kb_remind_notes)




#==================================================================================================================
#------------------------------------отработка кнопки ежедневное напоминание --------------------------------------
#==================================================================================================================

@router.callback_query(F.data == "daily_reminder")
async def daily_reminder(callback: CallbackQuery, state : FSMContext):
    await state.set_state(ReminderState.daily_text)
    await callback.message.answer("Введи текст напоминания:")


@router.message(ReminderState.daily_text)
async def daily_reminder_text(message: Message, state: FSMContext):
    await state.update_data(text = message.text)
    await state.set_state(ReminderState.daily_time)
    await message.answer("Введите время в формате ЧЧ:ММ\n\nНапример: 06:35")

@router.message(ReminderState.daily_time)
async def daily_reminder_time(message: Message, state: FSMContext):
    if not check_time(message.text):          #функция проверки ввода времени
        await message.answer("Введи время в правильном формате:")
        return
    hours, minutes = message.text.split(":")

    time = f"{int(hours):02}:{int(minutes):02}"

    await state.update_data(time=time)
    # await state.update_data(time=message.text)
    user_data = await state.get_data()
    user_id = message.from_user.id
    reminder_text = user_data.get("text")
    reminder_time = user_data.get("time")
    reminder_type = "daily"
    reminder_date = None
    add_reminder(user_id, reminder_text, reminder_type, reminder_date, reminder_time)
    await state.clear()
    await message.answer("Напоминание успешно создано ✅",reply_markup=kb_remind_notes)


#==================================================================================================================
#------------------------------------  отработка кнопки мои напоминания   -----------------------------------------
#==================================================================================================================

@router.callback_query(F.data == "check_reminders")
async def check_reminders_notes(callback: CallbackQuery):
    user_id = callback.from_user.id
    notes = get_remind_notes(user_id)
    result = []
    if not notes:
        await callback.message.edit_text("Твои напоминания пустые, выбери какое хочешь добавить",
                                         reply_markup=kb_empty_remind_notes)
        return
    once_result = [note for note in notes if note[2] == "once"]
    daily_result = [note for note in notes if note[2] == "daily"]
    if once_result:
        result.append("📅 Одноразовые напоминания\n")

        for index, note in enumerate(once_result, start=1):
            result.append(
                f"{index}. {note[1]}\n"
                f"📆 {note[3]}\n"
                f"🕐 {note[4]}\n"
            )

    if daily_result:
        result.append("\n🔁 Ежедневные напоминания\n")

        for index, note in enumerate(daily_result, start=1):
            result.append(
                f"{index}. {note[1]}\n"
                f"🕐 {note[4]}\n"
            )

    await callback.message.edit_text("\n".join(result), reply_markup=kb_back_to_remind_menu)


#----------------------отработка кнопки назад в меню напоминаний из моих напоминаний ------------
@router.callback_query(F.data=="back_to_remind_menu")
async def back_to_reminders_menu(callback: CallbackQuery):
    await callback.message.edit_text(text="Напоминания", reply_markup=kb_remind_notes)

#==================================================================================================================
#------------------------------------  отработка кнопки удалить напоминание   -------------------------------------
#==================================================================================================================

@router.callback_query(F.data == "delete_reminder")
async def delete_reminder_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    notes = get_remind_notes(user_id)
    result = []
    if not notes:
        await callback.message.edit_text("Твои напоминания пустые, сначала добавь",
                                         reply_markup=kb_empty_remind_notes)
        return
    once_result = [note for note in notes if note[2] == "once"]
    daily_result = [note for note in notes if note[2] == "daily"]
    if once_result:
        result.append("📅 Одноразовые напоминания\n")

        for index, note in enumerate(once_result, start=1):
            result.append(
                f"{index}. {note[1]}\n"
                f"📆 {note[3]}\n"
                f"🕐 {note[4]}\n"
            )

    if daily_result:
        result.append("\n🔁 Ежедневные напоминания\n")

        for index, note in enumerate(daily_result, start=1):
            result.append(
                f"{index}. {note[1]}\n"
                f"🕐 {note[4]}\n"
            )
    await callback.message.edit_text("\n".join(result), reply_markup=kb_delete_remind_notes)
    await callback.message.answer("Какое уведомление ты хочешь удалить?")
#---------------------удаление once напоминаний----------------
@router.callback_query(F.data=="once_delete_reminder")
async def delete_once_remind(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    notes = get_remind_notes(user_id)
    result = []
    if not notes:
        await callback.message.edit_text("Твои напоминания пустые, сначала добавь",
                                         reply_markup=kb_empty_remind_notes)
        return
    once_result = [note for note in notes if note[2] == "once"]
    if not once_result:
        await callback.message.answer("Одноразовых напоминаний у тебя нет.")
        return
    result.append("📅 Одноразовые напоминания\n")

    for index, note in enumerate(once_result, start=1):
        result.append(
            f"{index}. {note[1]}\n"
            f"📆 {note[3]}\n"
            f"🕐 {note[4]}\n"
        )
    await state.set_state(ReminderState.delete_once)
    await callback.message.answer(
        "\n".join(result) +"\n\nВведите номер удаляемого уведомления:")

@router.message(ReminderState.delete_once)
async def delete_once_reminder(message: Message, state: FSMContext):
    user_id = message.from_user.id
    notes = get_remind_notes(user_id)
    once_result = [note for note in notes if note[2] == "once"]
    if not message.text.isdigit():
        await message.answer("Введи номер правильно.")
        return
    elif (int(message.text) - 1) not in range(len(once_result)):
        await message.answer("Напоминания с таким номером не существует.")
        return
    reminder_id = once_result[int(message.text) - 1][0]
    delete_reminder(reminder_id)
    await message.answer("Напоминание успешно удалено ✅",reply_markup=kb_remind_notes)
    await state.clear()
#---------------------удаление daily напоминаний----------------
@router.callback_query(F.data =="daily_delete_reminder")
async def delete_daily_reminder(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    notes = get_remind_notes(user_id)
    result = []
    if not notes:
        await callback.message.edit_text("Твои напоминания пустые, сначала добавь",
                                         reply_markup=kb_empty_remind_notes)
        return
    daily_result = [note for note in notes if note[2] == "daily"]
    if not daily_result:
        await callback.message.answer("Ежедневных напоминаний у тебя нет.")
        return
    result.append("🔁 Ежедневные напоминания\n")

    for index, note in enumerate(daily_result, start=1):
        result.append(
            f"{index}. {note[1]}\n"
            f"🕐 {note[4]}\n"
        )
    await state.set_state(ReminderState.delete_daily)
    await callback.message.answer(
        "\n".join(result) + "\n\nВведите номер удаляемого уведомления:")

@router.message(ReminderState.delete_daily)
async def delete_daily_reminder(message: Message, state: FSMContext):
    user_id = message.from_user.id
    notes = get_remind_notes(user_id)
    daily_result = [note for note in notes if note[2] == "daily"]
    if not message.text.isdigit():
        await message.answer("Введи номер правильно.")
        return
    elif (int(message.text) - 1) not in range(len(daily_result)):
        await message.answer("Напоминания с таким номером не существует.")
        return
    reminder_id = daily_result[int(message.text) - 1][0]
    delete_reminder(reminder_id)
    await message.answer("Напоминание успешно удалено ✅", reply_markup=kb_remind_notes)
    await state.clear()
#-------------------------------------------Планировщик напоминаний-----------------------------------------------

async def check_reminders():
    now = datetime.now(ZoneInfo("Europe/Kyiv")) # Часовой пояс (если на сервере время отличается)
    reminders = get_reminder_once()                  #вызываем функцию с database.py
    for remind in reminders:
        reminder_id = remind[0]
        user_id = remind[1]
        text = remind[2]
        reminder_date = remind[4]
        reminder_time = remind[5]
        today = now.strftime("%d.%m.%Y")
        current_time = now.strftime("%H:%M")
        if reminder_date == today and reminder_time == current_time:
            await bot.send_message(chat_id=user_id,text=text)
            delete_reminder(reminder_id)

    reminders = get_reminder_daily()
    for remind in reminders:
        user_id = remind[1]
        text = remind[2]
        reminder_time = remind[5]
        current_time = now.strftime("%H:%M")
        if reminder_time == current_time:
            await bot.send_message(chat_id=user_id, text=text)

scheduler.add_job(check_reminders,trigger="interval",minutes=1)   #каждую минуту вызывает check_reminders()

#--------------------------------функция проверки ввода времени---------------------------------------------
def check_time(time: str):
    if ":" not in time:
        return False
    hours, minutes = time.split(":")

    if not hours.isdigit() or not minutes.isdigit():
        return False
    hours = int(hours)
    minutes = int(minutes)

    if hours not in range(24) or minutes not in range(60):
        return False
    return True