import os
import atexit
import traceback
import json
from typing import Any, Dict, List, Optional, NamedTuple


def log(message: str):
    print(message, flush=True)


class ChatHistory(NamedTuple):
    user: str
    message: str
    reply_to: Optional[str]


history: Dict[int, List[ChatHistory]] = {}


def is_valid_history_json(h: Any) -> bool:
    if not isinstance(h, dict):
        return False
    for key in h.keys():
        if not isinstance(key, str):
            return False
        try:
            int(key)
        except ValueError:
            return False
        if not isinstance(h[key], list):
            return False
        for chat in h[key]:
            if not isinstance(chat, dict):
                return False
            if "user" not in chat or "message" not in chat:
                return False
            if not isinstance(chat["user"], str) or not isinstance(chat["message"], str):
                return False
            if "reply_to" in chat and chat["reply_to"] is not None:
                if not isinstance(chat["reply_to"], str):
                    return False
    return True


# Load history from pickle file
if os.path.exists("history.json"):
    log("Loading history...")
    try:
        with open("history.json", "r") as f:
            raw_history = json.load(f)
            if not is_valid_history_json(raw_history):
                history = {}
            else:
                # Turn raw history into ChatHistory objects
                for group_id in raw_history.keys():
                    history[int(group_id)] = []
                    for chat in raw_history[group_id]:
                        history[int(group_id)].append(ChatHistory(chat["user"], chat["message"], chat["reply_to"]))

        total_chats = 0
        for group_id in history.keys():
            total_chats += len(history[group_id])
        if total_chats > 0:
            log(
                f"Loaded history: {total_chats} chats from {len(history.keys())} groups",
            )
        else:
            log("Loaded history: empty")
    except Exception as e:
        log(f"Error loading history: {repr(e)}")
        traceback.print_exc()


# Save history to pickle file when exiting
def save_history():
    log("Saving history...")
    with open("history.json", "w") as f:
        # Serialize into dict first
        raw_history = {}
        for group_id in history.keys():
            raw_history[group_id] = []
            for chat in history[group_id]:
                raw_history[group_id].append(
                    {
                        "user": chat.user,
                        "message": chat.message,
                        "reply_to": chat.reply_to,
                    }
                )
        json.dump(raw_history, f)
    log("History saved")


atexit.register(save_history)


def append_history(group_id: int, user: str, message: str, reply_to: Optional[str] = None):
    gid = group_id
    if gid not in history:
        history[gid] = [ChatHistory(user, message, reply_to)]
    else:
        history[gid].append(ChatHistory(user, message, reply_to))
    # Only keep last 10 items
    history[gid] = history[gid][-10:]


def get_history(group_id: int) -> List[ChatHistory]:
    if group_id not in history:
        return []
    return history[group_id]
