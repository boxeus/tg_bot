import sqlite3


#---------------------------------создание/конект с базами ----------------------------------------------------------

def create_database():
    conn = sqlite3.connect("database/database.db")
    cur = conn.cursor()
    # Создать таблицу заметок
    cur.execute("""CREATE TABLE IF NOT EXISTS notes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    note TEXT
    )
    """)
    # Создать таблицу напоминаний
    cur.execute("""CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT,
        reminder_type TEXT, 
        remind_date TEXT,
        remind_time TEXT,
        weekday TEXT)
        """)

    conn.commit() # нужен ли он ? не помешает)))
    conn.close()


#----------------------------------БАЗА ДЛЯ ЗАМЕТОК---------------------------------------------------


#---------------------------------добавление в базу данных-----------------------------------------------
def add_note_db(user_id, note):
    conn = sqlite3.connect("database/database.db")
    cur = conn.cursor()
    cur.execute("""INSERT INTO notes(user_id, note)
    VALUES (?, ?)""", (user_id, note))
    conn.commit()
    conn.close()

#------------------------------------------------показ заметок----------------------------------------------
def get_notes(user_id):
    conn = sqlite3.connect("database/database.db")
    cur = conn.cursor()
    cur.execute("""SELECT id, note
    FROM notes
    WHERE user_id = ? 
    """,
    (user_id,))
    notes = cur.fetchall()
    conn.close()
    return notes


#---------------------------------------------удаление заметок----------------------------------------------------
def delete_note_db(id_note):
    conn = sqlite3.connect("database/database.db")
    cur = conn.cursor()
    cur.execute("""DELETE FROM notes
    WHERE id = ?
    """, (id_note,))
    conn.commit()
    conn.close()



#----------------------------------БАЗА ДЛЯ НАПОМИНАНИЙ-----------------------------------------------------------

#==================================================================================================================
#------------------------------------добавление  напоминаний-----------------------------------------------------
#==================================================================================================================

def add_reminder(user_id, reminder_text, reminder_type, reminder_date, reminder_time):
    conn = sqlite3.connect("database/database.db")
    cur = conn.cursor()
    cur.execute("""INSERT INTO reminders(
    user_id,
    text,
    reminder_type,
    remind_date,
    remind_time
    )   
    VALUES (?, ?, ?, ?, ?)""", (user_id, reminder_text, reminder_type, reminder_date, reminder_time))
    conn.commit()
    conn.close()
#--------------------------------------Показ одноразовых напоминаний------------------------------------------------
def get_reminder_once():
    conn = sqlite3.connect("database/database.db")
    cur = conn.cursor()
    cur.execute("""SELECT * FROM reminders
    WHERE reminder_type = ?
    """, ("once",))
    reminders = cur.fetchall()
    conn.close()
    return reminders

def get_reminder_daily():
    conn = sqlite3.connect("database/database.db")
    cur = conn.cursor()
    cur.execute("""SELECT * FROM reminders
    WHERE reminder_type = ?
    """, ("daily",))
    reminders = cur.fetchall()
    conn.close()
    return reminders

#функция для удаления из базы напоминаний после отработки-- или удаление ежедневных напоминаний
def delete_reminder(reminder_id):
    conn = sqlite3.connect("database/database.db")
    cur = conn.cursor()
    cur.execute("""DELETE FROM reminders
    WHERE id = ?
    """, (reminder_id,))
    conn.commit()
    conn.close()

#-----------------------------------показ всех напоминаний------------------------------------------------

def get_remind_notes(user_id):
    conn = sqlite3.connect("database/database.db")
    cur = conn.cursor()
    cur.execute("""SELECT id, text, reminder_type, remind_date, remind_time
    FROM reminders
    WHERE user_id = ?
    """, (user_id,))
    notes = cur.fetchall()
    conn.close()
    return notes