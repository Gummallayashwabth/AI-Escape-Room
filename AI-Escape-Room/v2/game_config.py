"""Static game rules, solutions and clue text. Lives OUTSIDE the LLM.
The LLM never sees SOLUTIONS or undiscovered clue text."""

SOLUTIONS = {"drawer_code": "4721", "door_code": "1895"}
MAX_HINTS = 3

ROOM = {
    "intro": ("You wake up on a cold floor in a locked library. You can see a desk, a "
              "bookshelf, a painting, a locked drawer and a door with a four-digit keypad. "
              "Examine things, collect items, solve puzzles and escape. "
              "Type 'hint' if stuck (3 hints max) or 'inventory' to see what you carry."),
    "objects": {
        "desk": {"aliases": ["writing desk", "table"]},
        "bookshelf": {"aliases": ["shelf", "shelves", "books", "book"]},
        "painting": {"aliases": ["portrait", "picture", "frame", "plaque"]},
        "drawer": {"aliases": ["drawers"]},
        "door": {"aliases": ["keypad", "exit"]},
    },
    "items": {
        "brass key": {"aliases": ["key"], "description": "A small brass key with a tiny engraved drawer."},
    },
    "text": {
        "desk_first": "Searching the desk, you find a small brass key in a shallow tray.",
        "desk_again": "The desk holds nothing else of interest.",
        "bookshelf": "Four red books stand out of order. Each has a handwritten number inside its cover: 4, 7, 2, 1 in shelf order.",
        "painting": "A stern portrait. A brass plaque below it reads: 'Library founded 1895'.",
        "drawer_open": "The drawer slides open. Inside is a note: 'The founding year opens the way out.'",
        "drawer_locked": "The drawer is locked. It has a keyhole and a four-digit dial.",
        "drawer_done": "The drawer is already open; you have read the note inside.",
        "door_locked": "A heavy door with a four-digit keypad. It is locked.",
        "win": "The keypad beeps, the lock clicks and the door swings open. Fresh air - you escaped!",
    },
}
