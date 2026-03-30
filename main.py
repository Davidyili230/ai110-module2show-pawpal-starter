from datetime import datetime
from pawpal_system import Task, Pet, Owner, Scheduler, Frequency

# --- Setup ---
owner = Owner(name="Alex Johnson", email="alex@example.com")

dog = Pet(name="Buddy", species="Dog", age=3)
cat = Pet(name="Whiskers", species="Cat", age=5)

owner.add_pet(dog)
owner.add_pet(cat)

# --- Add Tasks OUT OF ORDER to demonstrate sorting ---
dog.add_task(Task(
    description="Evening walk",
    duration_minutes=45,
    due_time=datetime.now().replace(hour=19, minute=0, second=0, microsecond=0),
    recurrence=Frequency.DAILY,
))

cat.add_task(Task(
    description="Clean litter box",
    duration_minutes=10,
    due_time=datetime.now().replace(hour=18, minute=0, second=0, microsecond=0),
    recurrence=Frequency.DAILY,
))

dog.add_task(Task(
    description="Morning walk",
    duration_minutes=30,
    due_time=datetime.now().replace(hour=7, minute=0, second=0, microsecond=0),
    recurrence=Frequency.DAILY,
))

cat.add_task(Task(
    description="Feed Whiskers",
    duration_minutes=5,
    due_time=datetime.now().replace(hour=8, minute=30, second=0, microsecond=0),
    recurrence=Frequency.DAILY,
))

dog.add_task(Task(
    description="Feed Buddy",
    duration_minutes=5,
    due_time=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0),
    recurrence=Frequency.DAILY,
))

# --- Scheduler ---
scheduler = Scheduler(owner)

# --- Mark one task complete for filtering demo ---
all_tasks = scheduler.get_all_tasks()
all_tasks[0].mark_complete()  # mark "Evening walk" complete

# ── Section 1: All tasks sorted by time ─────────────────────────────────────
print("=" * 55)
print(f"  ALL TASKS SORTED BY TIME  —  {datetime.now().strftime('%A, %B %d %Y')}")
print("=" * 55)
for task in scheduler.sort_by_time():
    time_str = task.due_time.strftime("%I:%M %p") if task.due_time else "Anytime"
    status = "[x]" if task.is_complete else "[ ]"
    print(f"  {status}  {time_str}  |  {task.description}  ({task.duration_minutes} min)")

# ── Section 2: Filter — pending tasks only ──────────────────────────────────
print()
print("=" * 55)
print("  PENDING TASKS ONLY")
print("=" * 55)
for task in scheduler.sort_by_time(scheduler.filter_by_status(complete=False)):
    time_str = task.due_time.strftime("%I:%M %p") if task.due_time else "Anytime"
    print(f"  [ ]  {time_str}  |  {task.description}  ({task.duration_minutes} min)")

# ── Section 3: Filter — completed tasks only ────────────────────────────────
print()
print("=" * 55)
print("  COMPLETED TASKS")
print("=" * 55)
completed = scheduler.filter_by_status(complete=True)
if completed:
    for task in scheduler.sort_by_time(completed):
        time_str = task.due_time.strftime("%I:%M %p") if task.due_time else "Anytime"
        print(f"  [x]  {time_str}  |  {task.description}  ({task.duration_minutes} min)")
else:
    print("  No completed tasks.")

# ── Section 4: Filter — tasks by pet name ───────────────────────────────────
for pet_name in ("Buddy", "Whiskers"):
    print()
    print("=" * 55)
    print(f"  TASKS FOR {pet_name.upper()}")
    print("=" * 55)
    pet_tasks = scheduler.filter_by_pet(pet_name)
    for task in scheduler.sort_by_time(pet_tasks):
        time_str = task.due_time.strftime("%I:%M %p") if task.due_time else "Anytime"
        status = "[x]" if task.is_complete else "[ ]"
        print(f"  {status}  {time_str}  |  {task.description}  ({task.duration_minutes} min)")

# ── Section 5: Recurring task auto-scheduling ───────────────────────────────
print()
print("=" * 55)
print("  RECURRING TASK AUTO-SCHEDULING")
print("=" * 55)

# Find the pending "Morning walk" task to complete
morning_walk = next(
    t for t in scheduler.filter_by_pet("Buddy") if t.description == "Morning walk"
)
print(f"  Completing '{morning_walk.description}' (due {morning_walk.due_time.strftime('%b %d %I:%M %p')})...")
scheduler.mark_task_complete(morning_walk.id)

buddy_tasks = scheduler.sort_by_time(scheduler.filter_by_pet("Buddy"))
print(f"  Buddy now has {len(buddy_tasks)} task(s):")
for task in buddy_tasks:
    time_str = task.due_time.strftime("%b %d %I:%M %p") if task.due_time else "Anytime"
    status = "[x]" if task.is_complete else "[ ]"
    print(f"    {status}  {time_str}  |  {task.description}")

# ── Section 7: Conflict detection ───────────────────────────────────────────
print()
print("=" * 55)
print("  CONFLICT CHECK")
print("=" * 55)

# Task that overlaps with "Morning walk" (07:00, 30 min) — same pet
conflict_task_1 = Task(
    description="Vet appointment",
    duration_minutes=60,
    due_time=datetime.now().replace(hour=7, minute=15, second=0, microsecond=0),
)
warning = scheduler.check_conflicts(conflict_task_1)
if warning:
    print(f"  {warning}")
else:
    print(f"  '{conflict_task_1.description}' — no conflicts.")

# Task that overlaps with "Feed Whiskers" (08:30, 5 min) — different pet, same time window
conflict_task_2 = Task(
    description="Bath time for Buddy",
    duration_minutes=20,
    due_time=datetime.now().replace(hour=8, minute=30, second=0, microsecond=0),
)
warning2 = scheduler.check_conflicts(conflict_task_2)
if warning2:
    print(f"  {warning2}")
else:
    print(f"  '{conflict_task_2.description}' — no conflicts.")

# Task with no overlap — should be clean
safe_task = Task(
    description="Afternoon nap check",
    duration_minutes=10,
    due_time=datetime.now().replace(hour=14, minute=0, second=0, microsecond=0),
)
warning3 = scheduler.check_conflicts(safe_task)
if warning3:
    print(f"  {warning3}")
else:
    print(f"  '{safe_task.description}' — no conflicts.")

# ── Summary ──────────────────────────────────────────────────────────────────
print()
print("=" * 55)
stats = scheduler.summary()
print(f"  Pets: {stats['total_pets']}  |  Pending: {stats['pending']}  |  Done: {stats['completed']}")
print("=" * 55)
