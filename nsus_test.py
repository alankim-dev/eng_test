import streamlit as st
import time
import random
import requests
import json

# Google Sheets 연동 URL
GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbxHUtX406TMnBYKAk2MYwKsWpSn02FPC5hNfXWV6fx6eRO7vH5rn3rgXBlJ4-Ld3d95/exec"

# 예문 및 과제
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
        "passage_auto_submit": False,
        "email_auto_submit": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
st.title("NSUS English Test")

# 타이머 계산
def get_time_left(limit):
    if st.session_state.start_time is None:
        return limit
    return max(0, int(limit - (time.time() - st.session_state.start_time)))

# 시트 저장
def post_to_google_sheets(text, kind):
    try:
        requests.post(GOOGLE_SHEETS_URL, data=json.dumps({
            "response": text.strip(),
            "type": kind
        }))
    except Exception as e:
        st.error(f"Error saving to sheet: {e}")

# 단계: 인트로
def intro_step():
    st.subheader("📝 NSUS English Test")
    st.markdown("This is a two-part writing test including passage reconstruction and email writing.")
    if st.button("Start Test"):
        st.session_state.step = "passage_read"
        st.session_state.start_time = time.time()
        st.rerun()

# 단계: Reading
def passage_read_step():
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000)

    st.subheader("📄 Passage Reading")
    st.info(st.session_state.selected_passage)

    time_left = get_time_left(30)
    st.write(f"⏳ Time left: {time_left} seconds")

    if time_left <= 0 and not st.session_state.passage_auto_submit:
        st.session_state.passage_auto_submit = True
        st.session_state.step = "passage_write"
        st.session_state.start_time = time.time()
        st.rerun()

# 단계: Passage 작성
def passage_write_step():
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000)

    st.subheader("✍️ Reconstruct the Passage")
    time_left = get_time_left(120)
    disabled = time_left <= 0
    st.write(f"⏳ Time left: {time_left} seconds")
    if disabled:
        st.warning("⏰ Time is up. Please submit manually.")

    # 자동 제출
    if time_left <= 0 and not st.session_state.passage_auto_submit:
        st.session_state.passage_auto_submit = True
        post_to_google_sheets(st.session_state.passage_answer, "passage")
        st.session_state.step = "email_write"
        st.session_state.start_time = time.time()
        st.rerun()

    with st.form("passage_form"):
        user_input = st.text_area("Write the passage:", value=st.session_state.passage_answer, height=150, disabled=disabled)
        submitted = st.form_submit_button("Submit Answer")
        if submitted:
            st.session_state.passage_answer = user_input
            post_to_google_sheets(user_input, "passage")
            st.session_state.step = "email_write"
            st.session_state.start_time = time.time()
            st.rerun()

# 단계: Email 작성
def email_write_step():
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000)

    st.subheader("📧 Email Writing")
    st.info(st.session_state.selected_email)

    time_left = get_time_left(120)
    disabled = time_left <= 0
    st.write(f"⏳ Time left: {time_left} seconds")
    if disabled:
        st.warning("⏰ Time is up. Please submit manually.")

    if time_left <= 0 and not st.session_state.email_auto_submit:
        st.session_state.email_auto_submit = True
        post_to_google_sheets(st.session_state.email_answer, "email")
        st.session_state.step = "done"
        st.session_state.start_time = time.time()
        st.rerun()

    with st.form("email_form"):
        user_input = st.text_area("Write your email here:", value=st.session_state.email_answer, height=150, disabled=disabled)
        submitted = st.form_submit_button("Submit Answer")
        if submitted:
            st.session_state.email_answer = user_input
            post_to_google_sheets(user_input, "email")
            st.session_state.step = "done"
            st.session_state.start_time = time.time()
            st.rerun()

# 단계: 완료
def done_step():
    st.success("🎉 All tasks complete! Thank you.")

# 단계 실행
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
