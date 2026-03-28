from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

def make_task(pet_name="Buddy", priority=1, minutes_from_now=60):
    due = datetime.now() + timedelta(minutes=minutes_from_now)
    return Task("walk", due, duration=30, priority=priority, pet_name=pet_name)

# Test 1: mark_complete() changes task status
def test_task_completion():
    task = make_task()
    assert task.completed == False
    task.mark_complete()
    assert task.completed == True

# Test 2: adding a task increases the pet's task count
def test_task_addition_increases_count():
    pet = Pet(name="Buddy", species="Dog", age=2)
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1
    pet.add_task(make_task())
    assert len(pet.tasks) == 2

# Test 3: overdue detection works correctly
def test_overdue_detection():
    past_task = Task("feed", datetime.now() - timedelta(hours=1),
                     duration=10, priority=1, pet_name="Luna")
    future_task = make_task(minutes_from_now=60)
    assert past_task.is_overdue() == True
    assert future_task.is_overdue() == False

# Test 4: scheduler only returns today's tasks
def test_scheduler_filters_today():
    owner = Owner("Alex", "alex@example.com")
    pet = Pet("Biscuit", "Dog", 3)
    owner.add_pet(pet)
    pet.add_task(make_task(minutes_from_now=60))         # today
    pet.add_task(make_task(minutes_from_now=60*25))      # tomorrow
    scheduler = Scheduler(owner)
    assert len(scheduler.get_todays_tasks()) == 1