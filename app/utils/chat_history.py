from app.config.constants import MAX_CHAT_TURNS


def truncate_history(chat_history):
    max_messages = MAX_CHAT_TURNS * 2
    if len(chat_history) > max_messages:
        return chat_history[-max_messages:]
    return chat_history
