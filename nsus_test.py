import streamlit as st
import time
import random
import requests
import json
from streamlit_autorefresh import st_autorefresh

GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbxHUtX406TMnBYKAk2MYwKsWpSn02FPC5hNfXWV6fx6eRO7vH5rn3rgXBlJ4-Ld3d95/exec"

passages = [
    "Our new product line will be launched next month...",
    "We have recently updated our internal communication guidelines...",
    "To improve cross-functional collaboration, we will be launching...",
    "The finance team is conducting the quarterly budget review...",
    "Customer feedback has shown a strong interest in faster response times..."
]

email_tasks = [
    "One of our team members got sick suddenly, so it’s hard to finish the project on time..."
]

def initialize_session_state():
    if "step" not in st.session_state:
        st.session_state.step = "intro"
    if "selected_passage" not in st.session_state:
        st.session_state.selected_passage = random.choice(passages)
    if "selected_email" not in st.session_state:
        st.session_state.selected_email = random.choice(email_tasks)
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "write_done" not in st.session_state:
        st.session_state.write_done = False
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "passage_answer" not in st.session_state:
        st.session_state.passage_answer = ""
    if "email_answer" not in st.session_state:
        st.session_state.email_answer = ""
    if "input_passage_answer" not in st.session_state:
        st.session_state.input_passage_answer = ""
    if "input_email_answer" not in st.session_state:
        st.session_state.input_email_answer = ""

initialize_session_state()

st.title("NSUS English Test")

def move_to_step(next_step):
    st.session_state.step = next_step
    st.session_state.start_time = time.time()
    st.session_state.write_done = False
    st.session_state.submitted = False
    st.rerun()

def get_time_left(limit):
    if st.session_state.start_time is None:
        return limit
    return max(0, int(limit - (time.time() - st.session_state.start_time)))

def post_to_google_sheets(response_text, response_type):
    data = {
        "response": response_text.strip(),
        "type": response_type
    }
    try:
        requests.post(GOOGLE_SHEETS_URL, data=json.dumps(data))
    except Exception as e:
        st.error(f"Error saving {response_type} answer: {e}")

def intro_step():
    st.subheader("📝 NSUS English Test")
    st.markdown("This is a two-part writing test including passage reconstruction and email writing.")
    if st.button("Start Test"):
        move_to_step("passage_read")

def passage_read_step():
    st_autorefresh(interval=1000, key="read_refresh")
    st.subheader(":page_facing_up: Passage Reading (30s)")
    st.info(st.session_state.selected_passage)

    time_left = get_time_left(30)
    st.write(f":hourglass: Time left: {time_left} seconds")

    if time_left <= 0:
        move_to_step("passage_write")

def write_step(title, key_input, key_final, next_step, response_type):
    total_time = 120
    time_left = get_time_left(total_time)

    if not st.session_state.write_done:
        st_autorefresh(interval=1000, key=f"{response_type}_refresh")

    st.subheader(title)
    st.write(f":hourglass: Time left: {time_left} seconds")

    disabled = st.session_state.write_done or time_left <= 0

    input_value = st.text_area("Write here:", value=st.session_state.get(key_input, ""), key=key_input, height=150, disabled=disabled)
    st.session_state[key_final] = input_value  # 실시간 반영

    def on_write_done():
        st.session_state.write_done = True

    if time_left <= 0 and not st.session_state.write_done:
        st.markdown("""
        <script>
        const doneBtn = document.getElementById("done_button");
        if (doneBtn) { doneBtn.click(); }
        </script>
        """, unsafe_allow_html=True)

    if not st.session_state.write_done:
        st.button("작성 완료", key="done_button", on_click=on_write_done)
    else:
        cols = st.columns([1, 1])
        with cols[0]:
            st.button("작성 완료", disabled=True)
        with cols[1]:
            if st.button("Submit"):
                final_answer = st.session_state.get(key_input, "").strip()
                post_to_google_sheets(final_answer, response_type)
                move_to_step(next_step)

def passage_write_step():
    write_step(":pencil2: Reconstruct the Passage (120s)", "input_passage_answer", "passage_answer", "email_write", "passage")

def email_write_step():
    write_step(":email: Email Writing (120s)", "input_email_answer", "email_answer", "done", "email")

def done_step():
    st.success(":tada: All tasks are complete! Well done!")

if st.session_state.step == "intro":
    intro_step()
elif st.session_state.step == "passage_read":
    passage_read_step()
elif st.session_state.step == "passage_write":
    passage_write_step()
elif st.session_state.step == "email_write":
    email_write_step()
elif st.session_state.step == "done":
    done_step()
