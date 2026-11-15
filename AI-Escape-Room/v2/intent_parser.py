"""Offline rule-based intent parser (fallback and for tests) + shared code extraction."""
import re
from game_config import ROOM

CHEAT = re.compile(r"\b(admin|administrator|developer|system prompt|jailbreak|override|"
                   r"ignore (all|any|previous|your|the)|all (the )?(codes|solutions|secrets|answers)|"
                   r"reveal|tell me the (code|answer|solution|combination)|"
                   r"what('?s| is) the (code|answer|solution|combination))\b", re.I)
CODE = re.compile(r"(?<!\d)(\d)[ \-,.]?(\d)[ \-,.]?(\d)[ \-,.]?(\d)(?!\d)")


def extract_code(text):
    m = CODE.search(text)
    return "".join(m.groups()) if m else None


def _mentions(text, kind):
    out = []
    for canon, d in ROOM[kind].items():
        if any(re.search(rf"\b{re.escape(a)}s?\b", text) for a in [canon] + d["aliases"]):
            out.append(canon)
    return out


def parse(message):
    t = message.lower()
    objs, items = _mentions(t, "objects"), _mentions(t, "items")
    intent = {"action": "unknown", "target": objs[0] if objs else None,
              "item": items[0] if items else None, "code": extract_code(t)}
    if CHEAT.search(t):
        intent["action"] = "cheat"
    elif re.search(r"\b(hint|stuck)\b", t):
        intent["action"] = "hint"
    elif re.search(r"\b(help|instructions|how do i play)\b", t):
        intent["action"] = "help"
    elif re.search(r"\b(inventory|what do i have|my items|carrying)\b", t):
        intent["action"] = "inventory"
    elif re.search(r"\b(take|grab|pick up|collect|pocket)\b", t):
        intent["action"] = "take"
    elif re.search(r"\b(unlock|open|enter|try|use|input|type|code|escape)\b", t) and (
            intent["code"] or "drawer" in objs or "door" in objs):
        intent["action"] = "unlock"
    elif re.search(r"\b(examine|look|inspect|check|search|read|investigate|study)\b", t) or objs or items:
        intent["action"] = "examine"
    return intent
