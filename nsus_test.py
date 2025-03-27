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
    "Our new product line will be launched next month. We are planning a series of promotional events to increase awareness. All team members are expected to contribute ideas for marketing strategies. Please submit your suggestions by Friday afternoon.",
    "We have recently updated our internal communication guidelines to ensure that everyone stays informed and aligned. Managers are responsible for sharing weekly updates with their teams. Please check your email every Monday morning for the latest announcements and summaries.",
    "To improve cross-functional collaboration, we will be launching a new project management tool starting next week. Training sessions will be provided on Wednesday and Thursday. Attendance is mandatory for all team members who manage or participate in projects.",
    "The finance team is conducting the quarterly budget review, and all departments must submit their expense reports by the end of this week. Delayed submissions may result in your department's budget being frozen until the next quarter.",
    "Customer feedback has shown a strong interest in faster response times. To address this, we are adjusting our support team shifts starting Monday. Please review the updated schedule and confirm your availability with your manager by Friday."
]
email_tasks = [
    "One of our team members got sick suddenly, so it’s hard to finish the project on time. We asked another team member for help to complete it as quickly as possible. However, given the situation, we need to ask the manager if we can extend the deadline by one week."
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
    if "write_done" not in st.session_state:
        st.session_state.write_done = False
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
    st.session_state.write_done = False
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
    st_autorefresh(interval=1000, key="read_refresh")
    st.subheader("📄 Passage Reading (30s)")
    st.info(st.session_state.selected_passage)

    time_left = get_time_left(30)
    st.write(f"⏳ Time left: {time_left} seconds")

    if time_left <= 0:
        move_to_step("passage_write")

# 작성 공통 처리
def write_step(title, key_answer, next_step, response_type, prompt_text, show_info=None):
    total_time = 120
    time_left = get_time_left(total_time)

    if not st.session_state.write_done:
        st_autorefresh(interval=1000, key=f"{response_type}_refresh")

    st.subheader(title)
    st.markdown(prompt_text)
    if show_info:
        st.info(show_info)

    st.write(f"⏳ Time left: {time_left} seconds")

    disabled = st.session_state.write_done or time_left <= 0

    input_key = f"input_{key_answer}"
    input_value = st.text_area("Write here:", value=st.session_state.get(key_answer, ""), key=input_key, height=150, disabled=disabled)
    if not disabled:
        st.session_state[key_answer] = input_value

    def on_write_done():
        st.session_state[key_answer] = st.session_state.get(input_key, "").strip()
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
            if st.button("제출"):
                final_answer = st.session_state.get(key_answer, "").strip()
                post_to_google_sheets(final_answer, response_type)
                move_to_step(next_step)

# 단계: 지문 작성
def passage_write_step():
    write_step(
        "✍️ Reconstruct the Passage (120s)",
        "passage_answer",
        "email_write",
        "passage",
        "Use your own words to reconstruct the passage. **Do not copy the sentences or vocabulary directly.**"
    )

# 단계: 이메일 작성
def email_write_step():
    write_step(
        "📧 Email Writing (120s)",
        "email_answer",
        "done",
        "email",
        "Below is a situation. Based on it, write a professional and polite email that requests a one-week extension.",
        st.session_state.selected_email
    )

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
