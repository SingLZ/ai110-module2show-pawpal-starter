from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import json
from pathlib import Path

@dataclass
class Task:
    """Represents a single pet care activity."""
    task_type: str
    due_time: datetime
    duration: int        # minutes
    priority: int        # 1 = highest priority
    pet_name: str
    completed: bool = False
    recurrence: Optional[str] = None  # "daily", "weekly", or None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True
        if self.recurrence == "daily":
            return Task(self.task_type, self.due_time + timedelta(days=1),
                        self.duration, self.priority, self.pet_name,
                        recurrence="daily")
        if self.recurrence == "weekly":
            return Task(self.task_type, self.due_time + timedelta(weeks=1),
                        self.duration, self.priority, self.pet_name,
                        recurrence="weekly")
        return None

    def is_overdue(self) -> bool:
        """Return True if the task is past due and not completed."""
        return not self.completed and datetime.now() > self.due_time

    def reschedule(self, new_time: datetime) -> None:
        """Move the task to a new due time."""
        self.due_time = new_time

    def __str__(self) -> str:
        status = "✓" if self.completed else "○"
        overdue = " ⚠ OVERDUE" if self.is_overdue() else ""
        return (f"[{status}] [{self.task_type.upper()}] {self.pet_name} "
                f"@ {self.due_time.strftime('%I:%M %p')} "
                f"({self.duration} min, priority {self.priority}){overdue}")


@dataclass
class Pet:
    """Stores pet details and their associated tasks."""
    name: str
    species: str
    age: int
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def get_pending_tasks(self) -> list[Task]:
        """Return only incomplete tasks for this pet."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    """Manages an owner's profile and their pets."""
    name: str
    email: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def to_dict(self) -> dict:
        """Serialize the owner and all pets/tasks to a plain dictionary."""
        return {
            "name":  self.name,
            "email": self.email,
            "pets": [
                {
                    "name":          pet.name,
                    "species":       pet.species,
                    "age":           pet.age,
                    "special_needs": pet.special_needs,
                    "tasks": [
                        {
                            "task_type":  t.task_type,
                            "due_time":   t.due_time.isoformat(),
                            "duration":   t.duration,
                            "priority":   t.priority,
                            "pet_name":   t.pet_name,
                            "completed":  t.completed,
                            "recurrence": t.recurrence,
                        }
                        for t in pet.tasks
                    ],
                }
                for pet in self.pets
            ],
        }

    def save_to_json(self, path: str = "data.json") -> None:
        """Save the current owner state to a JSON file."""
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load_from_json(cls, path: str = "data.json") -> "Owner":
        """Load an Owner (with pets and tasks) from a JSON file."""
        if not Path(path).exists():
            return cls(name="My Owner", email="owner@example.com")
        data = json.loads(Path(path).read_text())
        owner = cls(name=data["name"], email=data["email"])
        for p in data["pets"]:
            pet = Pet(p["name"], p["species"], p["age"], p["special_needs"])
            for t in p["tasks"]:
                pet.add_task(Task(
                    task_type  = t["task_type"],
                    due_time   = datetime.fromisoformat(t["due_time"]),
                    duration   = t["duration"],
                    priority   = t["priority"],
                    pet_name   = t["pet_name"],
                    completed  = t["completed"],
                    recurrence = t["recurrence"],
                ))
            owner.add_pet(pet)
        return owner


class Scheduler:
    """Retrieves, organizes, and prioritizes tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_todays_tasks(self) -> list[Task]:
        """Return all tasks due today, sorted by due time."""
        today = datetime.now().date()
        todays = [
            t for t in self.owner.get_all_tasks()
            if t.due_time.date() == today
        ]
        return sorted(todays, key=lambda t: t.due_time)

    def prioritize(self) -> list[Task]:
        """Return today's incomplete tasks sorted by priority, then due time."""
        todays = self.get_todays_tasks()
        pending = [t for t in todays if not t.completed]
        return sorted(pending, key=lambda t: (t.priority, t.due_time))

    def get_overdue_tasks(self) -> list[Task]:
        """Return all incomplete tasks that are past their due time."""
        return [t for t in self.owner.get_all_tasks() if t.is_overdue()]
    
    def sort_by_time(self, tasks: list[Task] = None) -> list[Task]:
        """Return tasks sorted by due time, earliest first."""
        tasks = tasks or self.owner.get_all_tasks()
        return sorted(tasks, key=lambda t: t.due_time)

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks belonging to a specific pet."""
        return [t for t in self.owner.get_all_tasks() if t.pet_name == pet_name]

    def filter_by_status(self, completed: bool) -> list[Task]:
        """Return tasks filtered by completion status."""
        return [t for t in self.owner.get_all_tasks() if t.completed == completed]
    
    def complete_task(self, task: Task, pet: Pet) -> None:
        """Mark a task complete and auto-schedule the next recurrence."""
        next_task = task.mark_complete()
        if next_task:
            pet.add_task(next_task)

    def detect_conflicts(self) -> list[str]:
        """Return warning messages for tasks that overlap in time for the same pet."""
        warnings = []
        all_tasks = self.sort_by_time(self.get_todays_tasks())

        for i, task_a in enumerate(all_tasks):
            for task_b in all_tasks[i + 1:]:
                if task_a.pet_name != task_b.pet_name:
                    continue
                a_end = task_a.due_time + timedelta(minutes=task_a.duration)
                # task_b starts before task_a ends = overlap
                if task_b.due_time < a_end:
                    warnings.append(
                        f"⚠ Conflict: '{task_a.task_type}' and '{task_b.task_type}' "
                        f"overlap for {task_a.pet_name} "
                        f"({task_a.due_time.strftime('%I:%M %p')} vs "
                        f"{task_b.due_time.strftime('%I:%M %p')})"
                    )
        return warnings
    
    def find_next_available_slot(self, duration: int, pet_name: str,
                              search_from: datetime = None) -> datetime:
        """Find the next gap in a pet's schedule that fits a task of given duration."""
        search_from = search_from or datetime.now()
        pet_tasks = sorted(
            [t for t in self.filter_by_pet(pet_name)
            if t.due_time >= search_from and not t.completed],
            key=lambda t: t.due_time
        )
        candidate = search_from.replace(second=0, microsecond=0)
        for task in pet_tasks:
            slot_end = candidate + timedelta(minutes=duration)
            if slot_end <= task.due_time:
                return candidate       # gap before this task is big enough
            # push candidate past the end of this task
            candidate = task.due_time + timedelta(minutes=task.duration)
        return candidate               # no conflicts found — use this time

    def weighted_priority_score(self, task: Task) -> float:
        """Score a task combining priority, overdue status, and recurrence.
        Lower score = should be done sooner."""
        score = task.priority * 10
        if task.is_overdue():
            score -= 20               # overdue tasks jump to the front
        if task.recurrence:
            score -= 5                # recurring tasks are slightly more urgent
        return score

    def smart_prioritize(self) -> list[Task]:
        """Sort today's pending tasks by weighted score, then due time."""
        pending = [t for t in self.get_todays_tasks() if not t.completed]
        return sorted(pending, key=lambda t: (self.weighted_priority_score(t), t.due_time))