from flask import Flask, render_template, request
import csv
import os
import random

app = Flask(__name__)

EMPLOYEE_FILE = "employees.csv"   # emp_id,name
ASSIGNED_FILE = "assigned.csv"    # giver_id,receiver_id


# ✅ Load employees from CSV → {id: name}
def load_employees():
    employees = {}
    with open(EMPLOYEE_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            employees[row["emp_id"].strip()] = row["name"].strip()
    return employees


# ✅ Load assigned pairs → {giver_id: receiver_id}
def load_assigned():
    if not os.path.exists(ASSIGNED_FILE):
        return {}

    assigned = {}
    with open(ASSIGNED_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            assigned[row["giver_id"]] = row["receiver_id"]
    return assigned


# ✅ Save assigned pairs back to CSV
def save_assigned(assigned):
    with open(ASSIGNED_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["giver_id", "receiver_id"])
        for giver, receiver in assigned.items():
            writer.writerow([giver, receiver])


# ✅ Log status to Render logs
def log_status(employees, assigned):
    all_ids = list(employees.keys())
    matched = assigned.keys()
    unmatched = [i for i in all_ids if i not in matched]

    print("\n===== SECRET SANTA STATUS =====")

    print("\nMatched:")
    for giver, receiver in assigned.items():
        print(f"  {employees[giver]} → {employees[receiver]}")

    print("\nUnmatched:")
    for uid in unmatched:
        print(f"  {uid} - {employees[uid]}")

    print("================================\n")


@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    result = None

    employees = load_employees()   # {id: name}
    assigned = load_assigned()     # {giver_id: receiver_id}

    if request.method == "POST":
        user_input = request.form.get("username", "").strip()

        # ✅ Case-insensitive ID match
        emp_id = None
        for eid in employees:
            if eid.lower() == user_input.lower():
                emp_id = eid
                break

        if not emp_id:
            message = "Employee ID not found."
            return render_template("index.html", message=message)

        # ✅ Already assigned?
        if emp_id in assigned:
            receiver_name = employees[assigned[emp_id]]
            result = f"You have already drawn: {receiver_name}"
            return render_template("index.html", result=result)

        # ✅ Find available receivers
        all_ids = list(employees.keys())
        taken_receivers = set(assigned.values())

        # ✅ No self-matching + no duplicate receivers
        available = [
            i for i in all_ids
            if i not in taken_receivers and i.lower() != emp_id.lower()
        ]

        if not available:
            message = "No available employees left to assign."
            return render_template("index.html", message=message)

        # ✅ Assign random friend
        receiver_id = random.choice(available)
        assigned[emp_id] = receiver_id
        save_assigned(assigned)

        # ✅ Log to Render logs
        log_status(employees, assigned)

        giver_name = employees[emp_id]
        receiver_name = employees[receiver_id]

        result = f"{giver_name}, your assigned friend is: {receiver_name}"

        # ✅ All paired?
        if len(assigned) == len(employees):
            print("🎉 All employees have been successfully paired!")

    return render_template("index.html", message=message, result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
