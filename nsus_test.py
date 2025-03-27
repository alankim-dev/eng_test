import streamlit as st
import time
import random
import requests
import json
from streamlit_autorefresh import st_autorefresh

# Google Sheets URL
go_url = "https://script.google.com/macros/s/AKfycbxHUtX406TMnBYKAk2MYwKsWpSn02FPC5hNfXWV6fx6eRO7vH5rn3rgXBlJ4-Ld3d95/exec"

# Passages and Emails
passages = [
    "Our new product line will be launched next month. We are planning a series of promotional events to increase awareness. All team members are expected to contribute ideas for marketing strategies. Please submit your suggestions by Friday afternoon.",
    "We have recently updated our internal communication guidelines to ensure that everyone stays informed and aligned. Managers are responsible for sharing weekly updates with their teams. Please check your email every Monday morning for the latest announcements and summaries.",
    "To improve cross-functional collaboration, we will be launching a new project management tool starting next week. Training sessions will be provided on Wednesday and Thursday. Attendance is mandatory for all team members who manage or participate in projects.",
    "The finance team is conducting the quarterly budget review, and all departments must submit their expense reports by the end of this week. Delayed submissions may result in your department's budget being frozen until the next quarter.",
    "Customer feedback has shown a strong interest in faster response times. To address this, we are adjusting our support team shifts starting Monday. Please review the updated schedule and confirm your availability with your manager by Friday."
]
email_situation = "One of our team members got sick suddenly, so it’s hard to finish the project on time. We asked another team member for help to complete it as quickly as possible. However, given the situation, we need to ask the manager if we can extend the deadline by one week."

# State Initialization
def init_state():
    st.session_state.setdefault("step", "intro")
    st.session_state.setdefault("selected_passage", random.choice(passages))
    st.session_state.setdefault("start_time", None)
    st.session_state.setdefault("write_done", False)
    st.session_state.setdefault("submitted", False)
    st.session_state.setdefault("passage_answer", "")
    st.session_state.setdefault("email_answer", "")

init_state()

# Utilities
def move_to(step):
    st.session_state.step = step
    st.session_state.start_time = time.time()
    st.session_state.write_done = False
    st.session_state.submitted = False
    st.rerun()

def time_left(limit):
    if not st.session_state.start_time:
        return limit
    return max(0, int(limit - (time.time() - st.session_state.start_time)))

def post_answer(text, typ):
    try:
        requests.post(go_url, data=json.dumps({"response": text.strip(), "type": typ}))
    except:
        st.error("Error saving answer.")

# Layout
st.title("NSUS English Test")

def intro():
    st.subheader("\U0001F4DD NSUS English Test")
    st.markdown("This is a two-part writing test including passage reconstruction and email writing.")
    if st.button("Start Test"):
        move_to("reading")

def reading():
    st_autorefresh(interval=1000, key="read_timer")
    st.subheader("\U0001F4D3 Passage Reading (30s)")
    st.info(st.session_state.selected_passage)
    st.write(f"\u23F3 Time left: {time_left(30)} seconds")
    if time_left(30) <= 0:
        move_to("passage")

def writing(label, answer_key, next_step, type_, show_instruction=True, show_passage=False):
    total = 120
    tl = time_left(total)
    st_autorefresh(interval=1000, key=f"{type_}_timer")

    st.subheader(f"{'\U0001F4DD' if type_ == 'passage' else '📧'} {label} ({total}s)")
    if show_instruction:
        if type_ == "passage":
            st.markdown("Use your own words to reconstruct the passage. **Do not copy the sentences or vocabulary directly.**")
        else:
            st.markdown("Below is a situation. Based on it, write a professional and polite email that requests a one-week extension.")
            st.info(email_situation)

    st.write(f"\u23F3 Time left: {tl} seconds")
    disabled = st.session_state.write_done or tl <= 0

    form = st.form(f"form_{type_}")
    input_value = form.text_area("Write here:", value=st.session_state[answer_key], height=150, disabled=disabled)

    js = """
    <script>
    const textarea = document.querySelector('textarea');
    if (textarea) {
        textarea.blur();
        setTimeout(() => {
            const btn = document.getElementById('done_btn');
            if (btn) btn.click();
        }, 300);
    }
    </script>
    """
    if tl <= 0 and not st.session_state.write_done:
        st.markdown(js, unsafe_allow_html=True)

    col1, col2 = form.columns([1, 1])

    with col1:
        form.form_submit_button(
            "작성 완료",
            on_click=lambda: done(answer_key, input_value),
            disabled=st.session_state.write_done,
            key="done_btn"
        )

    with col2:
        if st.session_state.write_done:
            submitted = form.form_submit_button("제출")
            if submitted:
                post_answer(st.session_state[answer_key], type_)
                move_to(next_step)

    form.form_submit_button("작성 완료", disabled=True, key="btn_duplicate")  # prevent double init

def done(answer_key, value):
    st.session_state[answer_key] = value.strip()
    st.session_state.write_done = True

def complete():
    st.success("🎉 All tasks are complete! Well done!")

# Routing
if st.session_state.step == "intro":
    intro()
elif st.session_state.step == "reading":
    reading()
elif st.session_state.step == "passage":
    writing("Reconstruct the Passage", "passage_answer", "email", "passage", show_instruction=True, show_passage=False)
elif st.session_state.step == "email":
    writing("Email Writing", "email_answer", "done", "email", show_instruction=True)
elif st.session_state.step == "done":
    complete()
