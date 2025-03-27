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

initialize_session_state()

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

# 인트로 단계
def intro_step():
    st.title("NSUS English Test")
    st.subheader("\U0001F4DD NSUS English Test")
    st.markdown("This is a two-part writing test including passage reconstruction and email writing.")
    if st.button("Start Test"):
        move_to_step("passage_read")

# 읽기 단계
def passage_read_step():
    st_autorefresh(interval=1000, key="read_refresh")
    st.subheader("\U0001F4DC Passage Reading (30s)")
    st.info(st.session_state.selected_passage)
    time_left = get_time_left(30)
    st.write(f"\u23F3 Time left: {time_left} seconds")
    if time_left <= 0:
        move_to_step("passage_write")

# 작성 공통
def write_step(title, instruction, source_text, key_answer, next_step, response_type):
    total_time = 120
    time_left = get_time_left(total_time)
    if not st.session_state.write_done:
        st_autorefresh(interval=1000, key=f"{response_type}_refresh")

    st.subheader(title)
    st.markdown(instruction)
    if response_type == "passage":
        st.info(source_text)

    st.write(f"\u23F3 Time left: {time_left} seconds")
    disabled = st.session_state.write_done or time_left <= 0

    if not st.session_state.write_done:
        with st.form(f"form_{response_type}"):
            answer = st.text_area("Write here:", key=f"form_input_{response_type}", height=150, disabled=disabled)
            done = st.form_submit_button("작성 완료")
            if done:
                st.session_state[key_answer] = answer.strip()
                st.session_state.write_done = True

        # 타이머 만료 시 자동 제출
        if time_left <= 0:
            st.markdown("""
                <script>
                const textarea = document.querySelector('textarea');
                if (textarea) {
                    textarea.blur();
                    setTimeout(() => {
                        const btn = window.parent.document.querySelector("button[type='submit']");
                        if (btn) btn.click();
                    }, 300);
                }
                </script>
            """, unsafe_allow_html=True)
    else:
        st.text_area("Write here:", value=st.session_state.get(key_answer, ""), height=150, disabled=True)
        cols = st.columns([1, 1])
        with cols[0]:
            st.button("작성 완료", disabled=True)
        with cols[1]:
            if st.button("제출"):
                post_to_google_sheets(st.session_state.get(key_answer, ""), response_type)
                move_to_step(next_step)

# 작성 단계
def passage_write_step():
    write_step(
        "\u270D\uFE0F Reconstruct the Passage (120s)",
        "Use your own words to reconstruct the passage. **Do not copy the sentences or vocabulary directly.",
        st.session_state.selected_passage,
        "passage_answer",
        "email_write",
        "passage"
    )

def email_write_step():
    write_step(
        "\U0001F4E7 Email Writing (120s)",
        "Below is a situation. Based on it, write a professional and polite email that requests a one-week extension.",
        st.session_state.selected_email,
        "email_answer",
        "done",
        "email"
    )

# 완료 단계
def done_step():
    st.success("\U0001F389 All tasks are complete! Well done!")

# 실행
def main():
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

main()
