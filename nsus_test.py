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
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "passage_answer" not in st.session_state:
        st.session_state.passage_answer = ""
    if "email_answer" not in st.session_state:
        st.session_state.email_answer = ""

initialize_session_state()

st.title("NSUS English Test")

# ========== 유틸 함수 ==========
def move_to_step(next_step):
    st.session_state.step = next_step
    st.session_state.submitted = False
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

def save_passage_answer():
    post_to_google_sheets(st.session_state["passage_answer"], "passage")

def save_email_answer():
    post_to_google_sheets(st.session_state["email_answer"], "email")

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

    st.markdown("<div id='read_timer'>Time left: 30 seconds</div>", unsafe_allow_html=True)

    js = """
    <script>
    var seconds = 30;
    var timer = document.getElementById("read_timer");
    var interval = setInterval(function() {
        seconds--;
        if (seconds <= 0) {
            clearInterval(interval);
            window.location.href = window.location.href + "&step=write";
        } else {
            timer.innerHTML = "Time left: " + seconds + " seconds";
        }
    }, 1000);
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)

def passage_write_step():
    st.subheader("✍️ Reconstruct the Passage (2 minutes)")
    st.markdown("Use your own words to reconstruct the passage. **Do not copy the sentences or vocabulary directly.**")

    st.markdown("""
    <div id="countdown_passage">Time left: 120 seconds</div>
    <script>
    var seconds = 120;
    var countdown = document.getElementById("countdown_passage");
    var textarea = document.getElementsByTagName("textarea")[0];
    var interval = setInterval(function() {
        seconds--;
        countdown.innerHTML = "Time left: " + seconds + " seconds";
        if (seconds <= 0) {
            clearInterval(interval);
            if (textarea) {
                textarea.setAttribute("readonly", true);
                textarea.style.backgroundColor = "#eee";
            }
        }
    }, 1000);
    </script>
    """, unsafe_allow_html=True)

    st.text_area("Write the passage from memory:", key="passage_answer", height=150)

    if st.button("Submit Answer"):
        save_passage_answer()
        move_to_step("email_write")

def email_write_step():
    st.subheader("📧 Email Writing (2 minutes)")
    st.markdown("Below is a situation. Based on it, write a professional and polite email that requests a one-week extension.")
    st.info(st.session_state.selected_email)

    st.markdown("""
    <div id="countdown_email">Time left: 120 seconds</div>
    <script>
    var seconds = 120;
    var countdown = document.getElementById("countdown_email");
    var textarea = document.getElementsByTagName("textarea")[0];
    var interval = setInterval(function() {
        seconds--;
        countdown.innerHTML = "Time left: " + seconds + " seconds";
        if (seconds <= 0) {
            clearInterval(interval);
            if (textarea) {
                textarea.setAttribute("readonly", true);
                textarea.style.backgroundColor = "#eee";
            }
        }
    }, 1000);
    </script>
    """, unsafe_allow_html=True)

    st.text_area("Write your email here:", key="email_answer", height=150)

    if st.button("Submit Answer"):
        save_email_answer()
        move_to_step("done")

def done_step():
    st.success("🎉 All tasks are complete! Well done!")

# ========== 실행 ==========
query_params = st.experimental_get_query_params()
if query_params.get("step") == ["write"]:
    move_to_step("passage_write")

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
