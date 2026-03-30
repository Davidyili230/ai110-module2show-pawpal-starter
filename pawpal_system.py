from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional, List
import uuid


class Frequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    description: str
    duration_minutes: int
    due_time: Optional[datetime] = None
    recurrence: Frequency = Frequency.ONCE
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_complete: bool = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.is_complete = True

    def __repr__(self):
        """Return a human-readable string representation of the task."""
        status = "done" if self.is_complete else "pending"
        return f"Task({self.description!r}, {self.duration_minutes}min, {status})"


@dataclass
class Pet:
    name: str
    species: str
    age: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def __repr__(self):
        """Return a human-readable string representation of the pet."""
        return f"Pet({self.name!r}, {self.species}, age={self.age})"


@dataclass
class Owner:
    name: str
    email: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Register a pet under this owner's care."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> bool:
        """Remove a pet by ID, returning True if found and removed."""
        for i, pet in enumerate(self.pets):
            if pet.id == pet_id:
                self.pets.pop(i)
                return True
        return False

    def get_all_tasks(self) -> list[Task]:
        """Collect and return all tasks across every owned pet."""
        return [task for pet in self.pets for task in pet.tasks]

    def __repr__(self):
        """Return a human-readable string representation of the owner."""
        return f"Owner({self.name!r}, pets={len(self.pets)})"


class Scheduler:
    def __init__(self, owner: "Owner"):
        """Initialize the scheduler for the given owner."""
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Delegate to owner to retrieve all tasks across all pets."""
        return self.owner.get_all_tasks()

    def get_upcoming_tasks(self) -> list[Task]:
        """Return incomplete tasks sorted by due time, undated tasks last."""
        now = datetime.now()
        upcoming = []
        for task in self.get_all_tasks():
            if task.is_complete:
                continue
            if task.due_time is None or task.due_time >= now:
                upcoming.append(task)
        return sorted(
            upcoming,
            key=lambda t: (t.due_time or datetime.max),
        )

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return tasks sorted by due_time ascending; undated tasks sort last.

        If *tasks* is provided, sort that list. Otherwise sort all tasks owned
        by this scheduler's owner (including completed ones).
        """
        source = tasks if tasks is not None else self.get_all_tasks()
        return sorted(source, key=lambda t: (t.due_time or datetime.max))

    def filter_by_status(self, complete: bool) -> list[Task]:
        """Return all tasks whose completion status matches *complete*."""
        return [t for t in self.get_all_tasks() if t.is_complete == complete]

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks belonging to the pet whose name matches *pet_name* (case-insensitive)."""
        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                return list(pet.tasks)
        return []

    def mark_task_complete(self, task_id: str) -> bool:
        """Mark a task complete and, for daily/weekly tasks, schedule the next occurrence.

        Searches each pet's task list directly so the next occurrence can be
        attached to the correct pet using timedelta arithmetic:
          - Frequency.DAILY  → due_time + timedelta(days=1)
          - Frequency.WEEKLY → due_time + timedelta(weeks=1)

        Returns True if the task was found and marked complete, False otherwise.
        """
        from datetime import timedelta

        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.id != task_id:
                    continue
                task.mark_complete()
                if task.due_time is not None:
                    if task.recurrence == Frequency.DAILY:
                        next_due = task.due_time + timedelta(days=1)
                    elif task.recurrence == Frequency.WEEKLY:
                        next_due = task.due_time + timedelta(weeks=1)
                    else:
                        next_due = None
                    if next_due is not None:
                        pet.add_task(Task(
                            description=task.description,
                            duration_minutes=task.duration_minutes,
                            due_time=next_due,
                            recurrence=task.recurrence,
                        ))
                return True
        return False

    def check_conflicts(self, task: Task) -> Optional[str]:
        """Return a warning message if the given task overlaps with any existing task, else None.

        Lightweight strategy: scan all scheduled tasks and compare time windows using
        interval-overlap arithmetic (task starts before other ends AND ends after other starts).
        Returns the first conflict found as a human-readable string so callers can print
        a warning without crashing.
        """
        if task.due_time is None:
            return None
        task_end = datetime.fromtimestamp(
            task.due_time.timestamp() + task.duration_minutes * 60
        )
        for pet in self.owner.pets:
            for existing in pet.tasks:
                if existing is task or existing.due_time is None:
                    continue
                existing_end = datetime.fromtimestamp(
                    existing.due_time.timestamp() + existing.duration_minutes * 60
                )
                if task.due_time < existing_end and task_end > existing.due_time:
                    return (
                        f"WARNING: '{task.description}' "
                        f"({task.due_time.strftime('%I:%M %p')}–"
                        f"{task_end.strftime('%I:%M %p')}) conflicts with "
                        f"'{existing.description}' for {pet.name} "
                        f"({existing.due_time.strftime('%I:%M %p')}–"
                        f"{existing_end.strftime('%I:%M %p')})"
                    )
        return None

    def generate_recurring_tasks(self) -> list[Task]:
        """Create the next occurrence for each daily or weekly recurring task."""
        from datetime import timedelta

        generated = []
        for task in self.get_all_tasks():
            if task.recurrence == Frequency.DAILY and task.due_time:
                next_task = Task(
                    description=task.description,
                    duration_minutes=task.duration_minutes,
                    due_time=task.due_time + timedelta(days=1),
                    recurrence=task.recurrence,
                )
                generated.append(next_task)
            elif task.recurrence == Frequency.WEEKLY and task.due_time:
                next_task = Task(
                    description=task.description,
                    duration_minutes=task.duration_minutes,
                    due_time=task.due_time + timedelta(weeks=1),
                    recurrence=task.recurrence,
                )
                generated.append(next_task)
        return generated

    def summary(self) -> dict:
        """Return a dict with counts of pets, total tasks, pending, and completed."""
        all_tasks = self.get_all_tasks()
        pending = [t for t in all_tasks if not t.is_complete]
        completed = [t for t in all_tasks if t.is_complete]
        return {
            "owner": self.owner.name,
            "total_pets": len(self.owner.pets),
            "total_tasks": len(all_tasks),
            "pending": len(pending),
            "completed": len(completed),
        }
