import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from tools import get_project_state
from agent import run_agent


def check_project_health():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running project health check...")
    state = get_project_state()
    tasks = state["tasks"]

    stalled_or_at_risk = [
        t for t in tasks if t["status"] in ("not_started", "in_progress")
    ]

    if not stalled_or_at_risk:
        print("No active tasks to check.")
        return

    summary = "\n".join(
        f"- {t['title']} (status: {t['status']}, due: {t['due_date']})"
        for t in stalled_or_at_risk
    )
    prompt = (
        "Here is the current project state:\n"
        f"{summary}\n\n"
        "Review this and write a short, direct nudge for the freelancer — "
        "flag anything overdue or at risk, and suggest one concrete next action. "
        "Keep it to 2-3 sentences."
    )
    nudge = run_agent(prompt)
    print(f"AGENT NUDGE: {nudge}")


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_project_health, "interval", seconds=30)  # every 30s for testing
    scheduler.start()

    print("Scheduler started. Checking project health every 30 seconds. Press Ctrl+C to stop.")
    check_project_health()  # run once immediately so you don't wait

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("Scheduler stopped.")