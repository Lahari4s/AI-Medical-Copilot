from database.db import create_user, login_user

def signup(username, password):
    return create_user(username, password)

def login(username, password):
    return login_user(username, password)