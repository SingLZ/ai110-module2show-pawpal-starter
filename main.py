from datetime import datetime, timedelta
from tabulate import tabulate
from pawpal_system import Owner, Pet, Task, Scheduler

# ── Setup ─────────────────────────────────────────────────────────────────────

owner = Owner("Alex", "alex@example.com")
dog = Pet("Biscuit", "Dog", 3)
cat = Pet("Luna", "Cat", 5)
owner.add_pet(dog)
owner.add_pet(cat)

now = datetime.now()

dog.add_task(Task("walk",     now.replace(hour=18, minute=0),  30, 2, "Biscuit", recurrence="daily"))
dog.add_task(Task("feed",     now.replace(hour=7,  minute=0),  10, 1, "Biscuit"))
dog.add_task(Task("groom",    now.replace(hour=7,  minute=20), 20, 3, "Biscuit"))  # conflicts with feed
cat.add_task(Task("medicate", now.replace(hour=9,  minute=0),   5, 1, "Luna",    recurrence="weekly"))
cat.add_task(Task("feed",     now.replace(hour=13, minute=0),  10, 2, "Luna"))

scheduler = Scheduler(owner)

# ── Helper ────────────────────────────────────────────────────────────────────

def print_schedule(tasks: list, title: str = "Today's Schedule") -> None:
    """Print a formatted table of tasks to the terminal."""
    if not tasks:
        print(f"\n  {title}: no tasks found.\n")
        return

    priority_labels = {1: "🔴 Critical", 2: "🟠 High",
                       3: "🟡 Medium",   4: "🔵 Low", 5: "⚪ Minimal"}
    task_icons = {"walk": "🦮", "feed": "🍖", "medicate": "💊", "groom": "✂️"}

    rows = []
    for t in tasks:
        status = "✅ Done" if t.completed else ("🔴 OVERDUE" if t.is_overdue() else "⏳ Pending")
        rows.append([
            f"{task_icons.get(t.task_type, '📌')} {t.task_type.title()}",
            t.pet_name,
            t.due_time.strftime("%I:%M %p"),
            f"{t.duration} min",
            priority_labels.get(t.priority, str(t.priority)),
            t.recurrence or "—",
            status,
        ])

    headers = ["Task", "Pet", "Due", "Duration", "Priority", "Recurrence", "Status"]
    print(f"\n{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}")
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    print()

# ── Sorted schedule ───────────────────────────────────────────────────────────

print_schedule(scheduler.sort_by_time(scheduler.get_todays_tasks()), "Sorted by Time")

# ── Filtered: Biscuit only ────────────────────────────────────────────────────

print_schedule(scheduler.filter_by_pet("Biscuit"), "Biscuit's Tasks Only")

# ── Conflict detection ────────────────────────────────────────────────────────

print(f"{'─'*70}")
print("  Conflict Detection")
print(f"{'─'*70}")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for w in conflicts:
        print(f"  {w}")
else:
    print("  No conflicts found.")
print()

# ── Recurring task test ───────────────────────────────────────────────────────

print(f"{'─'*70}")
print("  Recurring Task Test")
print(f"{'─'*70}")
feed_task = dog.tasks[1]
print(f"  Before:         {feed_task.task_type} @ {feed_task.due_time.strftime('%I:%M %p')}")
next_task = feed_task.mark_complete()
if next_task:
    dog.add_task(next_task)
    print(f"  Auto-scheduled: {next_task.task_type} @ {next_task.due_time.strftime('%I:%M %p')}")
print()