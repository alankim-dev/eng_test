import streamlit as st
import time
import random
import requests
import json

# Google Apps Script 웹앱 URL
GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbxHUtX406TMnBYKAk2MYwKsWpSn02FPC5hNfXWV6fx6eRO7vH5rn3rgXBlJ4-Ld3d95/exec"

# ========== 예시 지문 및 이메일 과제 ==========
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

# ========== 초기 상태 설정 ==========
def initialize_session_state():
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

initialize_session_state()

st.title("NSUS English Test")

# ========== 유틸 함수 ==========
def get_time_left(total_seconds):
    if st.session_state.start_time is None:
        return total_seconds
    elapsed = time.time() - st.session_state.start_time
    return int(total_seconds - elapsed)

def move_to_step(next_step):
    st.session_state.step = next_step
    st.session_state.start_time = time.time()
    st.rerun()

def post_to_google_sheets(response_text, response_type):
    data = {
        "response": response_text.strip(),
        "type": response_type
    }
    try:
        r = requests.post(GOOGLE_SHEETS_URL, data=json.dumps(data))
        return r.json()
    except Exception as e:
        st.error(f"Error saving {response_type} answer: {e}")
        return None

# ========== 단계별 화면 ==========
def intro_step():
    st.subheader("📝 NSUS English Test")
    st.markdown("This is a two-part writing test including passage reconstruction and email writing.")
    if st.button("Start Test"):
        move_to_step("passage_read")

def passage_read_step():
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000, limit=0)

    st.subheader("📄 Passage Reconstruction (Reading)")
    st.markdown("You have **30 seconds** to read the passage. Then it will disappear.")
    st.info(st.session_state.selected_passage)

    time_left = get_time_left(30)
    if time_left < 0:
        time_left = 0
    st.write(f"⏳ Time left: **{time_left} seconds**")

    if time_left <= 0:
        move_to_step("passage_write")

def passage_write_step():
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000, limit=0)

    st.subheader("✍️ Reconstruct the Passage (2 minutes)")
    st.markdown("Use your own words to reconstruct the passage. **Do not copy the sentences or vocabulary directly.**")

    total_time = 120
    time_left = get_time_left(total_time)
    if time_left < 0:
        time_left = 0

    st.write(f"⏳ Time left: **{time_left} seconds**")
    disabled = time_left <= 0
    if disabled:
        st.warning("⏰ 시간이 종료되었습니다. 입력창은 비활성화되며 제출만 가능합니다.")

    with st.form("passage_form"):
        st.text_area("Write the passage from memory:", key="passage_answer", height=150, disabled=disabled)
        submitted = st.form_submit_button("Submit Answer")

        if submitted:
            post_to_google_sheets(st.session_state.get("passage_answer", "").strip(), "passage")
            move_to_step("email_write")

def email_write_step():
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000, limit=0)

    st.subheader("📧 Email Writing (2 minutes)")
    st.markdown("Below is a situation. Based on it, write a professional and polite email that requests a one-week extension.")
    st.info(st.session_state.selected_email)

    total_time = 120
    time_left = get_time_left(total_time)
    if time_left < 0:
        time_left = 0

    st.write(f"⏳ Time left: **{time_left} seconds**")
    disabled = time_left <= 0
    if disabled:
        st.warning("⏰ 시간이 종료되었습니다. 입력창은 비활성화되며 제출만 가능합니다.")

    with st.form("email_form"):
        st.text_area("Write your email here:", key="email_answer", height=150, disabled=disabled)
        submitted = st.form_submit_button("Submit Answer")

        if submitted:
            post_to_google_sheets(st.session_state.get("email_answer", "").strip(), "email")
            move_to_step("done")

def done_step():
    st.success("🎉 All tasks are complete! Well done!")

# ========== 실행 ==========
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
