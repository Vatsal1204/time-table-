# ============================================================
# app.py — Smart Kids Daily Timetable Generator (UPGRADED UI)
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

# ============================================================
# PAGE CONFIG (must be first)
# ============================================================

st.set_page_config(
    page_title="Smart Kids Timetable",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CUSTOM CSS — Vibrant, Playful, Premium Kids UI
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Poppins:wght@400;500;600;700&display=swap');

/* ── Root Variables ── */
:root {
    --bg: #0d1117;
    --card: #161b22;
    --card2: #1c2230;
    --border: #30363d;
    --accent1: #f78c40;
    --accent2: #4f8ef7;
    --accent3: #3dd68c;
    --accent4: #f75f8c;
    --accent5: #b57bee;
    --text: #e6edf3;
    --muted: #8b949e;
    --radius: 16px;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.main .block-container {
    padding: 2rem 3rem !important;
    max-width: 1100px !important;
}

/* ── Hide Streamlit defaults ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Hero Banner ── */
.hero {
    background: linear-gradient(135deg, #1a2340 0%, #1e1535 50%, #1a2340 100%);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(79,142,247,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: -40px;
    width: 160px; height: 160px;
    background: radial-gradient(circle, rgba(247,140,64,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero h1 {
    font-size: 2.4rem !important;
    font-weight: 900 !important;
    margin: 0 0 0.4rem 0 !important;
    background: linear-gradient(90deg, #f78c40, #f75f8c, #b57bee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero p {
    color: var(--muted);
    font-size: 1rem;
    margin: 0;
    font-weight: 600;
}

/* ── Section Cards ── */
.section-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
}
.section-title {
    font-size: 1.05rem;
    font-weight: 800;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-title span {
    font-size: 1.3rem;
}

/* ── Subject Grid ── */
.subject-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 0.75rem;
    margin-top: 0.5rem;
}
.subject-pill {
    background: var(--card2);
    border: 2px solid var(--border);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
    font-weight: 700;
    font-size: 0.9rem;
    position: relative;
}
.subject-pill:hover {
    border-color: var(--accent2);
    transform: translateY(-2px);
}
.subject-pill.selected {
    border-color: var(--accent3);
    background: rgba(61,214,140,0.1);
    color: var(--accent3);
}

/* ── Streamlit Widget Overrides ── */
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, var(--accent2), var(--accent5)) !important;
}
.stSelectbox > div > div {
    background: var(--card2) !important;
    border-color: var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: var(--card2) !important;
    border-color: var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 600 !important;
}
.stTextArea > div > div > textarea {
    background: var(--card2) !important;
    border-color: var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Nunito', sans-serif !important;
}
.stMultiSelect > div > div {
    background: var(--card2) !important;
    border-color: var(--border) !important;
    border-radius: 10px !important;
}
.stCheckbox > label {
    font-weight: 700 !important;
    font-size: 0.95rem !important;
}

/* ── Generate Button ── */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #f78c40, #f75f8c) !important;
    color: white !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.75rem 2.5rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px !important;
}
.stFormSubmitButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(247,92,140,0.35) !important;
}

/* ── Regular Buttons ── */
.stButton > button {
    background: var(--card2) !important;
    color: var(--accent2) !important;
    border: 2px solid var(--accent2) !important;
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: var(--accent2) !important;
    color: white !important;
}

/* ── Download Button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #3dd68c, #4f8ef7) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    width: 100% !important;
}

/* ── Dataframe ── */
.stDataFrame {
    border-radius: var(--radius) !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
}

/* ── Success / Info Alerts ── */
.stAlert {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-family: 'Nunito', sans-serif !important;
}

/* ── Divider ── */
hr {
    border-color: var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* ── Stat Badges ── */
.stat-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.stat-badge {
    background: var(--card2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.6rem 1.2rem;
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--muted);
}
.stat-badge b {
    color: var(--text);
    font-size: 1rem;
}

/* ── Routine toggles ── */
.toggle-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
}

/* Labels */
label, .stSlider label, .stSelectbox label,
.stNumberInput label, .stTextInput label,
.stTextArea label, .stMultiSelect label,
.stCheckbox label {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    color: var(--muted) !important;
    font-size: 0.88rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# OPTIONAL ML MODEL
# ============================================================

model = None
try:
    model = load("model.joblib")
except:
    pass

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "timetable_app")

mongo_ok = False
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000)
    client.server_info()
    db = client[DB_NAME]
    users_collection = db["users"]
    timetable_collection = db["timetables"]
    mongo_ok = True
except Exception as e:
    st.error(f"⚠️ Mongo Error → {e}")

# ============================================================
# HERO BANNER
# ============================================================

st.markdown("""
<div class="hero">
    <h1>🧠 Smart Kids Timetable</h1>
    <p>AI-powered daily routine planner &nbsp;·&nbsp; Study · Health · Play · Balance</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SUBJECT DEFINITIONS
# ============================================================

ALL_SUBJECTS = [
    {"name": "Maths",          "emoji": "🔢", "color": "#4f8ef7"},
    {"name": "Science",        "emoji": "🔬", "color": "#3dd68c"},
    {"name": "English",        "emoji": "📖", "color": "#f78c40"},
    {"name": "Hindi",          "emoji": "🇮🇳", "color": "#f75f8c"},
    {"name": "Gujarati",       "emoji": "🌸", "color": "#b57bee"},
    {"name": "Social Science", "emoji": "🌍", "color": "#f7c948"},
    {"name": "Computer",       "emoji": "💻", "color": "#40d4f7"},
    {"name": "Grammar",        "emoji": "✏️",  "color": "#f7834f"},
    {"name": "Moral Science",  "emoji": "🕊️",  "color": "#7bee8f"},
    {"name": "PT",             "emoji": "⚽",  "color": "#ee7baa"},
]

# ============================================================
# SUBJECT SELECTOR (outside form so it's interactive)
# ============================================================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title"><span>📚</span> Select Subjects</div>', unsafe_allow_html=True)
st.markdown("**Choose the subjects your child studies:**")

# Build a 5-column checkbox grid
cols = st.columns(5)
selected_subjects = []
for i, subj in enumerate(ALL_SUBJECTS):
    with cols[i % 5]:
        checked = st.checkbox(
            f"{subj['emoji']} {subj['name']}",
            value=subj["name"] in ["Maths", "Science", "English"],
            key=f"subj_{subj['name']}"
        )
        if checked:
            selected_subjects.append(subj["name"])

if not selected_subjects:
    st.warning("⚠️ Please select at least one subject!")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# MAIN FORM
# ============================================================

with st.form("main_form"):

    # ── Child Details ──────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span>👶</span> Child Details</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Child Name", "Aman")
        age  = st.number_input("Age", 5, 18, 10)
    with c2:
        grade = st.selectbox("Class / Standard", [str(i) for i in range(1, 11)])
        attention_span = st.slider("Attention Level", 0.5, 2.0, 1.0, 0.1)
    with c3:
        days_remaining  = st.number_input("Days till Exam", 1, 120, 14)
        max_daily_study = st.slider("Max Study Hours / Day", 1, 8, 4)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Sleep & Health ─────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span>🛌</span> Sleep & Health</div>', unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    with s1:
        sleep_hours = st.slider("Sleep Hours", 6.0, 10.0, 8.0, 0.5)
    with s2:
        sleep_start = st.selectbox("Bedtime (Hour)", list(range(20, 24)),
                                   format_func=lambda x: f"{x}:00")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Chapters per Subject ───────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span>📝</span> Chapters Remaining per Subject</div>', unsafe_allow_html=True)

    if selected_subjects:
        chap_cols = st.columns(min(len(selected_subjects), 5))
        chapter_map = {}
        for idx, sname in enumerate(selected_subjects):
            with chap_cols[idx % 5]:
                ch = st.number_input(sname, min_value=1, max_value=20, value=4, key=f"ch_{sname}")
                chapter_map[sname] = ch
    else:
        st.info("Select subjects above to set chapters.")
        chapter_map = {}

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Daily Routine ──────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span>⏰</span> Daily Routine Slots</div>', unsafe_allow_html=True)

    r1, r2, r3 = st.columns(3)
    with r1:
        include_breakfast = st.checkbox("🥣 Breakfast", True)
        include_lunch     = st.checkbox("🍱 Lunch", True)
    with r2:
        include_nap       = st.checkbox("😴 Nap Time", True)
        include_relax     = st.checkbox("🎵 Relax Time", True)
    with r3:
        include_games     = st.checkbox("⚽ Games / Sports", True)
        include_dinner    = st.checkbox("🍽️ Dinner", True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Family Event ───────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span>👨‍👩‍👧</span> Family Event</div>', unsafe_allow_html=True)

    family_event = st.checkbox("Any family event this week?")
    if family_event:
        fe1, fe2 = st.columns(2)
        with fe1:
            family_date = st.date_input("Event Date")
        with fe2:
            family_impact = st.selectbox("Impact on Schedule", ["low", "medium", "high"])

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Submit ─────────────────────────────────────────────
    submitted = st.form_submit_button("🚀 Generate My Timetable")

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def in_sleep(hour, sleep_start, sleep_hours):
    end = (sleep_start + int(sleep_hours)) % 24
    if sleep_start < end:
        return sleep_start <= hour < end
    return hour >= sleep_start or hour < end


def rule_scheduler(subjects):
    today = datetime.today().date()
    schedule = []

    routine_map = {}
    if include_breakfast: routine_map[8]  = "🥣 Breakfast"
    if include_lunch:     routine_map[13] = "🍱 Lunch"
    if include_nap:       routine_map[14] = "😴 Nap Time"
    if include_games:     routine_map[17] = "⚽ Games / Sports"
    if include_relax:     routine_map[18] = "🎵 Relax Time"
    if include_dinner:    routine_map[20] = "🍽️ Dinner"

    for d in range(days_remaining):
        date = today + timedelta(days=d)
        hour = 7
        study_done = 0

        subjs = sorted(subjects, key=lambda x: x["chapters_remaining"], reverse=True)

        while hour < 22:
            if in_sleep(hour, sleep_start, sleep_hours):
                hour += 1
                continue

            if hour in routine_map:
                schedule.append({
                    "📅 Date":    str(date),
                    "🕐 Time":    f"{hour}:00 – {hour+1}:00",
                    "📚 Subject": routine_map[hour],
                    "📋 Task":    "Routine"
                })
                hour += 1
                continue

            if study_done < max_daily_study and subjs:
                s = subjs[0]
                schedule.append({
                    "📅 Date":    str(date),
                    "🕐 Time":    f"{hour}:00 – {hour+1}:00",
                    "📚 Subject": s["name"],
                    "📋 Task":    f"Study — Ch. remaining: {s['chapters_remaining']}"
                })
                s["chapters_remaining"] -= 1
                study_done += 1
                if s["chapters_remaining"] <= 0:
                    subjs.pop(0)
            else:
                schedule.append({
                    "📅 Date":    str(date),
                    "🕐 Time":    f"{hour}:00 – {hour+1}:00",
                    "📚 Subject": "🌟 Free Time",
                    "📋 Task":    "Rest / Light Activity"
                })

            hour += 1

    return schedule

# ============================================================
# GENERATE TIMETABLE
# ============================================================

if submitted:
    if not selected_subjects:
        st.error("❌ Please select at least one subject before generating!")
    else:
        subjects = [
            {
                "name": s,
                "chapters_remaining": chapter_map.get(s, 4),
                "difficulty": "medium"
            }
            for s in selected_subjects
        ]

        timetable = rule_scheduler(subjects)
        df = pd.DataFrame(timetable)

        # ── Stats row ──
        total_days   = days_remaining
        study_slots  = len([r for r in timetable if r["📋 Task"] == "Study — Ch. remaining: 0" or "Study" in r["📋 Task"]])
        total_slots  = len(timetable)

        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-badge">📅 Days Planned <br><b>{total_days}</b></div>
            <div class="stat-badge">📚 Study Slots <br><b>{study_slots}</b></div>
            <div class="stat-badge">📋 Total Slots <br><b>{total_slots}</b></div>
            <div class="stat-badge">🧒 Child <br><b>{name}</b></div>
            <div class="stat-badge">🏫 Class <br><b>{grade}</b></div>
        </div>
        """, unsafe_allow_html=True)

        st.success(f"✅ Timetable generated for **{name}** — {total_slots} time slots across {total_days} days!")

        st.dataframe(df, use_container_width=True, height=420)

        c_dl1, c_dl2 = st.columns(2)
        with c_dl1:
            st.download_button(
                "⬇️ Download as JSON",
                data=json.dumps(timetable, indent=2),
                file_name=f"{name}_timetable.json",
                mime="application/json"
            )
        with c_dl2:
            st.download_button(
                "⬇️ Download as CSV",
                data=df.to_csv(index=False),
                file_name=f"{name}_timetable.csv",
                mime="text/csv"
            )

        # ── Save to MongoDB ──
        if mongo_ok:
            try:
                user_doc = {
                    "name": name, "age": age, "grade": grade,
                    "subjects": selected_subjects,
                    "created_at": str(datetime.now())
                }
                user_id = users_collection.insert_one(user_doc).inserted_id
                timetable_collection.insert_one({
                    "user_id": str(user_id),
                    "timetable": timetable,
                    "created_at": str(datetime.now())
                })
                st.success("📦 Timetable saved to MongoDB!")
            except Exception as e:
                st.warning(f"⚠️ Could not save to DB: {e}")

# ============================================================
# VIEW SAVED TIMETABLES
# ============================================================

st.markdown("---")

col_title, col_btn = st.columns([3, 1])
with col_title:
    st.markdown('<div class="section-title"><span>📂</span> Saved Timetables</div>', unsafe_allow_html=True)
with col_btn:
    show_saved = st.button("📂 Show Saved")

if show_saved:
    if not mongo_ok:
        st.error("❌ MongoDB not connected.")
    else:
        saved = list(timetable_collection.find().sort("created_at", -1).limit(5))
        if not saved:
            st.info("No saved timetables yet.")
        for item in saved:
            with st.expander(f"👤 User: {item.get('user_id', 'Unknown')} — {item.get('created_at', '')[:16]}"):
                st.dataframe(pd.DataFrame(item["timetable"]).head(30), use_container_width=True)
