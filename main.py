from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner("Alex", "alex@example.com")
dog = Pet("Biscuit", "Dog", 3)
cat = Pet("Luna", "Cat", 5)
owner.add_pet(dog)
owner.add_pet(cat)

now = datetime.now()

# Out-of-order tasks to test sorting
dog.add_task(Task("walk",     now.replace(hour=18, minute=0),  30, 2, "Biscuit", recurrence="daily"))
dog.add_task(Task("feed",     now.replace(hour=7,  minute=0),  10, 1, "Biscuit"))
dog.add_task(Task("groom",    now.replace(hour=7,  minute=20), 20, 3, "Biscuit"))  # conflicts with feed
cat.add_task(Task("medicate", now.replace(hour=9,  minute=0),   5, 1, "Luna",    recurrence="weekly"))
cat.add_task(Task("feed",     now.replace(hour=13, minute=0),  10, 2, "Luna"))

scheduler = Scheduler(owner)

# Sorting
print("\n--- Sorted by time ---")
for t in scheduler.sort_by_time(scheduler.get_todays_tasks()):
    print(" ", t)

# Filtering
print("\n--- Biscuit's tasks only ---")
for t in scheduler.filter_by_pet("Biscuit"):
    print(" ", t)

# Conflicts
print("\n--- Conflict detection ---")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for w in conflicts:
        print(" ", w)
else:
    print("  No conflicts found.")

# Recurring task test
print("\n--- Recurring task test ---")
feed_task = dog.tasks[1]
print(f"  Before: {feed_task}")
next_task = feed_task.mark_complete()
if next_task:
    dog.add_task(next_task)
    print(f"  Auto-scheduled: {next_task}")