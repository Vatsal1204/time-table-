# ============================================================
# app.py — Smart Kids Daily Timetable Generator (UPGRADED UI)
# ============================================================

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta, date
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from joblib import load
import math
import calendar

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
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Poppins:wght@400;500;600;700&display=swap');

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

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.main .block-container {
    padding: 2rem 3rem !important;
    max-width: 1100px !important;
}

#MainMenu, footer, header { visibility: hidden; }

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
.hero h1 {
    font-size: 2.4rem !important;
    font-weight: 900 !important;
    margin: 0 0 0.4rem 0 !important;
    background: linear-gradient(90deg, #f78c40, #f75f8c, #b57bee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero p { color: var(--muted); font-size: 1rem; margin: 0; font-weight: 600; }

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
.section-title span { font-size: 1.3rem; }

/* Calendar */
.cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    margin-top: 0.5rem;
    max-width: 420px;
}
.cal-day-label {
    text-align: center;
    font-size: 0.65rem;
    font-weight: 800;
    color: var(--muted);
    text-transform: uppercase;
    padding: 4px 0 6px 0;
    letter-spacing: 0.5px;
}
.cal-day {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background: transparent;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--text);
    margin: 0 auto;
}
.cal-day.selected {
    background: linear-gradient(135deg, #f78c40, #f75f8c);
    color: white;
    box-shadow: 0 2px 8px rgba(247,92,140,0.45);
}
.cal-day.today {
    border: 2px solid var(--accent2);
    color: var(--accent2);
}
.cal-day.empty { background: transparent; }
.cal-day.past  { opacity: 0.28; }

.event-row {
    background: var(--card2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
}

.stat-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.stat-badge {
    background: var(--card2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.6rem 1.2rem;
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--muted);
}
.stat-badge b { color: var(--text); font-size: 1rem; }

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
.stCheckbox > label { font-weight: 700 !important; font-size: 0.95rem !important; }

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
}
.stButton > button {
    background: var(--card2) !important;
    color: var(--accent2) !important;
    border: 2px solid var(--accent2) !important;
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
}
.stButton > button:hover { background: var(--accent2) !important; color: white !important; }
.stDownloadButton > button {
    background: linear-gradient(135deg, #3dd68c, #4f8ef7) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important; width: 100% !important;
}
.stDataFrame { border-radius: var(--radius) !important; overflow: hidden !important; }
.stAlert { border-radius: 12px !important; font-weight: 700 !important; font-family: 'Nunito', sans-serif !important; }
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

label, .stSlider label, .stSelectbox label,
.stNumberInput label, .stTextInput label,
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
# ML MODEL
# ============================================================
model = None
try:
    model = load("model.joblib")
except:
    pass

# ============================================================
# DATABASE
# ============================================================
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME", "timetable_app")

mongo_ok = False
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000)
    client.server_info()
    db = client[DB_NAME]
    users_collection     = db["users"]
    timetable_collection = db["timetables"]
    mongo_ok = True
except Exception as e:
    st.error(f"⚠️ Mongo Error → {e}")

# ============================================================
# SESSION STATE
# ============================================================
if "family_events" not in st.session_state:
    st.session_state.family_events = {}   # { "YYYY-MM-DD": {"impact": str, "hours": int} }
if "cal_offset" not in st.session_state:
    st.session_state.cal_offset = 0

# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="hero">
    <h1>🧠 Smart Kids Timetable</h1>
    <p>AI-powered daily routine planner &nbsp;·&nbsp; Study · Health · Play · Balance</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SUBJECTS
# ============================================================
ALL_SUBJECTS = [
    {"name": "Maths",          "emoji": "🔢"},
    {"name": "Science",        "emoji": "🔬"},
    {"name": "English",        "emoji": "📖"},
    {"name": "Hindi",          "emoji": "🇮🇳"},
    {"name": "Gujarati",       "emoji": "🌸"},
    {"name": "Social Science", "emoji": "🌍"},
    {"name": "Computer",       "emoji": "💻"},
    {"name": "Grammar",        "emoji": "✏️"},
    {"name": "Moral Science",  "emoji": "🕊️"},
    {"name": "PT",             "emoji": "⚽"},
]

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title"><span>📚</span> Select Subjects</div>', unsafe_allow_html=True)
st.markdown("**Choose the subjects your child studies:**")
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
# FAMILY EVENTS — fully outside form, fully interactive
# ============================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title"><span>👨‍👩‍👧</span> Family Events Calendar</div>', unsafe_allow_html=True)
st.markdown("**Pick dates with family events — timetable will adjust study hours automatically.**")

# Month navigation
today      = date.today()
base_first = date(today.year, today.month, 1)

nav1, nav2, nav3 = st.columns([1, 4, 1])
with nav1:
    if st.button("◀ Prev", key="cal_prev"):
        if st.session_state.cal_offset > 0:
            st.session_state.cal_offset -= 1
        st.rerun()
with nav3:
    if st.button("Next ▶", key="cal_next"):
        st.session_state.cal_offset += 1
        st.rerun()

# Compute displayed month
off         = st.session_state.cal_offset
raw_month   = base_first.month - 1 + off
disp_year   = base_first.year + raw_month // 12
disp_month  = raw_month % 12 + 1
disp_first  = date(disp_year, disp_month, 1)
_, days_in  = calendar.monthrange(disp_year, disp_month)
start_wd    = disp_first.weekday()   # 0=Mon

with nav2:
    st.markdown(
        f"<div style='text-align:center;font-size:1.15rem;font-weight:800;padding:6px 0;'>"
        f"📅 {disp_first.strftime('%B %Y')}</div>",
        unsafe_allow_html=True
    )

# Build calendar HTML (visual only)
day_labels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
label_html = "".join(f'<div class="cal-day-label">{d}</div>' for d in day_labels)

cells = ["<div class='cal-day empty'></div>"] * start_wd
for dn in range(1, days_in + 1):
    d   = date(disp_year, disp_month, dn)
    ds  = str(d)
    cls = "cal-day"
    if ds in st.session_state.family_events: cls += " selected"
    elif d == today:                          cls += " today"
    elif d < today:                           cls += " past"
    cells.append(f"<div class='{cls}'>{dn}</div>")

st.markdown(
    f"<div class='cal-grid'>{label_html}{''.join(cells)}</div>",
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# Date picker + Add button
future_days = [date(disp_year, disp_month, dn)
               for dn in range(1, days_in + 1)
               if date(disp_year, disp_month, dn) >= today]

if future_days:
    pick_col, add_col = st.columns([4, 1])
    with pick_col:
        picked = st.selectbox(
            "📆 Select a date to add as Family Event",
            options=future_days,
            format_func=lambda d: d.strftime("%A, %d %B %Y"),
            key="date_picker"
        )
    with add_col:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add", key="add_event_btn"):
            ds = str(picked)
            if ds not in st.session_state.family_events:
                st.session_state.family_events[ds] = {"impact": "medium", "hours": 3}
            st.rerun()
else:
    st.info("No future dates in this month — go to next month.")

# Show added events with controls
if st.session_state.family_events:
    st.markdown("---")
    st.markdown("**📋 Your Family Events — adjust impact & hours:**")

    study_reduction_label = {"low": "~20% less study", "medium": "~40% less study", "high": "~70% less study"}
    impact_emoji          = {"low": "🟢 Low", "medium": "🟡 Medium", "high": "🔴 High"}
    to_remove = []

    for ds in sorted(st.session_state.family_events.keys()):
        ev  = st.session_state.family_events[ds]
        dob = date.fromisoformat(ds)

        st.markdown(f"<div class='event-row'>", unsafe_allow_html=True)
        ec1, ec2, ec3, ec4 = st.columns([3, 2, 2, 1])

        with ec1:
            st.markdown(
                f"<div style='font-weight:800;font-size:0.98rem;padding-top:8px;'>"
                f"📅 {dob.strftime('%A, %d %B %Y')}</div>",
                unsafe_allow_html=True
            )

        with ec2:
            new_impact = st.selectbox(
                "Impact Level",
                ["low", "medium", "high"],
                index=["low", "medium", "high"].index(ev["impact"]),
                key=f"impact_{ds}"
            )
            st.session_state.family_events[ds]["impact"] = new_impact

        with ec3:
            new_hours = st.slider(
                "Family Event Hours",
                min_value=1, max_value=8,
                value=ev["hours"],
                key=f"hours_{ds}",
                help="How many hours will this event take?"
            )
            st.session_state.family_events[ds]["hours"] = new_hours

        with ec4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Remove", key=f"rem_{ds}"):
                to_remove.append(ds)

        st.markdown(
            f"<div style='font-size:0.8rem;color:#8b949e;margin-top:4px;'>"
            f"{impact_emoji[new_impact]} &nbsp;·&nbsp; "
            f"⏱️ {new_hours}h on family event &nbsp;·&nbsp; "
            f"📉 {study_reduction_label[new_impact]} that day</div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    for ds in to_remove:
        del st.session_state.family_events[ds]
    if to_remove:
        st.rerun()

else:
    st.markdown(
        "<div style='color:#8b949e;font-size:0.9rem;padding:10px 0;'>"
        "No family events added yet. Pick a date above and click ➕ Add.</div>",
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# MAIN FORM
# ============================================================
with st.form("main_form"):

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span>👶</span> Child Details</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Child Name", "Aman")
        age  = st.number_input("Age", 5, 18, 10)
    with c2:
        grade          = st.selectbox("Class / Standard", [str(i) for i in range(1, 11)])
        attention_span = st.slider("Attention Level", 0.5, 2.0, 1.0, 0.1)
    with c3:
        days_remaining  = st.number_input("Days till Exam", 1, 120, 14)
        max_daily_study = st.slider("Max Study Hours / Day", 1, 8, 4)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span>🛌</span> Sleep & Health</div>', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    with s1:
        sleep_hours = st.slider("Sleep Hours", 6.0, 10.0, 8.0, 0.5)
    with s2:
        sleep_start = st.selectbox("Bedtime Hour", list(range(20, 24)),
                                   format_func=lambda x: f"{x}:00")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span>📝</span> Chapters Remaining per Subject</div>', unsafe_allow_html=True)
    if selected_subjects:
        chap_cols   = st.columns(min(len(selected_subjects), 5))
        chapter_map = {}
        for idx, sname in enumerate(selected_subjects):
            with chap_cols[idx % 5]:
                ch = st.number_input(sname, min_value=1, max_value=20, value=4, key=f"ch_{sname}")
                chapter_map[sname] = ch
    else:
        st.info("Select subjects above to set chapters.")
        chapter_map = {}
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title"><span>⏰</span> Daily Routine Slots</div>', unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)
    with r1:
        include_breakfast = st.checkbox("🥣 Breakfast", True)
        include_lunch     = st.checkbox("🍱 Lunch", True)
    with r2:
        include_nap   = st.checkbox("😴 Nap Time", True)
        include_relax = st.checkbox("🎵 Relax Time", True)
    with r3:
        include_games  = st.checkbox("⚽ Games / Sports", True)
        include_dinner = st.checkbox("🍽️ Dinner", True)
    st.markdown('</div>', unsafe_allow_html=True)

    submitted = st.form_submit_button("🚀 Generate My Timetable")

# ============================================================
# HELPERS
# ============================================================
def in_sleep(hour, s_start, s_hours):
    end = (s_start + int(s_hours)) % 24
    if s_start < end:
        return s_start <= hour < end
    return hour >= s_start or hour < end


def rule_scheduler(subjects, family_events_map, days_remaining,
                   sleep_start, sleep_hours, max_daily_study,
                   include_breakfast, include_lunch, include_nap,
                   include_games, include_relax, include_dinner):

    today_d  = date.today()
    schedule = []

    routine_map = {}
    if include_breakfast: routine_map[8]  = "🥣 Breakfast"
    if include_lunch:     routine_map[13] = "🍱 Lunch"
    if include_nap:       routine_map[14] = "😴 Nap Time"
    if include_games:     routine_map[17] = "⚽ Games / Sports"
    if include_relax:     routine_map[18] = "🎵 Relax Time"
    if include_dinner:    routine_map[20] = "🍽️ Dinner"

    study_reduction = {"low": 0.8, "medium": 0.6, "high": 0.3}

    for d in range(days_remaining):
        current_date = today_d + timedelta(days=d)
        ds           = str(current_date)
        hour         = 7
        study_done   = 0

        fam_ev          = family_events_map.get(ds, None)
        fam_hours_left  = fam_ev["hours"] if fam_ev else 0
        fam_impact      = fam_ev["impact"] if fam_ev else None
        max_study_today = max_daily_study
        if fam_ev:
            max_study_today = max(1, int(max_daily_study * study_reduction[fam_impact]))

        subjs = sorted(
            [dict(s) for s in subjects],
            key=lambda x: x["chapters_remaining"],
            reverse=True
        )

        while hour < 22:
            if in_sleep(hour, sleep_start, sleep_hours):
                hour += 1
                continue

            # Family event block starts at 15:00
            if fam_ev and fam_hours_left > 0 and hour >= 15:
                schedule.append({
                    "📅 Date":    ds,
                    "🕐 Time":    f"{hour}:00 – {hour+1}:00",
                    "📚 Subject": "👨‍👩‍👧 Family Event",
                    "📋 Task":    f"Family Time · {fam_impact} impact · {fam_ev['hours']}h total"
                })
                fam_hours_left -= 1
                hour += 1
                continue

            if hour in routine_map:
                schedule.append({
                    "📅 Date":    ds,
                    "🕐 Time":    f"{hour}:00 – {hour+1}:00",
                    "📚 Subject": routine_map[hour],
                    "📋 Task":    "Routine"
                })
                hour += 1
                continue

            if study_done < max_study_today and subjs:
                s = subjs[0]
                schedule.append({
                    "📅 Date":    ds,
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
                    "📅 Date":    ds,
                    "🕐 Time":    f"{hour}:00 – {hour+1}:00",
                    "📚 Subject": "🌟 Free Time",
                    "📋 Task":    "Rest / Light Activity"
                })

            hour += 1

    return schedule

# ============================================================
# GENERATE
# ============================================================
if submitted:
    if not selected_subjects:
        st.error("❌ Please select at least one subject before generating!")
    else:
        subjects = [
            {"name": s, "chapters_remaining": chapter_map.get(s, 4), "difficulty": "medium"}
            for s in selected_subjects
        ]

        timetable = rule_scheduler(
            subjects, st.session_state.family_events, int(days_remaining),
            sleep_start, sleep_hours, max_daily_study,
            include_breakfast, include_lunch, include_nap,
            include_games, include_relax, include_dinner
        )

        df          = pd.DataFrame(timetable)
        study_slots = len([r for r in timetable if "Study" in r["📋 Task"]])
        fam_slots   = len([r for r in timetable if "Family" in r["📚 Subject"]])
        total_slots = len(timetable)

        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-badge">📅 Days<br><b>{int(days_remaining)}</b></div>
            <div class="stat-badge">📚 Study Slots<br><b>{study_slots}</b></div>
            <div class="stat-badge">👨‍👩‍👧 Family Slots<br><b>{fam_slots}</b></div>
            <div class="stat-badge">📋 Total Slots<br><b>{total_slots}</b></div>
            <div class="stat-badge">🧒 Child<br><b>{name}</b></div>
            <div class="stat-badge">🏫 Class<br><b>{grade}</b></div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.family_events:
            summary = ", ".join(
                f"{date.fromisoformat(ds).strftime('%d %b')} ({ev['impact']}, {ev['hours']}h)"
                for ds, ev in sorted(st.session_state.family_events.items())
            )
            st.info(f"👨‍👩‍👧 Family events included in schedule: **{summary}**")

        st.success(f"✅ Timetable generated for **{name}** — {total_slots} slots across {int(days_remaining)} days!")
        st.dataframe(df, use_container_width=True, height=420)

        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button("⬇️ Download JSON", data=json.dumps(timetable, indent=2),
                               file_name=f"{name}_timetable.json", mime="application/json")
        with dl2:
            st.download_button("⬇️ Download CSV", data=df.to_csv(index=False),
                               file_name=f"{name}_timetable.csv", mime="text/csv")

        if mongo_ok:
            try:
                uid = users_collection.insert_one({
                    "name": name, "age": age, "grade": grade,
                    "subjects": selected_subjects,
                    "family_events": st.session_state.family_events,
                    "created_at": str(datetime.now())
                }).inserted_id
                timetable_collection.insert_one({
                    "user_id": str(uid), "timetable": timetable,
                    "created_at": str(datetime.now())
                })
                st.success("📦 Saved to MongoDB!")
            except Exception as e:
                st.warning(f"⚠️ Could not save: {e}")

# ============================================================
# SAVED TIMETABLES
# ============================================================
st.markdown("---")
ct, cb = st.columns([3, 1])
with ct:
    st.markdown('<div class="section-title"><span>📂</span> Saved Timetables</div>', unsafe_allow_html=True)
with cb:
    show_saved = st.button("📂 Show Saved")

if show_saved:
    if not mongo_ok:
        st.error("❌ MongoDB not connected.")
    else:
        saved = list(timetable_collection.find().sort("created_at", -1).limit(5))
        if not saved:
            st.info("No saved timetables yet.")
        for item in saved:
            with st.expander(f"👤 {item.get('user_id','?')} — {str(item.get('created_at',''))[:16]}"):
                st.dataframe(pd.DataFrame(item["timetable"]).head(30), use_container_width=True)
