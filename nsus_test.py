import streamlit as st
import time
import random
import requests
import json

# Google Sheets 연동 URL
GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbxHUtX406TMnBYKAk2MYwKsWpSn02FPC5hNfXWV6fx6eRO7vH5rn3rgXBlJ4-Ld3d95/exec"

# 지문 및 이메일
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

# 초기 상태
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

# 타이머 계산
def get_time_left(total_seconds):
    if st.session_state.start_time is None:
        return total_seconds
    elapsed = time.time() - st.session_state.start_time
    return int(total_seconds - elapsed)

# 단계 전환 함수
def move_to_step(next_step):
    st.session_state.step = next_step
    st.session_state.start_time = time.time()
    st.session_state.submitted = False
    st.rerun()

# 응답 저장
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

def save_passage_answer():
    post_to_google_sheets(st.session_state["passage_answer"], "passage")

def save_email_answer():
    post_to_google_sheets(st.session_state["email_answer"], "email")

# 단계: 인트로
def intro_step():
    st.subheader("📝 NSUS English Test")
    st.markdown("This is a two-part writing test including passage reconstruction and email writing.")
    if st.button("Start Test"):
        move_to_step("passage_read")

# 단계: 지문 읽기
def passage_read_step():
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000, limit=0)
    st.subheader("📄 Passage Reading (30 seconds)")
    st.markdown("You have **30 seconds** to read the passage. Then it will disappear.")
    st.info(st.session_state.selected_passage)

    time_left = get_time_left(30)
    st.write(f"⏳ Time left: **{time_left} seconds**")

    if time_left <= 0 and not st.session_state.submitted:
        st.session_state.submitted = True
        move_to_step("passage_write")

# 단계: 지문 작성
def passage_write_step():
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000, limit=0)
    st.subheader("✍️ Reconstruct the Passage (2 minutes)")
    st.markdown("Use your own words to reconstruct the passage. **Do not copy the sentences or vocabulary directly.**")

    time_left = get_time_left(120)
    disabled = time_left <= 0
    st.write(f"⏳ Time left: **{time_left} seconds**")

    if time_left <= 0 and not st.session_state.submitted:
        st.session_state.submitted = True
        save_passage_answer()
        move_to_step("email_write")

    st.text_area("Write the passage from memory:", key="passage_answer", height=150, disabled=disabled)

    if st.button("Submit Answer"):
        save_passage_answer()
        st.session_state.submitted = True
        st.success("✅ Passage answer submitted.")
        move_to_step("email_write")

# 단계: 이메일 작성
def email_write_step():
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000, limit=0)
    st.subheader("📧 Email Writing (2 minutes)")
    st.markdown("Based on the situation below, write a professional and polite email requesting a one-week extension.")
    st.info(st.session_state.selected_email)

    time_left = get_time_left(120)
    disabled = time_left <= 0
    st.write(f"⏳ Time left: **{time_left} seconds**")

    if time_left <= 0 and not st.session_state.submitted:
        st.session_state.submitted = True
        save_email_answer()
        move_to_step("done")

    st.text_area("Write your email here:", key="email_answer", height=150, disabled=disabled)

    if st.button("Submit Answer"):
        save_email_answer()
        st.session_state.submitted = True
        st.success("✅ Email answer submitted.")
        move_to_step("done")

# 단계: 완료
def done_step():
    st.success("🎉 All tasks are complete! Thank you for your effort!")

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
