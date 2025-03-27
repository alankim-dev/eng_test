import streamlit as st
import time
import random
import requests
import json

# Google Apps Script 웹앱 URL
GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbxHUtX406TMnBYKAk2MYwKsWpSn02FPC5hNfXWV6fx6eRO7vH5rn3rgXBlJ4-Ld3d95/exec"

# ========== 예시 지문 및 이메일 과제 ==========
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

# ========== 상태 초기화 ==========
def initialize_state():
    if "step" not in st.session_state:
        st.session_state.step = "intro"
    if "selected_passage" not in st.session_state:
        st.session_state.selected_passage = random.choice(passages)
    if "selected_email" not in st.session_state:
        st.session_state.selected_email = random.choice(email_tasks)
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "passage_answer" not in st.session_state:
        st.session_state.passage_answer = ""
    if "email_answer" not in st.session_state:
        st.session_state.email_answer = ""

initialize_state()

st.title("NSUS English Test")

# ========== 유틸 함수 ==========
def get_time_left(total_sec):
    if st.session_state.start_time is None:
        return total_sec
    return int(total_sec - (time.time() - st.session_state.start_time))

def move_to_step(next_step):
    st.session_state.step = next_step
    st.session_state.start_time = time.time()
    st.rerun()

def post_to_google_sheets(text, kind):
    payload = {"response": text.strip(), "type": kind}
    try:
        requests.post(GOOGLE_SHEETS_URL, data=json.dumps(payload))
    except Exception as e:
        st.error(f"Error saving response: {e}")

# ========== 단계별 화면 ==========
def intro_step():
    st.subheader("📝 NSUS English Test")
    st.markdown("This is a two-part writing test including passage reconstruction and email writing.")
    if st.button("Start Test"):
        move_to_step("passage_read")

def passage_read_step():
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000, limit=0)

    st.subheader("📄 Passage Reading")
    st.info(st.session_state.selected_passage)

    time_left = get_time_left(30)
    st.write(f"⏳ Time left: **{max(time_left, 0)} seconds**")

    if time_left <= 0:
        move_to_step("passage_write")

def passage_write_step():
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000, limit=0)

    st.subheader("✍️ Reconstruct the Passage")
    time_left = get_time_left(120)
    disabled = time_left <= 0

    st.write(f"⏳ Time left: **{max(time_left, 0)} seconds**")
    if disabled:
        st.warning("Time is up. You can no longer edit your answer. Please click [Submit Answer] to continue.")

    st.text_area("Write the passage from memory:", key="passage_answer", height=150, disabled=disabled)

    if st.button("Submit Answer"):
        answer = st.session_state.get("passage_answer", "").strip()
        post_to_google_sheets(answer, "passage")
        move_to_step("email_write")

def email_write_step():
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000, limit=0)

    st.subheader("📧 Email Writing")
    st.info(st.session_state.selected_email)

    time_left = get_time_left(120)
    disabled = time_left <= 0

    st.write(f"⏳ Time left: **{max(time_left, 0)} seconds**")
    if disabled:
        st.warning("Time is up. You can no longer edit your answer. Please click [Submit Answer] to finish.")

    st.text_area("Write your email here:", key="email_answer", height=150, disabled=disabled)

    if st.button("Submit Answer"):
        answer = st.session_state.get("email_answer", "").strip()
        post_to_google_sheets(answer, "email")
        move_to_step("done")

def done_step():
    st.success("🎉 All tasks are complete! Thank you!")

# ========== 실행 ==========
step = st.session_state.step
if step == "intro":
    intro_step()
elif step == "passage_read":
    passage_read_step()
elif step == "passage_write":
    passage_write_step()
elif step == "email_write":
    email_write_step()
elif step == "done":
    done_step()
