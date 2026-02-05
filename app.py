# ============================================================
# app.py — Smart Kids Daily Timetable Generator (FINAL FIXED)
# ============================================================

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
from joblib import load

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Kids Timetable",
    page_icon="📅",
    layout="wide"
)

st.title("🧠 Smart Kids Daily Timetable Generator")
st.markdown("AI-ready routine planner with **study + health + play balance**")

# ============================================================
# DATABASE CONFIGURATION (STREAMLIT CLOUD SAFE)
# ============================================================

try:
    MONGO_URI = st.secrets["MONGODB_URI"]
    DB_NAME = st.secrets["DB_NAME"]

    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")  # Force connection test

    db = client[DB_NAME]
    users_collection = db["users"]
    timetable_collection = db["timetables"]

except Exception as e:
    st.error(f"Mongo Error → {e}")
    st.stop()


# ============================================================
# OPTIONAL ML MODEL
# ============================================================

model = None
try:
    model = load("model.joblib")
except:
    model = None

# ============================================================
# USER INPUT FORM
# ============================================================

with st.form("main_form"):

    st.header("👶 Child Details")

    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Child Name", "Aman")
        age = st.number_input("Age", 5, 18, 10)

    with col2:
        grade = st.selectbox("Class", [str(i) for i in range(1, 11)])
        attention_span = st.slider("Attention Level", 0.5, 2.0, 1.0)

    with col3:
        days_remaining = st.number_input("Days till Exam", 1, 120, 14)
        max_daily_study = st.slider("Max Study Hours / Day", 1, 8, 4)

    st.divider()

    st.header("🛌 Sleep")

    sleep_hours = st.slider("Sleep Hours", 6.0, 10.0, 8.0, 0.5)
    sleep_start = st.selectbox("Sleep Start Hour", list(range(20, 24)))

    st.divider()

    st.header("📚 Subjects")

    subjects_input = st.text_area(
        "Subjects (Name:Marks:Chapters)",
        "Math:100:5\nScience:100:4\nEnglish:100:3"
    )

    submitted = st.form_submit_button("🚀 Generate Timetable")

# ============================================================
# HELPERS
# ============================================================

def parse_subjects(text):
    subjects = []
    for line in text.splitlines():
        try:
            name, marks, ch = line.split(":")
            subjects.append({
                "name": name.strip(),
                "chapters_remaining": int(ch)
            })
        except:
            pass
    return subjects


def in_sleep(hour, start, hrs):
    end = (start + int(hrs)) % 24
    return start <= hour < end if start < end else hour >= start or hour < end


def rule_scheduler(subjects):
    today = datetime.today().date()
    schedule = []

    for d in range(days_remaining):
        date = today + timedelta(days=d)
        hour = 7
        study_done = 0

        while hour < 22:
            if in_sleep(hour, sleep_start, sleep_hours):
                hour += 1
                continue

            if study_done < max_daily_study and subjects:
                subj = subjects[0]
                schedule.append({
                    "date": str(date),
                    "time": f"{hour}:00 - {hour+1}:00",
                    "subject": subj["name"],
                    "task": "Study"
                })
                subj["chapters_remaining"] -= 1
                study_done += 1
                if subj["chapters_remaining"] <= 0:
                    subjects.pop(0)
            else:
                schedule.append({
                    "date": str(date),
                    "time": f"{hour}:00 - {hour+1}:00",
                    "subject": "Free Time",
                    "task": "Rest"
                })

            hour += 1

    return schedule

# ============================================================
# MAIN LOGIC
# ============================================================

if submitted:

    subjects = parse_subjects(subjects_input)
    timetable = rule_scheduler(subjects.copy())

    df = pd.DataFrame(timetable)
    st.success("✅ Timetable Generated")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇️ Download JSON",
        json.dumps(timetable, indent=2),
        "timetable.json"
    )

    user_doc = {
        "name": name,
        "age": age,
        "grade": grade,
        "created_at": datetime.utcnow()
    }

    user_id = users_collection.insert_one(user_doc).inserted_id

    timetable_collection.insert_one({
        "user_id": str(user_id),
        "timetable": timetable,
        "created_at": datetime.utcnow()
    })

    st.success("📦 Timetable saved to MongoDB")

# ============================================================
# VIEW SAVED
# ============================================================

st.divider()
st.header("📂 Saved Timetables")

if st.button("Show Saved"):
    saved = list(timetable_collection.find().sort("created_at", -1))
    for item in saved:
        st.subheader(f"User ID: {item['user_id']}")
        st.dataframe(pd.DataFrame(item["timetable"]).head(20))

