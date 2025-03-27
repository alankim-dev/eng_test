import streamlit as st
import time
import random
import requests
import json
from streamlit_autorefresh import st_autorefresh

GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbxHUtX406TMnBYKAk2MYwKsWpSn02FPC5hNfXWV6fx6eRO7vH5rn3rgXBlJ4-Ld3d95/exec"

passages = [
    "Our new product line will be launched next month. We are planning a series of promotional events to increase awareness. All team members are expected to contribute ideas for marketing strategies. Please submit your suggestions by Friday afternoon.",
    "We have recently updated our internal communication guidelines to ensure that everyone stays informed and aligned. Managers are responsible for sharing weekly updates with their teams. Please check your email every Monday morning for the latest announcements and summaries.",
    "To improve cross-functional collaboration, we will be launching a new project management tool starting next week. Training sessions will be provided on Wednesday and Thursday. Attendance is mandatory for all team members who manage or participate in projects.",
    "The finance team is conducting the quarterly budget review, and all departments must submit their expense reports by the end of this week. Delayed submissions may result in your department's budget being frozen until the next quarter.",
    "Customer feedback has shown a strong interest in faster response times. To address this, we are adjusting our support team shifts starting Monday. Please review the updated schedule and confirm your availability with your manager by Friday."
]

email_task = "One of our team members got sick suddenly, so it’s hard to finish the project on time. We asked another team member for help to complete it as quickly as possible. However, given the situation, we need to ask the manager if we can extend the deadline by one week."


def initialize():
    if "step" not in st.session_state:
        st.session_state.step = "intro"
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()
    if "write_done" not in st.session_state:
        st.session_state.write_done = False
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "passage" not in st.session_state:
        st.session_state.passage = random.choice(passages)
    if "passage_answer" not in st.session_state:
        st.session_state.passage_answer = ""
    if "email_answer" not in st.session_state:
        st.session_state.email_answer = ""


def move_to(step):
    st.session_state.step = step
    st.session_state.start_time = time.time()
    st.session_state.write_done = False
    st.session_state.submitted = False
    st.rerun()


def get_time_left(limit):
    return max(0, int(limit - (time.time() - st.session_state.start_time)))


def post_to_google_sheets(answer, answer_type):
    data = {"response": answer.strip(), "type": answer_type}
    try:
        requests.post(GOOGLE_SHEETS_URL, data=json.dumps(data))
    except:
        st.error("Error saving response.")


def passage_read():
    st_autorefresh(interval=1000, key="read_refresh")
    st.subheader("📄 Passage Reading (30s)")
    st.markdown(
        "Use your own words to reconstruct the passage. **Do not copy the sentences or vocabulary directly.**"
    )
    st.info(st.session_state.passage)
    if get_time_left(30) <= 0:
        move_to("passage_write")
    st.write(f"⏳ Time left: {get_time_left(30)} seconds")


def write_form(title, prompt, key_answer, next_step, answer_type):
    time_left = get_time_left(120)
    if not st.session_state.write_done:
        st_autorefresh(interval=1000, key=f"{answer_type}_refresh")

    st.subheader(title)
    st.markdown(prompt)
    st.write(f"⏳ Time left: {time_left} seconds")

    disabled = st.session_state.write_done or time_left <= 0
    with st.form(f"{answer_type}_form"):
        answer = st.text_area(
            "Write here:",
            value=st.session_state.get(key_answer, ""),
            key=f"{key_answer}_form_input",
            height=150,
            disabled=disabled
        )
        submitted = st.form_submit_button("작성 완료")
        if submitted:
            st.session_state[key_answer] = answer.strip()
            st.session_state.write_done = True
            st.rerun()

    # 타이머 만료 시 JS로 자동 클릭
    if time_left <= 0 and not st.session_state.write_done:
        st.markdown("""
            <script>
            const textarea = document.querySelector('textarea');
            if (textarea) {
                textarea.blur();
                setTimeout(() => {
                    document.querySelector('button[kind="formSubmit"]')?.click();
                }, 300);
            }
            </script>
        """, unsafe_allow_html=True)

    if st.session_state.write_done:
        cols = st.columns([1, 1])
        with cols[0]:
            st.button("작성 완료", disabled=True)
        with cols[1]:
            if st.button("제출"):
                final = st.session_state.get(key_answer, "").strip()
                post_to_google_sheets(final, answer_type)
                move_to(next_step)


initialize()
st.title("NSUS English Test")

if st.session_state.step == "intro":
    st.subheader("📝 NSUS English Test")
    st.markdown("This is a two-part writing test including passage reconstruction and email writing.")
    if st.button("Start Test"):
        move_to("passage_read")

elif st.session_state.step == "passage_read":
    passage_read()

elif st.session_state.step == "passage_write":
    write_form(
        "✍️ Reconstruct the Passage (120s)",
        "Use your own words to reconstruct the passage. **Do not copy the sentences or vocabulary directly.**",
        "passage_answer", "email_write", "passage"
    )

elif st.session_state.step == "email_write":
    write_form(
        "📧 Email Writing (120s)",
        "Below is a situation. Based on it, write a professional and polite email that requests a one-week extension.\n\n> " + email_task,
        "email_answer", "done", "email"
    )

elif st.session_state.step == "done":
    st.success("🎉 All tasks are complete! Well done!")
