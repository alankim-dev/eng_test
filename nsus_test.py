import streamlit as st
import time
import random
import requests
import json
from streamlit_autorefresh import st_autorefresh

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
    defaults = {
        "step": "intro",
        "selected_passage": random.choice(passages),
        "selected_email": random.choice(email_tasks),
        "start_time": None,
        "submitted": False,
        "passage_answer": "",
        "email_answer": "",
        "writing_done": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

st.title("NSUS English Test")

# 단계 이동
def move_to_step(next_step):
    st.session_state.step = next_step
    st.session_state.start_time = time.time()
    st.session_state.submitted = False
    st.session_state.writing_done = False
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

# 인트로 단계
def intro_step():
    st.subheader("📝 NSUS English Test")
    st.markdown("This is a two-part writing test including passage reconstruction and email writing.")
    if st.button("Start Test"):
        move_to_step("passage_read")

# 지문 읽기 단계
def passage_read_step():
    st_autorefresh(interval=1000, key="read_refresh")
    st.subheader("📄 Passage Reading (30s)")
    st.info(st.session_state.selected_passage)
    time_left = get_time_left(30)
    st.write(f"⏳ Time left: {time_left} seconds")
    if time_left <= 0:
        move_to_step("passage_write")

# 작성 단계 공통 함수
def writing_step(title, key_name, next_step, response_type, prompt_text):
    st_autorefresh(interval=1000, key=f"{response_type}_refresh")

    st.subheader(title)
    st.markdown(prompt_text)
    total_time = 120
    time_left = get_time_left(total_time)
    expired = time_left <= 0
    st.write(f"⏳ Time left: {time_left} seconds")

    if expired and not st.session_state.writing_done:
        st.session_state.writing_done = True
        st.rerun()

    disabled = st.session_state.writing_done or expired

    # 입력값을 임시로 변수에 저장 (최신 상태 유지)
    current_text = st.text_area("Write here:", value=st.session_state.get(key_name, ""), height=150, disabled=disabled, key=f"{key_name}_input")
    st.session_state[key_name] = current_text

    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("작성 완료", disabled=st.session_state.writing_done, key="writing_done_btn", on_click=lambda: st.session_state.update({"writing_done": True}))
    with col2:
        if st.session_state.writing_done:
            if st.button("제출", key="submit_btn"):
                answer = st.session_state.get(key_name, "").strip()
                post_to_google_sheets(answer, response_type)
                move_to_step(next_step)

# 각 단계 정의
def passage_write_step():
    writing_step(
        "✍️ Reconstruct the Passage (120s)",
        "passage_answer",
        "email_write",
        "passage",
        "Use your own words to reconstruct the passage. **Do not copy the sentences or vocabulary directly.**"
    )

def email_write_step():
    writing_step(
        "📧 Email Writing (120s)",
        "email_answer",
        "done",
        "email",
        "Based on the situation below, write a professional and polite email requesting a one-week extension."
    )
    st.info(st.session_state.selected_email)

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
