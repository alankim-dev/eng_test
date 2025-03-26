import streamlit as st
import time
import random
import requests
import json

# Google Apps Script 웹앱 URL
GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbxHUtX406TMnBYKAk2MYwKsWpSn02FPC5hNfXWV6fx6eRO7vH5rn3rgXBlJ4-Ld3d95/exec"

# 예시 지문 및 이메일 과제
passages = [
    "Our new product line will be launched next month...",
    "We have recently updated our internal communication guidelines...",
]
email_tasks = [
    "One of our team members got sick suddenly...",
]

# 초기 상태 설정 함수
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

initialize_session_state()

st.title("NSUS English Test")

# 유틸리티 함수들
def get_time_left(total_seconds):
    if st.session_state.start_time is None:
        return total_seconds
    elapsed = time.time() - st.session_state.start_time
    return int(total_seconds - elapsed)

def move_to_step(next_step):
    """단계를 전환하고 화면을 즉시 새로고침."""
    st.session_state.step = next_step
    st.session_state.start_time = time.time()
    st.session_state.submitted = False
    st.experimental_rerun()

def post_to_google_sheets(response_text, response_type):
    """Google Apps Script 웹앱으로 POST 요청을 보내 Sheet에 저장."""
    data = {
        "response": response_text.strip(),
        "type": response_type,
    }
    try:
        r = requests.post(GOOGLE_SHEETS_URL, data=json.dumps(data))
        return r.json()
    except Exception as e:
        st.error(f"Error saving {response_type} answer: {e}")
        return None

def save_passage_answer():
    post_to_google_sheets(st.session_state["passage_answer"], "passage")

def save_email_answer():
    post_to_google_sheets(st.session_state["email_answer"], "email")

# 단계별 로직 정의
def intro_step():
    st.subheader("📝 NSUS English Test")
    if st.button("Start Test"):
        move_to_step("passage_read")

def passage_read_step():
    st.subheader("📄 Passage Reconstruction (Reading)")
    time_left = get_time_left(30)
    if time_left <= 0:
        move_to_step("passage_write")
    
def passage_write_step():
    st.subheader("✍️ Reconstruct the Passage (2 minutes)")
    
    time_left = get_time_left(120)
    
    disabled_flag = (time_left <= 0)
    
    # text_area에서 key 사용하여 자동 저장 처리
    st.text_area(
        "Write the passage from memory:", 
        key="passage_answer", 
        height=150, 
        disabled=disabled_flag,
    )
    
    if disabled_flag and not st.session_state.submitted:
        st.info("Time is up! Please click [Submit Answer].")
    
    if st.button("Submit Answer") and not st.session_state.submitted:
        save_passage_answer()
        move_to_step("email_write")

def email_write_step():
    pass  # 이메일 작성 단계 구현

def done_step():
    pass  # 완료 단계 구현

# 단계별 실행 로직 연결
if __name__ == "__main__":
    if st.session_state.step == "intro":
        intro_step()
    elif st.session_state.step == "passage_read":
        passage_read_step()
