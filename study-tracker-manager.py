from datetime import datetime
import matplotlib.pyplot as plt
import oracledb

# ----------------- Database Connection -----------------
conn = oracledb.connect("system/Akshay@90537@localhost/XE")
cursor = conn.cursor()

# ----------------- Fixed Subject List -----------------
SUBJECTS = ["Math", "Physics", "Chemistry", "English", "CS"]

# ----------------- Helper Functions -----------------
def get_date():
    date_str = input("Enter date (YYYY-MM-DD) or leave blank for today: ")
    if date_str == "":
        return datetime.now().date()
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def get_subjects():
    subjects = {}
    print("\n📘 Enter study time for subjects (leave blank to skip):")
    for subject in SUBJECTS:
        try:
            time_str = input(f"Time spent on {subject} (minutes): ").strip()
            if time_str == "":
                continue
            time = int(time_str)
        except ValueError:
            print("Enter numeric value for time.")
            continue
        subjects[subject] = subjects.get(subject, 0) + time
    return subjects

def get_notes():
    return input("Any notes for today? (optional): ")

def save_data(date, subjects, notes):
    total_time = sum(subjects.values())

    # Check if this date already exists
    cursor.execute("SELECT id, total_study_time FROM study_log WHERE study_date = :dt", {"dt": date})
    row = cursor.fetchone()

    if row:
        log_id, old_total = row
        new_total = old_total + total_time

        # Update the main study_log table
        cursor.execute(
            "UPDATE study_log SET total_study_time = :tt WHERE id = :id",
            {"tt": new_total, "id": log_id}
        )

        # Update/insert subject times
        for subject, time in subjects.items():
            cursor.execute(
                "SELECT time_spent FROM study_subjects WHERE log_id = :id AND subject_name = :sub",
                {"id": log_id, "sub": subject}
            )
            sub_row = cursor.fetchone()
            if sub_row:
                new_time = sub_row[0] + time
                cursor.execute(
                    "UPDATE study_subjects SET time_spent = :tm WHERE log_id = :id AND subject_name = :sub",
                    {"tm": new_time, "id": log_id, "sub": subject}
                )
            else:
                cursor.execute(
                    "INSERT INTO study_subjects (log_id, subject_name, time_spent) VALUES (:id, :sub, :tm)",
                    {"id": log_id, "sub": subject, "tm": time}
                )

    else:
        # Insert new row for this date
        cursor.execute(
            "INSERT INTO study_log (study_date, total_study_time, notes) VALUES (:dt, :tt, :nt)",
            {"dt": date, "tt": total_time, "nt": notes}
        )
        cursor.execute("SELECT id FROM study_log WHERE study_date = :dt ORDER BY id DESC", {"dt": date})
        log_id = cursor.fetchone()[0]

        # Insert subject data
        for subject, time in subjects.items():
            cursor.execute(
                "INSERT INTO study_subjects (log_id, subject_name, time_spent) VALUES (:id, :sub, :tm)",
                {"id": log_id, "sub": subject, "tm": time}
            )

    conn.commit()
    print("✅ Data saved successfully!")

# ----------------- New Log Entry -----------------
def new_log_entry():
    date = get_date()
    subjects = get_subjects()
    notes = get_notes()
    save_data(date, subjects, notes)

# ----------------- Summary -----------------
def show_summary():
    cursor.execute("SELECT study_date, total_study_time, notes FROM study_log ORDER BY study_date DESC")
    rows = cursor.fetchall()
    print("\n ---- Study Summary ----")
    for row in rows:
        print(f"Date: {row[0]} | Total: {row[1]} mins | Notes: {row[2]}")

def show_subject_summary():
    cursor.execute("SELECT subject_name, SUM(time_spent) FROM study_subjects GROUP BY subject_name")
    rows = cursor.fetchall()
    print("\n ---- Subject Summary ----")
    for row in rows:
        if row[0] in SUBJECTS:
            print(f"{row[0]}: {row[1]} minutes ({row[1]/60:.2f} hours)")

# ----------------- Clear Data -----------------
def clear_data():
    confirm = input("⚠️ Are you sure you want to delete ALL data? (yes/no): ")
    if confirm.lower() == "yes":
        cursor.execute("DELETE FROM study_subjects")
        cursor.execute("DELETE FROM study_log")
        conn.commit()
        print("✅ All data cleared!")

# ----------------- Goals -----------------
def add_goal():
    subject = input("Enter subject for goal: ")
    if subject not in SUBJECTS:
        print("⚠️ Subject not in list. Add it first.")
        return
    goal_type = input("Goal type (daily/weekly): ").lower()
    goal_time = int(input("Enter goal time (minutes): "))
    cursor.execute(
        "INSERT INTO study_goals (goal_type, subject_name, goal_time) VALUES (:1, :2, :3)",
        (goal_type, subject, goal_time)
    )
    conn.commit()
    print("✅ Goal added successfully!")

def check_goals():
    cursor.execute("SELECT * FROM study_goals")
    goals = cursor.fetchall()
    print("\n---- Goal Progress ----")
    for goal in goals:
        goal_id, goal_type, subject, goal_time = goal
        if subject not in SUBJECTS:
            continue
        if goal_type == "daily":
            cursor.execute(
                "SELECT SUM(time_spent) FROM study_subjects s JOIN study_log l ON s.log_id = l.id "
                "WHERE s.subject_name=:1 AND l.study_date=TRUNC(SYSDATE)",
                (subject,)
            )
        else:  # weekly
            cursor.execute(
                "SELECT SUM(time_spent) FROM study_subjects s JOIN study_log l ON s.log_id = l.id "
                "WHERE s.subject_name=:1 AND TRUNC(l.study_date,'IW') = TRUNC(SYSDATE,'IW')",
                (subject,)
            )
        result = cursor.fetchone()[0] or 0
        print(f"{subject} ({goal_type}): {result}/{goal_time} mins ({result/goal_time*100:.2f}%)")

# ----------------- Analytics -----------------
def best_worst_day():
    cursor.execute("SELECT study_date, total_study_time FROM study_log ORDER BY total_study_time DESC FETCH FIRST 1 ROWS ONLY")
    best = cursor.fetchone()
    cursor.execute("SELECT study_date, total_study_time FROM study_log ORDER BY total_study_time ASC FETCH FIRST 1 ROWS ONLY")
    worst = cursor.fetchone()
    print(f"\n🏆 Best Day: {best[0]} -> {best[1]} mins")
    print(f"⚠️ Worst Day: {worst[0]} -> {worst[1]} mins")

def streak_tracker():
    cursor.execute("SELECT study_date FROM study_log ORDER BY study_date ASC")
    rows = [row[0] for row in cursor.fetchall()]
    if not rows:
        print("No data to calculate streak.")
        return
    max_streak = streak = 1
    for i in range(1, len(rows)):
        if (rows[i] - rows[i-1]).days == 1:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 1
    print(f"\n🔥 Maximum Study Streak: {max_streak} consecutive days")

# ----------------- Graphs -----------------
def graph_total_time():
    cursor.execute("SELECT study_date, total_study_time FROM study_log ORDER BY study_date ASC")
    rows = cursor.fetchall()
    if not rows:
        print("No data for graph.")
        return
    dates = [row[0] for row in rows]
    times = [row[1] for row in rows]
    plt.plot(dates, times, marker='o')
    plt.title("Total Study Time Over Days")
    plt.xlabel("Date")
    plt.ylabel("Time (minutes)")
    plt.xticks(dates, rotation=30)
    if len(dates) > 1:
        plt.xlim(min(dates), max(dates)) 
    
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def graph_subjects():
    print("\n📊 Subject-wise Graph Options")
    print("1. For a specific date")
    print("2. For this week")
    print("3. For this month")
    choice = input("Enter choice (1/2/3): ")

    if choice == "1":
        date_str = input("Enter date (YYYY-MM-DD): ")
        cursor.execute("""
            SELECT subject_name, time_spent 
            FROM study_log sl
            JOIN study_subjects ss ON sl.id = ss.log_id
            WHERE sl.study_date = TO_DATE(:dt, 'YYYY-MM-DD')
        """, {"dt": date_str})
        rows = cursor.fetchall()
        if not rows:
            print("⚠️ No data found for this date.")
            return

        subjects, times = zip(*rows)
        plt.bar(subjects, times)
        plt.title(f"Study Time on {date_str}")
        plt.xlabel("Subjects")
        plt.ylabel("Minutes")
        plt.show()

    elif choice == "2":  # Current week automatically
        cursor.execute("""
            SELECT subject_name, SUM(time_spent) 
            FROM study_log sl
            JOIN study_subjects ss ON sl.id = ss.log_id
            WHERE TRUNC(sl.study_date, 'IW') = TRUNC(SYSDATE, 'IW')
            GROUP BY subject_name
        """)
        rows = cursor.fetchall()
        if not rows:
            print("⚠️ No data found for this week.")
            return

        subjects, times = zip(*rows)
        plt.bar(subjects, times)
        plt.title("Study Time (This Week)")
        plt.xlabel("Subjects")
        plt.ylabel("Minutes")
        plt.show()

    elif choice == "3":  # Current month automatically
        cursor.execute("""
            SELECT subject_name, SUM(time_spent) 
            FROM study_log sl
            JOIN study_subjects ss ON sl.id = ss.log_id
            WHERE TRUNC(sl.study_date, 'MM') = TRUNC(SYSDATE, 'MM')
            GROUP BY subject_name
        """)
        rows = cursor.fetchall()
        if not rows:
            print("⚠️ No data found for this month.")
            return

        subjects, times = zip(*rows)
        plt.bar(subjects, times)
        plt.title("Study Time (This Month)")
        plt.xlabel("Subjects")
        plt.ylabel("Minutes")
        plt.show()

    else:
        print("⚠️ Invalid choice.")


# ----------------- Reports -----------------
def weekly_report():
    cursor.execute("""
        SELECT SUM(total_study_time) 
        FROM study_log 
        WHERE study_date >= TRUNC(SYSDATE,'IW') 
    """)
    total = cursor.fetchone()[0] or 0
    print(f"\n📅 Weekly Study Time: {total} minutes ({total/60:.2f} hours)")

def monthly_report():
    cursor.execute("""
        SELECT SUM(total_study_time) 
        FROM study_log 
        WHERE study_date >= TRUNC(SYSDATE,'MM') 
    """)
    total = cursor.fetchone()[0] or 0
    print(f"\n🗓️ Monthly Study Time: {total} minutes ({total/60:.2f} hours)")

# ----------------- Subject Management -----------------
def add_subject():
    new_subject = input("Enter new subject name: ").strip()
    if new_subject in SUBJECTS:
        print("⚠️ Subject already exists.")
    else:
        SUBJECTS.append(new_subject)
        print(f"✅ Subject '{new_subject}' added.")

def remove_subject():
    subject = input("Enter subject to remove: ").strip()
    if subject not in SUBJECTS:
        print("⚠️ Subject not found.")
    else:
        SUBJECTS.remove(subject)
        print(f"✅ Subject '{subject}' removed.")

# ----------------- Main Menu -----------------
def main():
    while True:
        print("\n📘 Study Tracker Menu")
        print("1. Log new data")
        print("2. Show summary")
        print("3. Subject-wise summary")
        print("4. Add goal")
        print("5. Check goals")
        print("6. Best/Worst day")
        print("7. Streak tracker")
        print("8. Weekly report")
        print("9. Monthly report")
        print("10. Graph: total time over days")
        print("11. Graph: subject-wise time")
        print("12. Clear data")
        print("13. Add subject")
        print("14. Remove subject")
        print("15. Exit")

        try:
            choice = int(input("Enter choice: "))
        except ValueError:
            print("❌ Invalid input.\n")
            continue

        if choice == 1:
            new_log_entry()
        elif choice == 2:
            show_summary()
        elif choice == 3:
            show_subject_summary()
        elif choice == 4:
            add_goal()
        elif choice == 5:
            check_goals()
        elif choice == 6:
            best_worst_day()
        elif choice == 7:
            streak_tracker()
        elif choice == 8:
            weekly_report()
        elif choice == 9:
            monthly_report()
        elif choice == 10:
            graph_total_time()
        elif choice == 11:
            graph_subjects()
        elif choice == 12:
            clear_data()
        elif choice == 13:
            add_subject()
        elif choice == 14:
            remove_subject()
        elif choice == 15:
            print("👋 Goodbye!")
            break
        else:
            print(" Invalid choice.\n")

if __name__ == "__main__":
    main()
