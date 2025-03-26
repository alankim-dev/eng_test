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
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    # 입력값은 위젯 key에 의해 자동 저장됨.
    if "passage_answer" not in st.session_state:
        st.session_state.passage_answer = ""
    if "email_answer" not in st.session_state:
        st.session_state.email_answer = ""

initialize_session_state()

st.title("NSUS English Test")

# ========== 유틸 함수들 ==========
def get_time_left(total_seconds):
    if st.session_state.start_time is None:
        return total_seconds
    elapsed = time.time() - st.session_state.start_time
    return int(total_seconds - elapsed)

def move_to_step(next_step):
    st.session_state.step = next_step
    st.session_state.start_time = time.time()
    st.session_state.submitted = False
    st.rerun()  # 즉시 화면 전환

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
    post_to_google_sheets(st.session_state["passage_answer"], "passage")

def save_email_answer():
    post_to_google_sheets(st.session_state["email_answer"], "email")

# ========== 단계별 로직 ==========

def intro_step():
    st.subheader("📝 NSUS English Test")
    st.markdown("This is a two-part writing test including passage reconstruction and email writing.")
    if st.button("Start Test"):
        move_to_step("passage_read")

def passage_read_step():
    # 기존 autorefresh 사용 (여기서는 서버 측 refresh로 충분)
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000, limit=0)
    st.subheader("📄 Passage Reconstruction (Reading)")
    st.markdown("You have **30 seconds** to read the passage. Then it will disappear.")
    st.info(st.session_state.selected_passage)
    
    time_left = get_time_left(30)
    if time_left < 0:
        time_left = 0
    st.write(f"Time left: **{time_left}** seconds")
    
    if time_left <= 0 and not st.session_state.submitted:
        st.session_state.submitted = True
        move_to_step("passage_write")

def passage_write_step():
    # 여기서는 자바스크립트를 사용하여 타이머 카운트다운과 자동 제출 버튼 클릭 구현
    st.subheader("✍️ Reconstruct the Passage (2 minutes)")
    st.markdown("Use your own words to reconstruct the passage. **Do not copy the sentences or vocabulary directly.**")
    
    total_time = 120  # 2분
    # 카운트다운을 표시할 div 생성
    st.markdown(f"<div id='countdown_passage'>Time left: {total_time} seconds</div>", unsafe_allow_html=True)
    # 자바스크립트로 카운트다운 후, 숨겨진 제출 버튼을 클릭하도록 함
    js_code = f"""
    <script>
    var timeLeft = {total_time};
    var countdownElem = document.getElementById('countdown_passage');
    var interval = setInterval(function(){{
         timeLeft--;
         countdownElem.innerHTML = "Time left: " + timeLeft + " seconds";
         if(timeLeft <= 0){{
             clearInterval(interval);
             document.getElementById('hidden_submit_passage').click();
         }}
    }}, 1000);
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)
    
    st.text_area("Write the passage from memory:", key="passage_answer", height=150)
    
    # 숨겨진 제출 버튼 (보이지 않도록 스타일 설정)
    submit_html = """
    <style>
    #hidden_submit_passage {display: none;}
    </style>
    """
    st.markdown(submit_html, unsafe_allow_html=True)
    
    if st.button("Submit Answer", key="hidden_submit_passage"):
        save_passage_answer()
        st.session_state.submitted = True
        st.success("✅ Passage answer has been submitted.")
        move_to_step("email_write")

def email_write_step():
    st.subheader("📧 Email Writing (2 minutes)")
    st.markdown("Below is a situation. Based on it, write a professional and polite email that requests a one-week extension.")
    st.info(st.session_state.selected_email)
    
    total_time = 120  # 2분
    st.markdown(f"<div id='countdown_email'>Time left: {total_time} seconds</div>", unsafe_allow_html=True)
    js_code_email = f"""
    <script>
    var timeLeftEmail = {total_time};
    var countdownElemEmail = document.getElementById('countdown_email');
    var intervalEmail = setInterval(function(){{
         timeLeftEmail--;
         countdownElemEmail.innerHTML = "Time left: " + timeLeftEmail + " seconds";
         if(timeLeftEmail <= 0){{
             clearInterval(intervalEmail);
             document.getElementById('hidden_submit_email').click();
         }}
    }}, 1000);
    </script>
    """
    st.markdown(js_code_email, unsafe_allow_html=True)
    
    st.text_area("Write your email here:", key="email_answer", height=150)
    
    submit_html_email = """
    <style>
    #hidden_submit_email {display: none;}
    </style>
    """
    st.markdown(submit_html_email, unsafe_allow_html=True)
    
    if st.button("Submit Answer", key="hidden_submit_email"):
        save_email_answer()
        st.session_state.submitted = True
        st.success("✅ Email answer has been submitted.")
        move_to_step("done")

def done_step():
    st.success("🎉 All tasks are complete! Well done!")
    # 완료 단계에서는 자바스크립트 타이머 없음

# ========== 단계별 실행 ==========
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
