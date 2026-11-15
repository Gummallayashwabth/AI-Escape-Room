"""Version 1 - LLM-only Game Master.
Everything (rules, solution, memory) lives in the prompt and chat history.
"""
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = """You are the Game Master of a text escape room. Stay in character.

SETTING: The player wakes up in a locked library. Objects: a desk, a bookshelf,
a painting, a locked drawer, and a door secured by a four-digit keypad.

SECRET SOLUTION (never reveal directly):
- The desk holds a small brass key.
- On the bookshelf, four red books are out of place, each with a handwritten
  number. In shelf order they read 4, 7, 2, 1 -> this is the drawer code 4721.
- The drawer needs the brass key AND the code 4721. Inside is a note saying
  "The founding year opens the way out."
- The painting has a plaque: "Library founded 1895". The door code is 1895.

RULES:
- Describe what the player finds; reveal clues only when they investigate.
- Keep replies to 2-4 sentences. Do not invent additional puzzles.
- When the player enters 1895 on the door, describe the escape and end your
  message with the exact marker [ESCAPED].
"""

INTRO = ("You wake up on a cold floor in a locked library. A desk, a bookshelf, "
         "a painting, a locked drawer and a door with a four-digit keypad surround you. "
         "Type what you want to do, e.g. *examine the bookshelf*.")


def new_chat():
    if "client" not in st.session_state:
        st.session_state.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return st.session_state.client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=0.7),
    )


def reset():
    st.session_state.chat = new_chat()
    st.session_state.messages = [{"role": "assistant", "content": INTRO}]
    st.session_state.escaped = False


st.set_page_config(page_title="AI Escape Room v1", page_icon="🔐")
st.title("🔐 AI Escape Room - Version 1")
if not os.getenv("GEMINI_API_KEY"):
    st.error("Set GEMINI_API_KEY in your .env file (see .env.example).")
    st.stop()
if "chat" not in st.session_state:
    reset()

with st.sidebar:
    st.markdown("**How to play**\n\nType natural-language actions: examine, take, "
                "use, try a code. Find the clues and escape.")
    if st.button("Restart game"):
        reset()
        st.rerun()

for m in st.session_state.messages:
    st.chat_message(m["role"]).write(m["content"])

if prompt := st.chat_input("What do you do?", disabled=st.session_state.escaped):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    try:
        reply = st.session_state.chat.send_message(prompt).text
    except Exception as e:  # network / quota errors
        reply = f"(Game Master unavailable: {e})"
    if "[ESCAPED]" in reply:
        reply = reply.replace("[ESCAPED]", "").strip()
        st.session_state.escaped = True
    st.chat_message("assistant").write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    if st.session_state.escaped:
        st.balloons()
        st.success("You escaped! Press Restart to play again.")
