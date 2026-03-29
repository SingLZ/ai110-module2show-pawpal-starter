from datetime import datetime
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# Session state init
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="My Owner", email="owner@example.com")

owner = st.session_state.owner
scheduler = Scheduler(owner)

# --- Add a pet ---
st.subheader("Add a Pet")
with st.form("add_pet_form"):
    pet_name    = st.text_input("Pet name")
    species     = st.text_input("Species")
    age         = st.number_input("Age", min_value=0, step=1)
    if st.form_submit_button("Add Pet") and pet_name:
        owner.add_pet(Pet(pet_name, species, int(age)))
        st.rerun()

# --- Add a task ---
st.subheader("Schedule a Task")
pet_names = [p.name for p in owner.pets]

if not pet_names:
    st.info("Add a pet first before scheduling tasks.")
else:
    with st.form("add_task_form"):
        selected  = st.selectbox("Pet", pet_names)
        task_type = st.selectbox("Type", ["walk", "feed", "medicate", "groom"])
        due_time  = st.time_input("Due time")
        priority  = st.slider("Priority (1=high)", 1, 5, 2)
        if st.form_submit_button("Add Task"):
            pet = next(p for p in owner.pets if p.name == selected)
            due_dt = datetime.now().replace(
                hour=due_time.hour, minute=due_time.minute, second=0)
            pet.add_task(Task(task_type, due_dt, 30, priority, selected))
            st.rerun()

st.divider()

# --- Today's schedule ---
st.subheader("📋 Today's Schedule")

if st.button("Generate schedule"):
    tasks = scheduler.prioritize()
    if tasks:
        st.success(f"{len(tasks)} task(s) pending today.")
    else:
        st.info("No pending tasks for today.")

for task in scheduler.prioritize():
    col1, col2 = st.columns([4, 1])
    col1.write(str(task))
    if col2.button("✓ Done", key=str(id(task))):
        pet = next(p for p in owner.pets if p.name == task.pet_name)
        scheduler.complete_task(task, pet)
        st.rerun()