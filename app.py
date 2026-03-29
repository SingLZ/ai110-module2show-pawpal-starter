from datetime import datetime
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler


def priority_badge(priority: int) -> str:
    return {1: "🔴 Critical", 2: "🟠 High",
            3: "🟡 Medium",  4: "🔵 Low", 5: "⚪ Minimal"}.get(priority, str(priority))

def task_icon(task_type: str) -> str:
    return {"walk": "🦮", "feed": "🍖", "medicate": "💊",
            "groom": "✂️"}.get(task_type, "📌")

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Your smart pet care scheduler.")

# ── Session state ─────────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner.load_from_json("data.json")

owner     = st.session_state.owner
scheduler = Scheduler(owner)

# ── Sidebar: Add a pet ────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🐶 Add a Pet")
    with st.form("add_pet_form"):
        pet_name = st.text_input("Pet name")
        species  = st.text_input("Species")
        age      = st.number_input("Age", min_value=0, step=1)
        needs    = st.text_input("Special needs (comma-separated)", value="")
        if st.form_submit_button("Add Pet") and pet_name:
            special = [n.strip() for n in needs.split(",") if n.strip()]
            owner.add_pet(Pet(pet_name, species, int(age), special_needs=special))
            owner.save_to_json("data.json")
            st.success(f"{pet_name} added!")
            st.rerun()

    st.divider()
    st.header("🐱 Your Pets")
    if not owner.pets:
        st.info("No pets yet.")
    else:
        for pet in owner.pets:
            needs_str = ", ".join(pet.special_needs) if pet.special_needs else "none"
            st.markdown(f"**{pet.name}** ({pet.species}, age {pet.age})")
            st.caption(f"Special needs: {needs_str}")

# ── Main: Add a task ──────────────────────────────────────────────────────────
st.subheader("📝 Schedule a Task")
pet_names = [p.name for p in owner.pets]

if not pet_names:
    st.info("Add a pet in the sidebar to get started.")
else:
    with st.form("add_task_form"):
        col1, col2 = st.columns(2)
        with col1:
            selected   = st.selectbox("Pet", pet_names)
            task_type  = st.selectbox("Task type", ["walk", "feed", "medicate", "groom"])
            recurrence = st.selectbox("Repeats", ["none", "daily", "weekly"])
        with col2:
            due_time = st.time_input("Due time")
            duration = st.slider("Duration (min)", 5, 120, 30)
            priority = st.slider("Priority (1 = most urgent)", 1, 5, 2)

        if st.form_submit_button("➕ Add Task"):
            pet    = next(p for p in owner.pets if p.name == selected)
            due_dt = datetime.now().replace(
                hour=due_time.hour, minute=due_time.minute, second=0, microsecond=0)
            rec = None if recurrence == "none" else recurrence
            pet.add_task(Task(task_type, due_dt, duration, priority, selected,
                              recurrence=rec))
            st.success(f"Task added for {selected}!")
            owner.save_to_json("data.json")
            st.rerun()

st.divider()

# ── Main: Conflict warnings ───────────────────────────────────────────────────
conflicts = scheduler.detect_conflicts()
if conflicts:
    st.subheader("⚠️ Scheduling Conflicts")
    for warning in conflicts:
        st.warning(warning)

# ── Main: Today's schedule ────────────────────────────────────────────────────
st.subheader("📋 Today's Schedule")

col_filter1, col_filter2 = st.columns(2)
with col_filter1:
    filter_pet = st.selectbox("Filter by pet", ["All"] + pet_names)
with col_filter2:
    filter_status = st.selectbox("Filter by status", ["Pending", "Completed", "All"])

tasks = scheduler.sort_by_time(scheduler.get_todays_tasks())

if filter_pet != "All":
    tasks = [t for t in tasks if t.pet_name == filter_pet]
if filter_status == "Pending":
    tasks = [t for t in tasks if not t.completed]
elif filter_status == "Completed":
    tasks = [t for t in tasks if t.completed]

if not tasks:
    st.info("No tasks match your filters.")
else:
    tasks = scheduler.smart_prioritize() if filter_status == "Pending" \
        else scheduler.sort_by_time(scheduler.get_todays_tasks())
    for task in tasks:
        col1, col2, col3 = st.columns([3, 1, 1])
        status_icon = "✅" if task.completed else ("🔴" if task.is_overdue() else "⏳")
        rec_label   = f" 🔁 {task.recurrence}" if task.recurrence else ""
        col1.markdown(
            f"{status_icon} **{task.task_type.title()}** — {task.pet_name}  \n"
            f"🕐 {task.due_time.strftime('%I:%M %p')} &nbsp;&nbsp;"
            f"⏱ {task.duration} min &nbsp;&nbsp;"
            f"🎯 Priority {priority_badge(task.priority)}{rec_label}"
        )
        if not task.completed:
            if col3.button("✓ Done", key=f"done_{id(task)}"):
                pet = next(p for p in owner.pets if p.name == task.pet_name)
                scheduler.complete_task(task, pet)
                owner.save_to_json("data.json")
                st.rerun()
        else:
            col3.markdown("~~Done~~")

st.divider()
st.subheader("🔍 Find Next Available Slot")
if pet_names:
    col1, col2, col3 = st.columns(3)
    slot_pet      = col1.selectbox("Pet", pet_names, key="slot_pet")
    slot_duration = col2.slider("Task duration (min)", 5, 120, 30, key="slot_dur")
    if col3.button("Find slot"):
        slot = scheduler.find_next_available_slot(slot_duration, slot_pet)
        st.success(f"Next open slot for {slot_pet}: **{slot.strftime('%I:%M %p')}**")


# ── Main: Summary stats ───────────────────────────────────────────────────────
all_today = scheduler.get_todays_tasks()
if all_today:
    total     = len(all_today)
    done      = len([t for t in all_today if t.completed])
    overdue   = len(scheduler.get_overdue_tasks())
    m1, m2, m3 = st.columns(3)
    m1.metric("Tasks today",  total)
    m2.metric("Completed",    f"{done}/{total}")
    m3.metric("Overdue",      overdue, delta=f"-{overdue}" if overdue else None,
              delta_color="inverse")