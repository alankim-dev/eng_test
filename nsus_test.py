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
    "The finance team is conducting the quarterly budget review, and all departments must submit their expense reports by Friday afternoon.",
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
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "passage_answer" not in st.session_state:
        st.session_state.passage_answer = ""
    if "email_answer" not in st.session_state:
        st.session_state.email_answer = ""

# ========== 유틸 함수들 ==========
def get_time_left(total_seconds):
    if st.session_state.start_time is None:
        return total_seconds
    elapsed = time.time() - st.session_state.start_time
    return int(total_seconds - elapsed)

def move_to_step(next_step):
    st.info(f"move_to_step() called with next_step: {next_step}")  # 디버깅
    st.session_state.step = next_step
    st.session_state.start_time = time.time()  # 새로운 단계마다 타이머 재설정
    st.session_state.submitted = False
    st.experimental_set_query_params()  # 쿼리 파라미터 초기화
    st.rerun()

def post_to_google_sheets(response_text, response_type):
    data = {
        "response": response_text.strip(),
        "type": response_type  # "passage" 또는 "email"
    }
    try:
        r = requests.post(GOOGLE_SHEETS_URL, data=json.dumps(data))
        return r.json()
    except Exception as e:
        st.error(f"Error saving {response_type} answer: {e}")
        return None

def save_passage_answer():
    post_to_google_sheets(st.session_state.get("passage_answer", ""), "passage")

def save_email_answer():
    post_to_google_sheets(st.session_state.get("email_answer", ""), "email")

# ========== 단계별 로직 ==========
def intro_step():
    st.subheader("📝 NSUS English Test")
    st.markdown("This is a two-part writing test including passage reconstruction and email writing.")
    if st.button("Start Test"):
        move_to_step("passage_read")

def passage_read_step():
    # Passage Reading 단계는 기존과 동일하게 서버 사이드 타이머 사용
    st.experimental_rerun()  # 자동 새로고침 대신 이 단계에서는 간단하게 진행
    st.subheader("📄 Passage Reconstruction (Reading)")
    st.markdown("You have **30 seconds** to read the passage. Then it will disappear.")
    st.info(st.session_state.selected_passage)

    # 타이머 시작
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    time_left = get_time_left(30)
    if time_left < 0:
        time_left = 0
    st.write(f"Time left: **{time_left}** seconds")

    if time_left <= 0 and not st.session_state.submitted:
        st.session_state.submitted = True
        move_to_step("passage_write")

def passage_write_step():
    st.subheader("✍️ Reconstruct the Passage (2 minutes)")
    st.markdown("Use your own words to reconstruct the passage. **Do not copy the sentences or vocabulary directly.**")

    total_time = 120  # 2분 = 120초
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    # 클라이언트 사이드 JS 타이머 삽입 (passage 단계)
    st.markdown(f"""
    <div id="passage_timer" style="font-size:20px; font-weight:bold;">Time left: <span id="passage_timer_val">{total_time}</span> seconds</div>
    <script>
      var passageTimeLeft = {total_time};
      var passageTimerId = setInterval(function() {{
        if(passageTimeLeft > 0){{
          passageTimeLeft--;
          document.getElementById("passage_timer_val").innerText = passageTimeLeft;
        }}
        if(passageTimeLeft <= 0){{
          clearInterval(passageTimerId);
          // 시간이 다 되었을 때 URL에 쿼리 파라미터를 추가해 자동 제출 신호 전달
          window.location.href = window.location.pathname + "?auto_submit_passage=true";
        }}
      }}, 1000);
    </script>
    """, unsafe_allow_html=True)

    passage_answer = st.text_area("Write the passage from memory:", key="passage_answer", height=150)

    if st.button("Submit Answer", key="submit_passage"):
        save_passage_answer()
        st.session_state.submitted = True
        st.success("✅ Passage answer has been submitted.")
        move_to_step("email_write")

    # URL 쿼리 파라미터에 auto_submit_passage가 있으면 자동 제출 처리
    params = st.experimental_get_query_params()
    if params.get("auto_submit_passage") and not st.session_state.submitted:
        st.session_state.submitted = True
        save_passage_answer()
        move_to_step("email_write")

def email_write_step():
    st.subheader("📧 Email Writing (2 minutes)")
    st.markdown("Below is a situation. Based on it, write a professional and polite email that requests a one-week extension.")
    st.info(st.session_state.selected_email)

    total_time = 120  # 2분 = 120초
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()
    # 클라이언트 사이드 JS 타이머 삽입 (email 단계)
    st.markdown(f"""
    <div id="email_timer" style="font-size:20px; font-weight:bold;">Time left: <span id="email_timer_val">{total_time}</span> seconds</div>
    <script>
      var emailTimeLeft = {total_time};
      var emailTimerId = setInterval(function() {{
        if(emailTimeLeft > 0){{
          emailTimeLeft--;
          document.getElementById("email_timer_val").innerText = emailTimeLeft;
        }}
        if(emailTimeLeft <= 0){{
          clearInterval(emailTimerId);
          window.location.href = window.location.pathname + "?auto_submit_email=true";
        }}
      }}, 1000);
    </script>
    """, unsafe_allow_html=True)

    email_answer = st.text_area("Write your email here:", key="email_answer", height=150)

    if st.button("Submit Answer", key="submit_email"):
        save_email_answer()
        st.session_state.submitted = True
        st.success("✅ Email answer has been submitted.")
        move_to_step("done")

    # URL 쿼리 파라미터에 auto_submit_email가 있으면 자동 제출 처리
    params = st.experimental_get_query_params()
    if params.get("auto_submit_email") and not st.session_state.submitted:
        st.session_state.submitted = True
        save_email_answer()
        move_to_step("done")

def done_step():
    st.success("🎉 All tasks are complete! Well done!")

# ========== 단계별 실행 ==========
def main():
    initialize_session_state()
    st.title("NSUS English Test")
    st.info(f"Current step: {st.session_state.step}")
    
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

if __name__ == "__main__":
    main()
