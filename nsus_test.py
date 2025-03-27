import streamlit as st
import time
import random
import requests
import json

# Google Sheets URL
GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbxHUtX406TMnBYKAk2MYwKsWpSn02FPC5hNfXWV6fx6eRO7vH5rn3rgXBlJ4-Ld3d95/exec"

# 지문 및 과제
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
def initialize_session_state():
    if "step" not in st.session_state:
        st.session_state.step = "intro"
    if "selected_passage" not in st.session_state:
        st.session_state.selected_passage = random.choice(passages)
    if "selected_email" not in st.session_state:
        st.session_state.selected_email = random.choice(email_tasks)
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "passage_answer" not in st.session_state:
        st.session_state.passage_answer = ""
    if "email_answer" not in st.session_state:
        st.session_state.email_answer = ""

initialize_session_state()

st.title("NSUS English Test")

# 단계 이동
def move_to_step(next_step):
    st.session_state.step = next_step
    st.session_state.start_time = time.time()
    st.session_state.submitted = False
    st.rerun()

# 시간 계산
def get_time_left(limit):
    if st.session_state.start_time is None:
        return limit
    return max(0, int(limit - (time.time() - st.session_state.start_time)))

# 저장 함수
def post_to_google_sheets(response_text, response_type):
    data = {
        "response": response_text.strip(),
        "type": response_type
    }
    try:
        requests.post(GOOGLE_SHEETS_URL, data=json.dumps(data))
    except Exception as e:
        st.error(f"Error saving {response_type} answer: {e}")

# 단계: 인트로
def intro_step():
    st.subheader("📝 NSUS English Test")
    st.markdown("This is a two-part writing test including passage reconstruction and email writing.")
    if st.button("Start Test"):
        move_to_step("passage_read")

# 단계: 읽기
def passage_read_step():
    st.subheader("📄 Passage Reading (30s)")
    st.info(st.session_state.selected_passage)

    time_left = get_time_left(30)
    st.write(f"⏳ Time left: {time_left} seconds")

    if time_left <= 0 and not st.session_state.submitted:
        st.session_state.submitted = True
        move_to_step("passage_write")

# 단계: 지문 작성
def passage_write_step():
    st.subheader("✍️ Reconstruct the Passage (120s)")

    total_time = 120
    time_left = get_time_left(total_time)
    st.write(f"⏳ Time left: {time_left} seconds")

    disabled = time_left <= 0
    if disabled:
        st.warning("Time is up. Please click the Submit button to continue.")

    st.text_area("Write the passage:", key="passage_answer", height=150, disabled=disabled)

    if st.button("Submit Answer"):
        post_to_google_sheets(st.session_state.passage_answer, "passage")
        move_to_step("email_write")

# 단계: 이메일 작성
def email_write_step():
    st.subheader("📧 Email Writing (120s)")

    total_time = 120
    time_left = get_time_left(total_time)
    st.write(f"⏳ Time left: {time_left} seconds")

    disabled = time_left <= 0
    if disabled:
        st.warning("Time is up. Please click the Submit button to continue.")

    st.text_area("Write your email:", key="email_answer", height=150, disabled=disabled)

    if st.button("Submit Answer"):
        post_to_google_sheets(st.session_state.email_answer, "email")
        move_to_step("done")

# 단계: 완료
def done_step():
    st.success("🎉 All tasks are complete! Well done!")

# 실행
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
