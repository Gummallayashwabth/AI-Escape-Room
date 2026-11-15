"""Deterministic game engine: structured state + action validation.
Python decides what succeeds; the LLM only narrates the returned facts."""
import re
from game_config import ROOM, SOLUTIONS, MAX_HINTS

T = ROOM["text"]


def new_state():
    return {"inventory": [], "key_revealed": False, "books_read": False,
            "painting_read": False, "drawer_open": False, "door_open": False,
            "escaped": False, "turns": 0, "hints_used": 0, "failed_attempts": 0}


def resolve(name):
    """Map free text to ('object'|'item', canonical) or None."""
    if not name:
        return None
    n = name.lower().strip()
    for kind in ("objects", "items"):
        for canon, d in ROOM[kind].items():
            for a in [canon] + d["aliases"]:
                if n == a or re.search(rf"\b{re.escape(a)}\b", n):
                    return ("object" if kind == "objects" else "item", canon)
    return None


def _r(ok, event, *facts):
    return {"ok": ok, "event": event, "facts": list(facts)}


def _examine(s, i):
    ref = resolve(i.get("target") or i.get("item"))
    if not ref:
        return _r(False, "unknown_target", "There is no such thing in this room.")
    kind, name = ref
    if kind == "item":
        if name in s["inventory"]:
            return _r(True, "examine_item", ROOM["items"][name]["description"])
        return _r(False, "not_held", f"You are not carrying a {name}.")
    if name == "desk":
        if not s["key_revealed"]:
            s["key_revealed"] = True
            return _r(True, "found_key", T["desk_first"])
        return _r(True, "examine", T["desk_again"])
    if name == "bookshelf":
        s["books_read"] = True
        return _r(True, "clue", T["bookshelf"])
    if name == "painting":
        s["painting_read"] = True
        return _r(True, "clue", T["painting"])
    if name == "drawer":
        return _r(True, "examine", T["drawer_done"] if s["drawer_open"] else T["drawer_locked"])
    return _r(True, "examine", T["win"] if s["door_open"] else T["door_locked"])


def _take(s, i):
    ref = resolve(i.get("item") or i.get("target"))
    if not ref:
        return _r(False, "unknown_target", "There is nothing like that to take.")
    kind, name = ref
    if kind == "object":
        return _r(False, "cannot_take", f"You cannot pick up the {name}.")
    if name in s["inventory"]:
        return _r(False, "already_have", f"You already have the {name}.")
    if name == "brass key" and not s["key_revealed"]:
        return _r(False, "not_visible", "You do not see any such item yet.")
    s["inventory"].append(name)
    return _r(True, "took_item", f"You pick up the {name}.")


def _unlock(s, i):
    item_raw, code = i.get("item"), i.get("code")
    if item_raw:
        ref = resolve(item_raw)
        if not ref or ref[0] != "item":
            return _r(False, "unknown_item", "You have no such item.")
        if ref[1] not in s["inventory"]:
            return _r(False, "not_held", f"You are not carrying a {ref[1]}.")
    ref = resolve(i.get("target"))
    if not ref or ref[0] != "object" or ref[1] not in ("drawer", "door"):
        return _r(False, "bad_target", "Nothing happens. Say what you want to open (the drawer or the door).")
    name = ref[1]
    if name == "drawer":
        if s["drawer_open"]:
            return _r(True, "already_open", T["drawer_done"])
        if "brass key" not in s["inventory"]:
            return _r(False, "locked", "The drawer will not budge. You have nothing to fit its keyhole.")
        if not code:
            return _r(False, "need_code", "The key turns, but the four-digit dial still blocks the drawer.")
        if code != SOLUTIONS["drawer_code"]:
            s["failed_attempts"] += 1
            return _r(False, "wrong_code", "The dial clicks but does not release. That combination is wrong.")
        s["drawer_open"] = True
        return _r(True, "drawer_opened", T["drawer_open"])
    if s["door_open"]:
        return _r(True, "already_open", T["win"])
    if not code:
        return _r(False, "need_code", "The keypad waits for a four-digit code.")
    if code != SOLUTIONS["door_code"]:
        s["failed_attempts"] += 1
        return _r(False, "wrong_code", "The keypad buzzes angrily. Wrong code.")
    s["door_open"] = s["escaped"] = True
    return _r(True, "escaped", T["win"])


def _inventory(s, i):
    return _r(True, "inventory", f"You are carrying: {', '.join(s['inventory']) or 'nothing'}.")


def _hint(s, i):
    if s["hints_used"] >= MAX_HINTS:
        return _r(False, "no_hints", "You have used all your hints.")
    s["hints_used"] += 1
    if not s["key_revealed"]:
        h = "Start by searching the furniture for something you can carry."
    elif "brass key" not in s["inventory"]:
        h = "That small object you found could be useful. Pick it up."
    elif not s["books_read"]:
        h = "Something on the bookshelf looks out of place."
    elif not s["drawer_open"]:
        h = "You have a key and some numbers. Try them on the drawer."
    elif not s["painting_read"]:
        h = "The note mentions a year. Where might a founding year be written?"
    else:
        h = "You know the year. Try it on the door keypad."
    return _r(True, "hint", f"Hint {s['hints_used']} of {MAX_HINTS}: {h}")


def _cheat(s, i):
    return _r(False, "refused", "The Game Master cannot reveal solutions, skip puzzles or grant special permissions. "
              "Nobody has administrator powers in this room. Investigate, or ask for a hint.")


def _help(s, i):
    return _r(True, "help", "You can examine objects, take items, use items, try codes on the drawer or door, ask for a hint, or check your inventory.")


def _unknown(s, i):
    return _r(False, "unknown", "That is not something you can do in this room.")


HANDLERS = {"examine": _examine, "take": _take, "unlock": _unlock, "inventory": _inventory,
            "hint": _hint, "cheat": _cheat, "help": _help}


def execute(state, intent):
    """Validate + apply an intent dict {action,target,item,code}. Mutates state."""
    action = (intent.get("action") or "unknown").lower()
    if state["escaped"] and action not in ("help", "inventory"):
        return _r(True, "already_escaped", "You already escaped. Restart to play again.")
    if action in ("examine", "take", "unlock"):
        state["turns"] += 1
    return HANDLERS.get(action, _unknown)(state, intent)
