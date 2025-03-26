import streamlit as st
import time
import random
from streamlit_autorefresh import st_autorefresh

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

# Test 제목 변경
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

def save_passage_answer():
    with open("passage_answers.txt", "a", encoding="utf-8") as f:
        f.write(st.session_state["passage_answer"].strip() + "\t" + time.strftime("%Y-%m-%d %H:%M:%S") + "\n")

def save_email_answer():
    with open("email_answers.txt", "a", encoding="utf-8") as f:
        f.write(st.session_state["email_answer"].strip() + "\t" + time.strftime("%Y-%m-%d %H:%M:%S") + "\n")

# ========== 단계별 로직 ==========

def intro_step():
    st.subheader("📝 NSUS English Test")
    st.markdown("This is a two-part writing test including passage reconstruction and email writing.")
    if st.button("Start Test"):
        move_to_step("passage_read")

def passage_read_step():
    st_autorefresh(interval=1000, limit=0)  # 1초마다 새로고침
    st.subheader("📄 Passage Reconstruction (Reading)")
    st.markdown("You have **30 seconds** to read the passage. Then it will disappear.")
    st.info(st.session_state.selected_passage)
    
    time_left = get_time_left(30)
    if time_left < 0:
        time_left = 0
    st.write(f"Time left: **{time_left}** seconds")
    
    # 시간이 다 되면 자동으로 다음 단계로 이동
    if time_left <= 0 and not st.session_state.submitted:
        st.session_state.submitted = True
        move_to_step("passage_write")
        st.stop()

def passage_write_step():
    st_autorefresh(interval=1000, limit=0)
    st.subheader("✍️ Reconstruct the Passage (2 minutes)")
    st.markdown("Use your own words to reconstruct the passage. **Do not copy the sentences or vocabulary directly.**")
    
    time_left = get_time_left(120)  # 2분 = 120초
    if time_left < 0:
        time_left = 0
    st.write(f"Time left: **{time_left}** seconds")
    
    # 입력창은 제한 시간이 남아있으면 활성, 만료되면 비활성화
    disabled_flag = (time_left <= 0)
    st.text_area("Write the passage from memory:", key="passage_answer", height=150, disabled=disabled_flag)
    
    if disabled_flag and not st.session_state.submitted:
        st.info("Time is up! The response area is now disabled. Please click [Submit Answer] to submit your response.")
    
    if st.button("Submit Answer") and not st.session_state.submitted:
        save_passage_answer()
        st.session_state.submitted = True
        st.success("✅ Passage answer has been submitted.")
        move_to_step("email_write")
        st.stop()

def email_write_step():
    st_autorefresh(interval=1000, limit=0)
    st.subheader("📧 Email Writing (2 minutes)")
    st.markdown("Below is a situation. Based on it, write a professional and polite email that requests a one-week extension.")
    st.info(st.session_state.selected_email)
    
    time_left = get_time_left(120)  # 2분 = 120초
    if time_left < 0:
        time_left = 0
    st.write(f"Time left: **{time_left}** seconds")
    
    disabled_flag = (time_left <= 0)
    st.text_area("Write your email here:", key="email_answer", height=150, disabled=disabled_flag)
    
    if disabled_flag and not st.session_state.submitted:
        st.info("Time is up! The email input is disabled. Please click [Submit Answer] to submit your response.")
    
    if st.button("Submit Answer") and not st.session_state.submitted:
        save_email_answer()
        st.session_state.submitted = True
        st.success("✅ Email answer has been submitted.")
        move_to_step("done")
        st.stop()

def done_step():
    st.success("🎉 All tasks are complete! Well done!")

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
