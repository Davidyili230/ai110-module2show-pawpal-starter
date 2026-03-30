from datetime import datetime
from pawpal_system import Task, Pet, Owner, Scheduler, Frequency

# --- Setup ---
owner = Owner(name="Alex Johnson", email="alex@example.com")

dog = Pet(name="Buddy", species="Dog", age=3)
cat = Pet(name="Whiskers", species="Cat", age=5)

owner.add_pet(dog)
owner.add_pet(cat)

# --- Add Tasks ---
dog.add_task(Task(
    description="Morning walk",
    duration_minutes=30,
    due_time=datetime.now().replace(hour=7, minute=0, second=0, microsecond=0),
    recurrence=Frequency.DAILY,
))

dog.add_task(Task(
    description="Feed Buddy",
    duration_minutes=5,
    due_time=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0),
    recurrence=Frequency.DAILY,
))

cat.add_task(Task(
    description="Feed Whiskers",
    duration_minutes=5,
    due_time=datetime.now().replace(hour=8, minute=30, second=0, microsecond=0),
    recurrence=Frequency.DAILY,
))

cat.add_task(Task(
    description="Clean litter box",
    duration_minutes=10,
    due_time=datetime.now().replace(hour=18, minute=0, second=0, microsecond=0),
    recurrence=Frequency.DAILY,
))

dog.add_task(Task(
    description="Evening walk",
    duration_minutes=45,
    due_time=datetime.now().replace(hour=19, minute=0, second=0, microsecond=0),
    recurrence=Frequency.DAILY,
))

# --- Scheduler ---
scheduler = Scheduler(owner)

# --- Print Today's Schedule ---
print("=" * 50)
print(f"  TODAY'S SCHEDULE  —  {datetime.now().strftime('%A, %B %d %Y')}")
print(f"  Owner: {owner.name}")
print("=" * 50)

tasks = scheduler.get_upcoming_tasks()
if not tasks:
    print("  No upcoming tasks today!")
else:
    for task in tasks:
        time_str = task.due_time.strftime("%I:%M %p") if task.due_time else "Anytime"
        status = "[x]" if task.is_complete else "[ ]"
        print(f"  {status}  {time_str}  |  {task.description}  ({task.duration_minutes} min)")

print("=" * 50)
stats = scheduler.summary()
print(f"  Pets: {stats['total_pets']}  |  Pending: {stats['pending']}  |  Done: {stats['completed']}")
print("=" * 50)
