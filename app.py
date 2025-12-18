# ============================================================
# app.py — Smart Kids Daily Timetable Generator (FINAL)
# ============================================================

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from joblib import load
import math
from pymongo import MongoClient
import streamlit as st

MONGO_URI = st.secrets["MONGODB_URI"]
DB_NAME = st.secrets["DB_NAME"]

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

timetable_collection = db["timetables"]
users_collection = db["users"]


# ============================================================
# OPTIONAL ML MODEL LOADING
# ============================================================

model = None
try:
    model = load("model.joblib")
except Exception as e:
    model = None
    print("ML model not loaded, using rule-based scheduler")

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

import streamlit as st
from pymongo import MongoClient

MONGO_URI = st.secrets["MONGODB_URI"]
DB_NAME = st.secrets["DB_NAME"]

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

timetable_collection = db["timetables"]


# ============================================================
# PAGE CONFIG & STYLING
# ============================================================

st.set_page_config(
    page_title="Smart Kids Timetable",
    page_icon="📅",
    layout="wide"
)

st.markdown("""
<style>
.main { background-color: #0f172a; color: white; }
.stButton>button { background-color: #2563eb; color: white; }
.stSelectbox, .stTextInput, .stNumberInput, .stSlider {
    background-color: #020617;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Smart Kids Daily Timetable Generator")
st.markdown("AI-ready routine planner with **study + health + play balance**")

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
        grade = st.selectbox("Class / Standard", [str(i) for i in range(1, 11)])
        attention_span = st.slider("Attention Level", 0.5, 2.0, 1.0)

    with col3:
        days_remaining = st.number_input("Days till Exam", 1, 120, 14)
        max_daily_study = st.slider("Max Study Hours / Day", 1, 8, 4)

    st.divider()

    # --------------------------------------------------------
    # SLEEP & HEALTH
    # --------------------------------------------------------

    st.header("🛌 Sleep & Health")

    col4, col5 = st.columns(2)
    with col4:
        sleep_hours = st.slider("Sleep Hours", 6.0, 10.0, 8.0, 0.5)
    with col5:
        sleep_start = st.selectbox("Sleep Start Hour", list(range(20, 24)))

    st.divider()

    # --------------------------------------------------------
    # DAILY ROUTINE TOGGLES
    # --------------------------------------------------------

    st.header("⏰ Daily Routine Slots")

    col6, col7, col8 = st.columns(3)

    with col6:
        include_breakfast = st.checkbox("Breakfast", True)
        include_lunch = st.checkbox("Lunch", True)

    with col7:
        include_nap = st.checkbox("Nap Time", True)
        include_relax = st.checkbox("Relax Time", True)

    with col8:
        include_games = st.checkbox("Games / Sports", True)
        include_dinner = st.checkbox("Dinner", True)

    st.divider()

    # --------------------------------------------------------
    # SUBJECTS
    # --------------------------------------------------------

    st.header("📚 Subjects")

    base_subjects = [
        "Math", "Science", "English", "Hindi",
        "Gujarati", "Social Science", "Computer", "Sanskrit"
    ]

    chosen_subjects = st.multiselect(
        "Choose Subjects",
        base_subjects,
        default=["Math", "Science", "English"]
    )

    subjects_input = st.text_area(
        "Custom Subjects (Name:Marks:Chapters)",
        value="Math:100:5\nScience:100:4\nEnglish:100:3"
    )

    st.divider()

    # --------------------------------------------------------
    # FAMILY EVENT
    # --------------------------------------------------------

    st.header("👨‍👩‍👧 Family Events")

    family_event = st.checkbox("Any family event?")
    family_date = None
    family_impact = "low"

    if family_event:
        family_date = st.date_input("Event Date")
        family_impact = st.selectbox("Impact", ["low", "medium", "high"])

    submitted = st.form_submit_button("🚀 Generate Timetable")

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def parse_subjects(text):
    subjects = []
    for line in text.splitlines():
        if ":" not in line:
            continue
        try:
            name, marks, ch = line.split(":")
            subjects.append({
                "name": name.strip(),
                "max_marks": int(marks),
                "chapters_remaining": int(ch),
                "difficulty": "medium"
            })
        except:
            pass
    return subjects


def merge_subjects(preset, custom):
    merged = {}
    for s in preset + custom:
        key = s["name"]
        if key not in merged:
            merged[key] = s
        else:
            merged[key]["chapters_remaining"] += s["chapters_remaining"]
    return list(merged.values())


def in_sleep(hour, sleep_start, sleep_hours):
    end = (sleep_start + int(sleep_hours)) % 24
    if sleep_start < end:
        return sleep_start <= hour < end
    return hour >= sleep_start or hour < end


# ============================================================
# RULE-BASED SCHEDULER (CORE LOGIC)
# ============================================================

def rule_scheduler(subjects):
    today = datetime.today().date()
    schedule = []

    routine_slots = {
        "Breakfast": 8 if include_breakfast else None,
        "Lunch": 13 if include_lunch else None,
        "Nap": 14 if include_nap else None,
        "Games": 17 if include_games else None,
        "Relax": 18 if include_relax else None,
        "Dinner": 20 if include_dinner else None
    }

    routine_slots = {k: v for k, v in routine_slots.items() if v is not None}

    for d in range(days_remaining):
        date = today + timedelta(days=d)
        hour = 7
        study_done = 0

        subjects_sorted = sorted(
            subjects,
            key=lambda x: x["chapters_remaining"],
            reverse=True
        )

        while hour < 22:

            if in_sleep(hour, sleep_start, sleep_hours):
                hour += 1
                continue

            if hour in routine_slots.values():
                routine = list(routine_slots.keys())[
                    list(routine_slots.values()).index(hour)
                ]
                schedule.append({
                    "date": str(date),
                    "time": f"{hour}:00 - {hour+1}:00",
                    "subject": routine,
                    "task": f"{routine} Time"
                })
                hour += 1
                continue

            if study_done < max_daily_study and subjects_sorted:
                subj = subjects_sorted[0]
                schedule.append({
                    "date": str(date),
                    "time": f"{hour}:00 - {hour+1}:00",
                    "subject": subj["name"],
                    "task": "Study"
                })
                subj["chapters_remaining"] -= 1
                study_done += 1
                if subj["chapters_remaining"] <= 0:
                    subjects_sorted.pop(0)
            else:
                schedule.append({
                    "date": str(date),
                    "time": f"{hour}:00 - {hour+1}:00",
                    "subject": "Free Time",
                    "task": "Rest / Light Activity"
                })

            hour += 1

    return schedule

# ============================================================
# MAIN EXECUTION
# ============================================================

if submitted:

    preset_subjects = [{
        "name": s,
        "max_marks": 100,
        "chapters_remaining": 3,
        "difficulty": "medium"
    } for s in chosen_subjects]

    custom_subjects = parse_subjects(subjects_input)
    subjects = merge_subjects(preset_subjects, custom_subjects)

    timetable = rule_scheduler(subjects)

    df = pd.DataFrame(timetable)
    st.success("✅ Timetable Generated")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇️ Download JSON",
        data=json.dumps(timetable, indent=2),
        file_name="timetable.json"
    )

    # --------------------------------------------------------
    # SAVE TO DATABASE
    # --------------------------------------------------------

    user_doc = {
        "name": name,
        "age": age,
        "grade": grade,
        "created_at": str(datetime.now())
    }

    user_id = users_collection.insert_one(user_doc).inserted_id

    timetable_collection.insert_one({
        "user_id": str(user_id),
        "timetable": timetable,
        "created_at": str(datetime.now())
    })

    st.success("📦 Timetable saved to MongoDB")

# ============================================================
# VIEW SAVED TIMETABLES
# ============================================================

st.divider()
st.header("📂 Saved Timetables")

if st.button("Show Saved"):
    saved = list(timetable_collection.find().sort("created_at", -1))
    for item in saved:
        st.subheader(f"User ID: {item['user_id']}")
        st.dataframe(pd.DataFrame(item["timetable"]).head(20))



