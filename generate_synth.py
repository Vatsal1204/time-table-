# generate_synth.py
import random
import csv
from datetime import datetime, timedelta

subjects = ["Math","Science","English","History","Geography","Computer","Hindi","Physics","Chemistry"]
difficulties = {"easy": 0.8, "medium": 1.0, "hard": 1.2}

def sample_row():
    # user / global features
    age = random.randint(8,18)
    grade = random.randint(1,12)
    sleep_hours = round(random.uniform(6,10),1)
    days_remaining = random.randint(1,30)
    family_event = random.choice([0,0,0,1])   # mostly no event
    slot_hour = random.choice([9,10,11,14,15,16,18,19])  # hour-of-day
    is_weekend = random.choice([0,0,0,1])
    attention_span = random.choice([0.6,0.8,1.0,1.2])  # shorter -> smaller multiplier

    # subject features
    subj = random.choice(subjects)
    subj_difficulty = random.choice(["easy","medium","hard"])
    subj_difficulty_factor = difficulties[subj_difficulty]

    # urgency: chapters_remaining / days_remaining
    chapters_remaining = random.randint(0,8)
    urgency = (chapters_remaining + 0.5) / max(1, days_remaining)

    # base effective minutes (60 minute slot)
    base = 60.0

    # heuristics to generate label (you can tune)
    # good sleep + morning slot + easy subject + long attention -> high minutes
    morning_bonus = 1.05 if 8 <= slot_hour <= 11 else 0.95
    weekend_penalty = 0.9 if is_weekend else 1.0
    family_penalty = 0.7 if family_event else 1.0

    # predicted effective minutes
    # factors: attention span, difficulty, urgency (higher urgency increases focused minutes slightly),
    # sleep, morning/afternoon, weekend, family
    effective = base * attention_span / subj_difficulty_factor
    effective *= morning_bonus * weekend_penalty * family_penalty
    # sleep effect
    if sleep_hours < 7:
        effective *= 0.8
    elif sleep_hours > 9:
        effective *= 1.05
    # urgency effect (if very urgent, maybe more focused)
    effective *= (1.0 + min(urgency, 1.0) * 0.2)
    # add some noise
    effective += random.gauss(0,8)

    # clamp
    effective = max(10, min(60, effective))

    return {
        "age": age,
        "grade": grade,
        "sleep_hours": sleep_hours,
        "days_remaining": days_remaining,
        "family_event": family_event,
        "slot_hour": slot_hour,
        "is_weekend": is_weekend,
        "attention_span": attention_span,
        "subject": subj,
        "subj_difficulty": subj_difficulty,
        "chapters_remaining": chapters_remaining,
        "urgency": urgency,
        "effective_minutes": round(effective,1)
    }

def generate(n=5000, out="synth.csv"):
    keys = list(sample_row().keys())
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for _ in range(n):
            w.writerow(sample_row())

if __name__ == "__main__":
    generate(6000, "synth.csv")
    print("synth.csv created")
