import streamlit as st
import time
import random
import requests
import json

# Google Sheets 연동
GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbxHUtX406TMnBYKAk2MYwKsWpSn02FPC5hNfXWV6fx6eRO7vH5rn3rgXBlJ4-Ld3d95/exec"

# 지문과 이메일
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

# 상태 초기화
def init_state():
    defaults = {
        "step": "intro",
        "selected_passage": random.choice(passages),
        "selected_email": random.choice(email_tasks),
        "start_time": None,
        "passage_answer": "",
        "email_answer": "",
        "next_step": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
st.title("NSUS English Test")

# 시간 계산
def get_time_left(limit):
    if st.session_state.start_time is None:
        return limit
    return max(0, int(limit - (time.time() - st.session_state.start_time)))

# Google Sheets로 제출
def post_to_google_sheets(text, kind):
    try:
        requests.post(GOOGLE_SHEETS_URL, data=json.dumps({"response": text.strip(), "type": kind}))
    except Exception as e:
        st.error(f"Error: {e}")

# 단계별 화면
def intro_step():
    st.subheader("📝 NSUS English Test")
    st.markdown("This is a two-part writing test including passage reconstruction and email writing.")
    if st.button("Start Test"):
        st.session_state.step = "passage_read"
        st.session_state.start_time = time.time()

def passage_read_step():
    st.subheader("📄 Passage Reading")
    st.info(st.session_state.selected_passage)

    time_left = get_time_left(30)
    st.write(f"⏳ Time left: {time_left} seconds")

    if time_left <= 0:
        st.session_state.step = "passage_write"
        st.session_state.start_time = time.time()

def passage_write_step():
    st.subheader("✍️ Reconstruct the Passage")
    time_left = get_time_left(120)
    disabled = time_left <= 0
    st.write(f"⏳ Time left: {time_left} seconds")

    if disabled:
        st.warning("⏰ Time is up. You can no longer edit your answer. Please click Submit.")

    with st.form("passage_form"):
        st.text_area("Write the passage from memory:", key="passage_answer", height=150, disabled=disabled)
        submitted = st.form_submit_button("Submit Answer")
        if submitted:
            post_to_google_sheets(st.session_state.passage_answer, "passage")
            st.session_state.next_step = "email_write"

def email_write_step():
    st.subheader("📧 Email Writing")
    st.info(st.session_state.selected_email)

    time_left = get_time_left(120)
    disabled = time_left <= 0
    st.write(f"⏳ Time left: {time_left} seconds")

    if disabled:
        st.warning("⏰ Time is up. You can no longer edit your answer. Please click Submit.")

    with st.form("email_form"):
        st.text_area("Write your email here:", key="email_answer", height=150, disabled=disabled)
        submitted = st.form_submit_button("Submit Answer")
        if submitted:
            post_to_google_sheets(st.session_state.email_answer, "email")
            st.session_state.next_step = "done"

def done_step():
    st.success("🎉 All tasks complete! Thank you.")

# 🔄 단계 전환 (form 밖에서만 수행)
if st.session_state.next_step:
    st.session_state.step = st.session_state.next_step
    st.session_state.start_time = time.time()
    st.session_state.next_step = None

# 단계 실행
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
