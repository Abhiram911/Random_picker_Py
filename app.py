from flask import Flask, render_template, request
import json
import os
import random

app = Flask(__name__)

NAMES_FILE = "names.txt"
STATE_FILE = "assigned.json"

def load_names():
    with open(NAMES_FILE, "r") as f:
        return [name.strip() for name in f.readlines() if name.strip()]

def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def get_available_receivers(all_names, assigned):
    assigned_receivers = set(assigned.values())
    return [name for name in all_names if name not in assigned_receivers]

@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    result = None

    all_names = load_names()
    assigned = load_state()

    if request.method == "POST":
        user_input = request.form.get("username", "").strip()

        # Case-insensitive match
        matched_name = None
        for name in all_names:
            if name.lower() == user_input.lower():
                matched_name = name
                break

        if not matched_name:
            message = "Name not found in the list."
            return render_template("index.html", message=message)

        if matched_name in assigned:
            result = f"You have already drawn: {assigned[matched_name]}"
            return render_template("index.html", result=result)

        available = get_available_receivers(all_names, assigned)

        # Remove self
        available = [name for name in available if name.lower() != matched_name.lower()]

        if not available:
            message = "No available names left to assign."
            return render_template("index.html", message=message)

        friend = random.choice(available)
        assigned[matched_name] = friend
        save_state(assigned)

        result = f"{matched_name}, your assigned friend is: {friend}"

        if len(assigned) == len(all_names):
            message = "🎉 All 20 people have been successfully paired!"

    return render_template("index.html", message=message, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
