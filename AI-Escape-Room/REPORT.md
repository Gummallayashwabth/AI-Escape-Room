# Report: AI-Powered Escape Room

*(Draft - edit it with your own observations and results before submitting; aim for 2-3 pages.)*

## 1. Goal
Build an LLM-driven escape room in two versions: V1 with an LLM Game Master only, and V2 with structured
game state and validation so that behaviour is reliable even against adversarial players.

## 2. Version 1 design
A Streamlit chat UI sends the player's messages to Gemini through a chat session. The system prompt describes
the library, the five objects, the puzzle chain and the solutions (drawer code 4721, door code 1895). Memory is
the chat history. The LLM appends `[ESCAPED]` when the door code is entered, which the app uses to detect completion.
A sidebar button restarts the game and the intro explains how to play.

**Problems observed (record yours):** the model can contradict earlier state, invent objects, hand out items too
early, accept codes loosely, and leak the solution because it sits in the prompt. Completion detection relies on
the model following a formatting rule.

## 3. Version 2 design
Responsibilities are separated:
- **`game_config.py`** stores solutions and clue texts outside the LLM.
- **`engine.py`** keeps a state dictionary (inventory, key/drawer/door status, hints, turns, failed attempts) and has one
  validation function per action. Python decides success or failure.
- **`intent_parser.py` / `llm.py`** use Gemini (temperature 0, JSON output) to convert free text into
  `{action, target, item, code}`, with a rule-based fallback. Codes are taken from the raw text by regex.
- **Narrator:** Gemini receives only the facts returned by the engine and describes them; an output guard rejects text
  containing digits that are not in the facts.
- **Guardrails:** `cheat` intent is refused, hints are limited to three and progressive, input is treated as untrusted data.

## 4. Testing
Nine scenarios are listed in `TEST_CASES.md`; eleven automated tests cover the engine (uncollected key, wrong code, false
solved claim, administrator impersonation, secret disclosure, nonexistent objects, hint limit, consistency after solving,
full walkthrough). Add your V1 observations and screenshots there.

## 5. Problems and lessons
- Prompt instructions alone are not a security boundary; secrets must not be in the prompt at all.
- LLMs are better as translators (text to intent, facts to text) than as rule enforcers.
- The intent parser is still an LLM, so it can misclassify; defence in depth (regex code extraction, engine validation,
  narration guard) ensures a misclassification cannot corrupt state.
- API outages and quota limits required fallbacks.

## 6. Limitations and future work
One room, limited fallback phrasing, no automated LLM-based evaluation. Future work: multiple rooms, save/load,
a larger adversarial test set, and measuring parser accuracy.
