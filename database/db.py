import sqlite3
from datetime import datetime
import bcrypt

DB_PATH = "healthcare_app.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash BLOB NOT NULL,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        role TEXT,
        content TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS food_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        food TEXT,
        ai_feedback TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS health_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        bp TEXT,
        sugar TEXT,
        weight TEXT,
        sleep TEXT,
        water TEXT,
        steps TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def create_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, hashed, datetime.now().isoformat())
        )
        conn.commit()
        return True, "Account created successfully"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    finally:
        conn.close()

def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()

    if row:
        user_id, stored_hash = row
        if bcrypt.checkpw(password.encode(), stored_hash):
            return True, user_id

    return False, None
# ---------------- CHAT FUNCTIONS ----------------

def create_chat(user_id, title="New Chat"):
    conn = get_connection()
    cur = conn.cursor()

    now = datetime.now().isoformat()

    cur.execute(
        """
        INSERT INTO chats (user_id, title, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, title, now, now)
    )

    conn.commit()

    chat_id = cur.lastrowid

    conn.close()

    return chat_id


def get_user_chats(user_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, title, updated_at
        FROM chats
        WHERE user_id=?
        ORDER BY updated_at DESC
        """,
        (user_id,)
    )

    chats = cur.fetchall()

    conn.close()

    return chats


def rename_chat(chat_id, new_title):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        UPDATE chats
        SET title=?, updated_at=?
        WHERE id=?
        """,
        (
            new_title,
            datetime.now().isoformat(),
            chat_id
        )
    )

    conn.commit()

    conn.close()


def delete_chat(chat_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM messages WHERE chat_id=?",
        (chat_id,)
    )

    cur.execute(
        "DELETE FROM chats WHERE id=?",
        (chat_id,)
    )

    conn.commit()

    conn.close()


# ---------------- MESSAGE FUNCTIONS ----------------

def add_message(chat_id, role, content):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO messages
        (chat_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            chat_id,
            role,
            content,
            datetime.now().isoformat()
        )
    )

    cur.execute(
        """
        UPDATE chats
        SET updated_at=?
        WHERE id=?
        """,
        (
            datetime.now().isoformat(),
            chat_id
        )
    )

    conn.commit()

    conn.close()


def get_messages(chat_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT role, content
        FROM messages
        WHERE chat_id=?
        ORDER BY id ASC
        """,
        (chat_id,)
    )

    rows = cur.fetchall()

    conn.close()

    return [
        {
            "role": row[0],
            "content": row[1]
        }
        for row in rows
    ]


# ---------------- FOOD TRACKER ----------------

def save_food_log(user_id, food, ai_feedback):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO food_logs
        (user_id, food, ai_feedback, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            food,
            ai_feedback,
            datetime.now().isoformat()
        )
    )

    conn.commit()

    conn.close()


def get_food_logs(user_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT food, ai_feedback, created_at
        FROM food_logs
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    logs = cur.fetchall()

    conn.close()

    return logs


# ---------------- HEALTH TRACKING ----------------

def save_health_log(
    user_id,
    bp,
    sugar,
    weight,
    sleep,
    water,
    steps
):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO health_logs
        (
            user_id,
            bp,
            sugar,
            weight,
            sleep,
            water,
            steps,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            bp,
            sugar,
            weight,
            sleep,
            water,
            steps,
            datetime.now().isoformat()
        )
    )

    conn.commit()

    conn.close()


def get_health_logs(user_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
        bp,
        sugar,
        weight,
        sleep,
        water,
        steps,
        created_at
        FROM health_logs
        WHERE user_id=?
        ORDER BY id ASC
        """,
        (user_id,)
    )

    rows = cur.fetchall()

    conn.close()

    return rows
# ---------------- REPORT STORAGE ----------------

def save_report(
    user_id,
    chat_id,
    report_text,
    analysis
):

    conn = get_connection()

    cur = conn.cursor()

    # Create reports table if not exists

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        chat_id INTEGER,
        report_text TEXT,
        analysis TEXT,
        created_at TEXT
    )
    """)

    cur.execute(
        """
        INSERT INTO reports
        (
            user_id,
            chat_id,
            report_text,
            analysis,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            chat_id,
            report_text,
            analysis,
            datetime.now().isoformat()
        )
    )

    conn.commit()

    conn.close()


def get_reports(user_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
        report_text,
        analysis,
        created_at
        FROM reports
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    rows = cur.fetchall()

    conn.close()

    return rows
# ---------------- MEDICINE REMINDERS ----------------

def add_reminder(
    user_id,
    medicine,
    dosage,
    timing
):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        medicine TEXT,
        dosage TEXT,
        timing TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    cur.execute(
        """
        INSERT INTO reminders
        (
            user_id,
            medicine,
            dosage,
            timing,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            medicine,
            dosage,
            timing,
            "Active",
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_reminders(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        medicine TEXT,
        dosage TEXT,
        timing TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    cur.execute(
        """
        SELECT medicine, dosage, timing, status
        FROM reminders
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    rows = cur.fetchall()

    conn.close()

    return rows