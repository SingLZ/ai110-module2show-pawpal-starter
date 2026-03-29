from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

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