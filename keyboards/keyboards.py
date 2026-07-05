from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

#==================================================================================================================
#--------------------------------------------  Кнопки Заметок   ---------------------------------------------------
#==================================================================================================================
kb = InlineKeyboardMarkup(                                       #кнопки базового меню (Заметки/INFO)
    inline_keyboard=[
        [InlineKeyboardButton(text = "Заметки", callback_data= "notes")],
        [InlineKeyboardButton(text = "Напоминания", callback_data= "remind_notes")],
        [InlineKeyboardButton(text = "INFO", callback_data= "info")]
    ]
)

kb_notes = InlineKeyboardMarkup(                                                    #кнопки главного меню -  Заметки
    inline_keyboard=[
        [InlineKeyboardButton(text="Просмотреть заметки", callback_data="check_notes")],
        [InlineKeyboardButton(text="Добавить заметку", callback_data="add_note")],
        [InlineKeyboardButton(text="Удалить заметку", callback_data="delete_note")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
    ]
)

kb_back = InlineKeyboardMarkup(                              #Кнопка назад
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
    ]
)

kb_empty_notes = InlineKeyboardMarkup(                      #кнопка отрабоки когда нажал на посмотреть заметки а их нет
    inline_keyboard=[
        [InlineKeyboardButton(text="Добавить заметку", callback_data ="add_note")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_notes")]
    ]
)

#==================================================================================================================
#------------------------------------  Кнопки Напоминаний   -------------------------------------------------------
#==================================================================================================================


kb_remind_notes = InlineKeyboardMarkup(                        #кнопки главного меню напоминаний
    inline_keyboard=[
        [InlineKeyboardButton(text="Одноразовое напоминание",callback_data="once_reminder")],
        [InlineKeyboardButton(text="Ежедневное напоминание",callback_data="daily_reminder")],
        [InlineKeyboardButton(text="Мои напоминания",callback_data="check_reminders")],
        [InlineKeyboardButton(text="Удалить напоминание",callback_data="delete_reminder")],
        [InlineKeyboardButton(text="Назад",callback_data="back_to_menu")]
    ]
)
# [InlineKeyboardButton(text="Еженедельное напоминание", callback_data="weekly_reminder")] - добавлю если будет нужным

kb_empty_remind_notes = InlineKeyboardMarkup( #клавиатура для добавление напоминаний при их отсутствии.
    inline_keyboard=[
        [InlineKeyboardButton(text="Одноразовое напоминание", callback_data="once_reminder")],
        [InlineKeyboardButton(text="Ежедневное напоминание", callback_data="daily_reminder")],
        [InlineKeyboardButton(text="Назад",callback_data="back_to_remind_menu")]
    ]
)

kb_delete_remind_notes = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Одноразовое напоминание", callback_data="once_delete_reminder")],
        [InlineKeyboardButton(text="Ежедневное напоминание", callback_data="daily_delete_reminder")]
    ]
)

kb_back_to_remind_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад",callback_data="back_to_remind_menu")]
    ]
)