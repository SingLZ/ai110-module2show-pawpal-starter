from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Alex", email="alex@example.com")

dog = Pet(name="Biscuit", species="Dog", age=3, special_needs=["3 walks/day"])
cat = Pet(name="Luna", species="Cat", age=5, special_needs=["insulin shot"])

owner.add_pet(dog)
owner.add_pet(cat)

# --- Tasks (all due today) ---
now = datetime.now()

dog.add_task(Task("walk",  now.replace(hour=8,  minute=0),  duration=30, priority=2, pet_name="Biscuit"))
dog.add_task(Task("feed",  now.replace(hour=12, minute=0),  duration=10, priority=1, pet_name="Biscuit"))
dog.add_task(Task("walk",  now.replace(hour=18, minute=0),  duration=30, priority=2, pet_name="Biscuit"))
cat.add_task(Task("medicate", now.replace(hour=9, minute=0), duration=5, priority=1, pet_name="Luna"))
cat.add_task(Task("feed",  now.replace(hour=13, minute=0),  duration=10, priority=2, pet_name="Luna"))

# --- Print Schedule ---
scheduler = Scheduler(owner)

print(f"\n{'='*45}")
print(f"  PawPal+ — Today's Schedule for {owner.name}")
print(f"{'='*45}")

tasks = scheduler.prioritize()
if not tasks:
    print("  No pending tasks for today!")
else:
    for task in tasks:
        print(f"  {task}")

overdue = scheduler.get_overdue_tasks()
if overdue:
    print(f"\n  ⚠  {len(overdue)} overdue task(s):")
    for task in overdue:
        print(f"     {task}")

print(f"{'='*45}\n")