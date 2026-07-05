from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database.database import add_note_db, get_notes, delete_note_db


from keyboards.keyboards import kb, kb_notes, kb_back, kb_empty_notes

router = Router()
# all_notes = {}    #временная база данных - тут хранятся заметки...

#==================================================================================================================
#------------------------------------ отработка базовой команды старт ---------------------------------------------
#==================================================================================================================

@router.message(Command("start"))
async def start (message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Главное меню", reply_markup=kb)

#==================================================================================================================
#------------------------------------------ отработка кнопки INFO -------------------------------------------------
#==================================================================================================================

@router.callback_query(F.data == "info")
async def info_bot(callback: CallbackQuery):
    await callback.message.edit_text("""
                Добро пожаловать в Lead Team Manager Bot! 👋
        
        Этот бот поможет не забывать о важных задачах и держать всю работу в одном месте.
        
        📌 Заметки
        Создавайте, просматривайте и удаляйте заметки. Здесь можно хранить:
        • идеи;
        • задачи;
        • контакты;
        • напоминания самому себе;
        • любую важную информацию, которую не хочется потерять.
        
        ⏰ Напоминания
        Бот поддерживает два типа напоминаний:
        
        • Одноразовые — сработают один раз в указанную дату и время.
        • Ежедневные — будут повторяться каждый день в выбранное время."""
        # • Еженедельные — будут приходить в выбранные дни недели. (на данный момент отсутствуют без надобности)
        
        """"💡 Рекомендуем включить автоудаление сообщений.
        
        Для этого:
        • нажмите ПКМ по чату с ботом;
        • выберите «Очистить историю»;
        • нажмите «Настроить автоудаление»;
        • выберите удобный период.
        
        Это позволит автоматически очищать чат от старых сообщений. При этом все ваши заметки и 
        напоминания останутся сохранены в базе данных бота.
    """,  reply_markup=kb_back)

#==================================================================================================================
#------------------------------------------ отработка кнопки заметки ----------------------------------------------
#==================================================================================================================

@router.callback_query(F.data == "notes")
async def notes(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(text = "Заметки", reply_markup=kb_notes)


#==================================================================================================================
#------------------------------------отработка кнопки Назад в меню заметок-----------------------------------------
#==================================================================================================================

@router.callback_query(F.data == "back_to_menu")
async def back_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(text ="Главное меню", reply_markup=kb)

#---------------------------------------------------Класс состояний----------------------------------------------------
class NotesState(StatesGroup):
    add_note = State()
    delete_note = State()

#==================================================================================================================
#------------------------------------Отработка кнопки Добавление заметок-------------------------------------------
#==================================================================================================================

@router.callback_query(F.data == "add_note")
async def add_note(callback: CallbackQuery, state: FSMContext):
    await state.set_state(NotesState.add_note)
    await  callback.message.edit_text("Введи заметку:")

@router.message(NotesState.add_note)
async def save_note(message: Message, state: FSMContext):

    user_id = message.from_user.id
    note = message.text

    add_note_db(user_id, note)     #функция из database.py - добавление заметок в базу

    await message.answer("Заметка успешно сохранена ✅\n\nЗаметки",reply_markup=kb_notes)
    await state.clear()


#==================================================================================================================
#------------------------------------Отработка кнопки показа всех заметок------------------------------------------
#==================================================================================================================

@router.callback_query(F.data == "check_notes")
async def check_notes(callback: CallbackQuery):
    user_id = callback.from_user.id
    db_notes = get_notes(user_id)
    result = []
    if not db_notes:
        await callback.message.edit_text("Твои заметки пустые", reply_markup=kb_empty_notes)
        return
    else:
        for index, value in enumerate(db_notes, start = 1):
            result.append(f"{index}: {value[-1]}")
        await callback.message.edit_text("\n".join(result), reply_markup=kb_empty_notes)
#-------------------------------------------отработка кнопки назад в меню мои заметки-------------------------------
@router.callback_query(F.data == "back_to_notes")
async def back_to_notes(callback: CallbackQuery):
    await callback.message.edit_text(text="Заметки", reply_markup=kb_notes)


#==================================================================================================================
#------------------------------------Отработка кнопки удаление заметок---------------------------------------------
#==================================================================================================================

@router.callback_query(F.data == "delete_note")
async def delete_notes(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    db_notes = get_notes(user_id)
    result = []
    if not db_notes:
        await callback.message.answer("Твои заметки пустые", reply_markup= kb_empty_notes)
        return
    else:
        for index, value in enumerate(db_notes, start = 1):
            result.append(f"{index}: {value[-1]}")
        await state.set_state(NotesState.delete_note)
        await callback.message.answer(f"Твои заметки:\n\n{"\n".join(result)}\n\n"
                                      f"Введи номер заметки которую хочешь удалить:")

@router.message(NotesState.delete_note)
async def delete_notes_1(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db_notes = get_notes(user_id)
    if not message.text.isdigit():
        await message.answer("Введи число")
        return
    elif (int(message.text) - 1) not in range(len(db_notes)):
        await message.answer("Заметки с таким номером не существует")
    else:
        delete_note_db(db_notes[int(message.text)-1][0])
    await message.answer("Заметка успешно удалена ✅\n\nЗаметки",reply_markup=kb_notes)
    await state.clear()
