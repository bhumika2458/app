import json
from datetime import datetime, timedelta
import os
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        CYAN = ''
    class Style:
        RESET_ALL = ''

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

TASK_FILE = "tasks.json"
USER_FILE = "user_settings.json"

# --- Load tasks ---
def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r") as f:
            return json.load(f)
    return []

# --- Save tasks ---
def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

# --- Load user settings ---
def load_user():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

# --- Save user settings ---
def save_user(user):
    with open(USER_FILE, "w") as f:
        json.dump(user, f, indent=4)

# --- Notifications ---
def send_notification(title, message):
    if PLYER_AVAILABLE:
        notification.notify(title=title, message=message)
    else:
        print(Fore.YELLOW + f"[Notification] {title}: {message}")

# --- Add task ---
def add_task(tasks):
    title = input("Task title: ")
    category = input("Category (Work/Personal/Study/Health): ")
    priority = input("Priority (High/Medium/Low): ")
    due_date = input("Due date (YYYY-MM-DD): ")
    recurrence = input("Recurring? (none/daily/weekly/monthly): ").lower()
    
    task = {
        "title": title,
        "category": category,
        "priority": priority,
        "due_date": due_date,
        "recurrence": recurrence,
        "done": False
    }
    tasks.append(task)
    save_tasks(tasks)
    print(Fore.GREEN + f"Task '{title}' added!")

# --- Handle recurring tasks ---
def handle_recurring(tasks):
    today = datetime.today()
    updated = False
    for task in tasks:
        if task["done"] and task["recurrence"] != "none":
            due_date = datetime.strptime(task["due_date"], "%Y-%m-%d")
            if task["recurrence"] == "daily":
                new_date = due_date + timedelta(days=1)
            elif task["recurrence"] == "weekly":
                new_date = due_date + timedelta(weeks=1)
            elif task["recurrence"] == "monthly":
                month = due_date.month + 1 if due_date.month < 12 else 1
                year = due_date.year + 1 if month == 1 else due_date.year
                day = min(due_date.day, 28)
                new_date = due_date.replace(year=year, month=month, day=day)
            task["due_date"] = new_date.strftime("%Y-%m-%d")
            task["done"] = False
            updated = True
    if updated:
        save_tasks(tasks)

# --- View tasks ---
def view_tasks(tasks, view_type="weekly"):
    today = datetime.today()
    print(Fore.CYAN + f"\n--- {view_type.capitalize()} Tasks ---")
    filtered = []
    for idx, task in enumerate(tasks):
        task_date = datetime.strptime(task["due_date"], "%Y-%m-%d")
        if view_type == "weekly" and 0 <= (task_date - today).days <= 7:
            filtered.append((idx, task))
        elif view_type == "monthly" and 0 <= (task_date - today).days <= 30:
            filtered.append((idx, task))
    if not filtered:
        print(Fore.YELLOW + "No tasks found for this period!")
        return
    for idx, task in filtered:
        status = Fore.GREEN + "✅" if task["done"] else Fore.RED + "❌"
        print(f"{idx+1}. [{status}{Style.RESET_ALL}] {task['title']} - {task['category']} - Due: {task['due_date']} - Priority: {task['priority']}")

# --- Complete task ---
def complete_task(tasks):
    view_tasks(tasks, "monthly")
    try:
        num = int(input("Enter task number to mark as done: ")) - 1
        if 0 <= num < len(tasks):
            tasks[num]["done"] = True
            save_tasks(tasks)
            print(Fore.GREEN + f"Task '{tasks[num]['title']}' completed!")
            handle_recurring(tasks)
        else:
            print(Fore.RED + "Invalid task number!")
    except ValueError:
        print(Fore.RED + "Invalid input!")

# --- AI Suggestions ---
def suggest_tasks(tasks):
    today = datetime.today()
    high_tasks = sorted([t for t in tasks if t["priority"].lower() == "high" and not t["done"]],
                        key=lambda x: datetime.strptime(x["due_date"], "%Y-%m-%d"))
    print(Fore.YELLOW + "\n--- AI Suggested Tasks ---")
    for task in high_tasks[:5]:
        print(f"{task['title']} - Due: {task['due_date']} - Category: {task['category']}")
        days_left = (datetime.strptime(task["due_date"], "%Y-%m-%d") - today).days
        if days_left <= 1:
            send_notification("Urgent Task!", f"{task['title']} is due soon!")

# --- Task Stats ---
def task_stats(tasks):
    total = len(tasks)
    done = len([t for t in tasks if t["done"]])
    pending = total - done
    print(Fore.BLUE + f"\nTotal Tasks: {total} | Completed: {done} | Pending: {pending}")

# --- Main ---
def main():
    user = load_user()
    if not user.get("name"):
        user["name"] = input("Enter your name: ")
        user["theme"] = "default"
        user["default_view"] = "weekly"
        save_user(user)
    print(Fore.CYAN + f"\nHello, {user['name']}! Welcome to Smart Task Organizer.\n")
    
    tasks = load_tasks()
    handle_recurring(tasks)
    
    while True:
        print(Fore.CYAN + "\n=== Menu ===")
        print("1. Add Task")
        print("2. View Weekly Tasks")
        print("3. View Monthly Tasks")
        print("4. Complete Task")
        print("5. AI Suggested Tasks")
        print("6. Task Stats")
        print("7. Exit")
        choice = input("Choice: ")
        
        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            view_tasks(tasks, "weekly")
        elif choice == "3":
            view_tasks(tasks, "monthly")
        elif choice == "4":
            complete_task(tasks)
        elif choice == "5":
            suggest_tasks(tasks)
        elif choice == "6":
            task_stats(tasks)
        elif choice == "7":
            print(Fore.CYAN + f"Goodbye, {user['name']}!")
            break
        else:
            print(Fore.RED + "Invalid choice!")

if __name__ == "__main__":
    main()
