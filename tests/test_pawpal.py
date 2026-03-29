from datetime import datetime, timedelta
import pytest
from pawpal_system import Owner, Pet, Task, Scheduler

# ── Helpers ──────────────────────────────────────────────────────────────────

def make_task(pet_name="Buddy", task_type="walk", hour=9, minute=0,
              duration=30, priority=2, recurrence=None):
    due = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    return Task(task_type, due, duration, priority, pet_name, recurrence=recurrence)

def make_scheduler(tasks_by_pet: dict) -> tuple[Scheduler, Owner]:
    """Create a scheduler pre-loaded with pets and tasks."""
    owner = Owner("Alex", "alex@example.com")
    for pet_name, tasks in tasks_by_pet.items():
        pet = Pet(pet_name, "Dog", 3)
        for t in tasks:
            pet.add_task(t)
        owner.add_pet(pet)
    return Scheduler(owner), owner


# ── Task tests ────────────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed == False
    task.mark_complete()
    assert task.completed == True

def test_non_recurring_mark_complete_returns_none():
    task = make_task(recurrence=None)
    result = task.mark_complete()
    assert result is None

def test_daily_recurrence_returns_next_day():
    task = make_task(recurrence="daily")
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_time.date() == (datetime.now() + timedelta(days=1)).date()
    assert next_task.recurrence == "daily"

def test_weekly_recurrence_returns_next_week():
    task = make_task(recurrence="weekly")
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_time.date() == (datetime.now() + timedelta(weeks=1)).date()
    assert next_task.recurrence == "weekly"

def test_recurrence_preserves_task_type_and_priority():
    task = make_task(task_type="medicate", priority=1, recurrence="daily")
    next_task = task.mark_complete()
    assert next_task.task_type == "medicate"
    assert next_task.priority == 1

def test_overdue_detection():
    past = datetime.now() - timedelta(hours=1)
    task = Task("walk", past, 30, 1, "Buddy")
    assert task.is_overdue() == True

def test_completed_task_not_overdue():
    past = datetime.now() - timedelta(hours=1)
    task = Task("walk", past, 30, 1, "Buddy")
    task.mark_complete()
    assert task.is_overdue() == False

def test_future_task_not_overdue():
    task = make_task()   # defaults to 9 AM today — fine unless run at 8:59
    future = Task("walk", datetime.now() + timedelta(hours=2), 30, 1, "Buddy")
    assert future.is_overdue() == False


# ── Pet tests ─────────────────────────────────────────────────────────────────

def test_add_task_increases_count():
    pet = Pet("Luna", "Cat", 5)
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1

def test_get_pending_tasks_excludes_completed():
    pet = Pet("Luna", "Cat", 5)
    t1 = make_task(hour=9)
    t2 = make_task(hour=10)
    t1.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)
    pending = pet.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0] == t2

def test_pet_with_no_tasks():
    pet = Pet("Empty", "Cat", 2)
    assert pet.get_tasks() == []
    assert pet.get_pending_tasks() == []


# ── Owner tests ───────────────────────────────────────────────────────────────

def test_add_pet_increases_count():
    owner = Owner("Alex", "alex@example.com")
    assert len(owner.pets) == 0
    owner.add_pet(Pet("Biscuit", "Dog", 3))
    assert len(owner.pets) == 1

def test_get_all_tasks_flattens_across_pets():
    owner = Owner("Alex", "alex@example.com")
    dog = Pet("Biscuit", "Dog", 3)
    cat = Pet("Luna", "Cat", 5)
    dog.add_task(make_task(pet_name="Biscuit", hour=8))
    dog.add_task(make_task(pet_name="Biscuit", hour=9))
    cat.add_task(make_task(pet_name="Luna", hour=10))
    owner.add_pet(dog)
    owner.add_pet(cat)
    assert len(owner.get_all_tasks()) == 3

def test_owner_with_no_pets_returns_empty():
    owner = Owner("Alex", "alex@example.com")
    assert owner.get_all_tasks() == []


# ── Scheduler: sorting ────────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    t1 = make_task(hour=14)
    t2 = make_task(hour=8)
    t3 = make_task(hour=11)
    scheduler, _ = make_scheduler({"Biscuit": [t1, t2, t3]})
    sorted_tasks = scheduler.sort_by_time()
    times = [t.due_time for t in sorted_tasks]
    assert times == sorted(times)

def test_sort_preserves_all_tasks():
    tasks = [make_task(hour=h) for h in [14, 8, 11, 7, 16]]
    scheduler, _ = make_scheduler({"Biscuit": tasks})
    assert len(scheduler.sort_by_time()) == 5


# ── Scheduler: filtering ──────────────────────────────────────────────────────

def test_filter_by_pet_returns_correct_tasks():
    scheduler, _ = make_scheduler({
        "Biscuit": [make_task(pet_name="Biscuit", hour=9)],
        "Luna":    [make_task(pet_name="Luna",    hour=10)],
    })
    results = scheduler.filter_by_pet("Biscuit")
    assert all(t.pet_name == "Biscuit" for t in results)
    assert len(results) == 1

def test_filter_by_status_pending():
    t1 = make_task(hour=9)
    t2 = make_task(hour=10)
    t1.mark_complete()
    scheduler, _ = make_scheduler({"Biscuit": [t1, t2]})
    pending = scheduler.filter_by_status(completed=False)
    assert len(pending) == 1
    assert pending[0] == t2

def test_filter_by_status_completed():
    t1 = make_task(hour=9)
    t2 = make_task(hour=10)
    t1.mark_complete()
    scheduler, _ = make_scheduler({"Biscuit": [t1, t2]})
    done = scheduler.filter_by_status(completed=True)
    assert len(done) == 1
    assert done[0] == t1

def test_filter_by_nonexistent_pet_returns_empty():
    scheduler, _ = make_scheduler({"Biscuit": [make_task()]})
    assert scheduler.filter_by_pet("Ghost") == []


# ── Scheduler: conflict detection ─────────────────────────────────────────────

def test_exact_time_conflict_detected():
    t1 = make_task(hour=9, minute=0, duration=30)
    t2 = make_task(hour=9, minute=0, duration=30)
    scheduler, _ = make_scheduler({"Biscuit": [t1, t2]})
    assert len(scheduler.detect_conflicts()) > 0

def test_overlapping_duration_conflict_detected():
    t1 = make_task(hour=9, minute=0,  duration=30)   # ends 9:30
    t2 = make_task(hour=9, minute=20, duration=30)   # starts 9:20 — overlap
    scheduler, _ = make_scheduler({"Biscuit": [t1, t2]})
    assert len(scheduler.detect_conflicts()) > 0

def test_non_overlapping_tasks_no_conflict():
    t1 = make_task(hour=9,  minute=0,  duration=30)  # ends 9:30
    t2 = make_task(hour=10, minute=0,  duration=30)  # starts 10:00 — clear
    scheduler, _ = make_scheduler({"Biscuit": [t1, t2]})
    assert scheduler.detect_conflicts() == []

def test_conflicts_across_different_pets_not_flagged():
    t1 = make_task(pet_name="Biscuit", hour=9, duration=30)
    t2 = make_task(pet_name="Luna",    hour=9, duration=30)
    scheduler, _ = make_scheduler({"Biscuit": [t1], "Luna": [t2]})
    assert scheduler.detect_conflicts() == []

def test_no_tasks_no_conflicts():
    scheduler, _ = make_scheduler({"Biscuit": []})
    assert scheduler.detect_conflicts() == []


# ── Scheduler: complete_task with recurrence ──────────────────────────────────

def test_complete_task_adds_next_occurrence_to_pet():
    t = make_task(recurrence="daily")
    scheduler, owner = make_scheduler({"Biscuit": [t]})
    pet = owner.pets[0]
    scheduler.complete_task(t, pet)
    assert len(pet.tasks) == 2
    assert pet.tasks[1].due_time.date() == (datetime.now() + timedelta(days=1)).date()

def test_complete_nonrecurring_task_does_not_add_new():
    t = make_task(recurrence=None)
    scheduler, owner = make_scheduler({"Biscuit": [t]})
    pet = owner.pets[0]
    scheduler.complete_task(t, pet)
    assert len(pet.tasks) == 1