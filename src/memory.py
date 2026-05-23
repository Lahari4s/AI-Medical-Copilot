from database.db import add_message, get_messages

def save_chat_message(chat_id, role, content):
    add_message(chat_id, role, content)

def load_chat_messages(chat_id):
    return get_messages(chat_id)