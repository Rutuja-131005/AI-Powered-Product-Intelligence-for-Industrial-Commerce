import json
import os
import time

HISTORY_FILE = "/tmp/history.json" if os.getenv("VERCEL") == "1" else "history.json"

def _load_data():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_data(data):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_all_chats():
    """Returns a list of chat summaries (id, title, timestamp)."""
    data = _load_data()
    # Sort by timestamp descending
    data.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    return [{"id": chat["id"], "title": chat.get("title", "New Chat"), "timestamp": chat.get("timestamp")} for chat in data]

def get_chat(chat_id):
    """Returns the full chat object for a given ID."""
    data = _load_data()
    for chat in data:
        if chat["id"] == chat_id:
            return chat
    return None

def save_chat(chat_id, title, messages):
    """Upserts a chat session."""
    data = _load_data()
    chat_found = False
    
    # Update existing chat
    for chat in data:
        if chat["id"] == chat_id:
            chat["title"] = title
            chat["messages"] = messages
            chat["timestamp"] = int(time.time() * 1000) # Update timestamp on save
            chat_found = True
            break
    
    # Create new chat if not found
    if not chat_found:
        new_chat = {
            "id": chat_id,
            "title": title,
            "messages": messages,
            "timestamp": int(time.time() * 1000)
        }
        data.append(new_chat)
    
    _save_data(data)

def delete_chat(chat_id):
    """Deletes a chat session by ID."""
    data = _load_data()
    initial_len = len(data)
    data = [chat for chat in data if chat["id"] != chat_id]
    
    if len(data) < initial_len:
        _save_data(data)
        return True
    return False
