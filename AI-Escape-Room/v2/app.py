"""Version 2 - Reliable AI Escape Room (Streamlit UI)."""
import streamlit as st
import engine
import llm
from game_config import ROOM, MAX_HINTS

st.set_page_config(page_title="AI Escape Room v2", page_icon="🔐")


def reset():
    st.session_state.state = engine.new_state()
    st.session_state.messages = [{"role": "assistant", "content": ROOM["intro"]}]
    st.session_state.debug = []


if "state" not in st.session_state:
    reset()
s = st.session_state.state

st.title("🔐 AI Escape Room - Version 2")
if not llm.available():
    st.warning("No GEMINI_API_KEY found: running in offline mode (rule-based parser, plain narration).")

with st.sidebar:
    st.header("Status")
    st.write("🎒 Inventory:", ", ".join(s["inventory"]) or "empty")
    st.write(f"💡 Hints used: {s['hints_used']}/{MAX_HINTS}")
    st.write(f"🧭 Turns: {s['turns']}")
    if st.button("Restart game"):
        reset()
        st.rerun()
    with st.expander("Debug: last parsed actions"):
        st.json(st.session_state.debug[-3:])

for m in st.session_state.messages:
    st.chat_message(m["role"]).write(m["content"])

if prompt := st.chat_input("What do you do?", disabled=s["escaped"]):
    intent = llm.parse_intent(prompt)
    result = engine.execute(s, intent)
    reply = llm.narrate(prompt, result)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.debug.append({"intent": intent, "result": result})
    st.rerun()

if s["escaped"]:
    st.balloons()
    st.success("You escaped! Press Restart to play again.")
