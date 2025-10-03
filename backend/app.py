"""
Combined Productivity Backend (Tasks + Habits + Expenses + Badges)

Run:
    python app.py

What it provides:
- /health
- /tasks  (GET, POST)
- /tasks/<id> (GET, PUT, DELETE)  [PUT/DELETE included]
- /habits (GET, POST)
- /habits/<id> (GET, PUT, DELETE)
- /habits/<id>/complete (POST) -> updates streak, may award badges
- /expenses (GET, POST)
- /expenses/<id> (GET, PUT, DELETE)
- /badges (GET) -> all awarded badges
- /badges/recent (GET) -> recent awarded badges

Notes:
- Simple SQLite DB: backend/data.db
- Badges are persisted and idempotent by (name + reason)
- API returns `badge_awarded` field in creating endpoints when a badge was awarded
"""

import os
from datetime import date, datetime, timedelta
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# --------------------------
# App + DB setup
# --------------------------
app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --------------------------
# Models
# --------------------------

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default="todo")  # todo, in-progress, done
    created_at = db.Column(db.String(30), default=lambda: datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "description": self.description,
            "status": self.status, "created_at": self.created_at
        }

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    frequency = db.Column(db.String(20), default="daily")  # daily, weekly
    streak = db.Column(db.Integer, default=0)
    last_completed = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.String(30), default=lambda: datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "frequency": self.frequency,
            "streak": self.streak, "last_completed": self.last_completed, "created_at": self.created_at
        }

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), default=date.today().isoformat())
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.String(30), default=lambda: datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            "id": self.id, "amount": self.amount, "category": self.category,
            "date": self.date, "note": self.note, "created_at": self.created_at
        }

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    emoji = db.Column(db.String(8), nullable=True)
    description = db.Column(db.String(300), nullable=True)
    reason = db.Column(db.String(300), nullable=True)  # used to avoid duplicate awards for same rule
    date_awarded = db.Column(db.String(30), default=lambda: datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "emoji": self.emoji,
            "description": self.description, "reason": self.reason, "date_awarded": self.date_awarded
        }

# Create DB init (create tables)
# create tables when the app starts using the application context.
def create_tables():
    db.create_all()

# Create tables once at startup (safe to call repeatedly)
with app.app_context():
    create_tables()

# --------------------------
# Badge utilities
# --------------------------

def badge_exists(name, reason=None):
    q = Badge.query.filter_by(name=name)
    if reason:
        q = q.filter_by(reason=reason)
    return q.first() is not None

def award_badge(name, emoji=None, description=None, reason=None):
    """
    Creates and saves a Badge if not already present with same name+reason.
    Returns the created Badge object or None if no award (duplicate).
    """
    if badge_exists(name, reason):
        return None
    b = Badge(name=name, emoji=emoji, description=description, reason=reason, date_awarded=datetime.utcnow().isoformat())
    db.session.add(b)
    db.session.commit()
    return b

# --------------------------
# Health
# --------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# --------------------------
# TASKS endpoints
# --------------------------
@app.route("/tasks", methods=["GET"])
def list_tasks():
    tasks = Task.query.order_by(Task.id.desc()).all()
    return jsonify([t.to_dict() for t in tasks]), 200

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json() or {}
    title = data.get("title")
    if not title:
        return jsonify({"error":"title is required"}), 400
    t = Task(title=title, description=data.get("description"), status=data.get("status","todo"))
    db.session.add(t)
    db.session.commit()

    # Award badges: first task + generic getting started
    b1 = award_badge("Task Initiate", emoji="📝", description="Created your first task", reason="first_task")
    b2 = award_badge("Getting Started", emoji="🚀", description="First activity in the app", reason="getting_started")

    resp = t.to_dict()
    # include newly awarded badge(s) if any
    if b1:
        resp["badge_awarded"] = b1.to_dict()
    elif b2:
        # If first task didn't award (maybe got by another action), include getting started
        resp["badge_awarded"] = b2.to_dict()
    return jsonify(resp), 201

@app.route("/tasks/<int:tid>", methods=["GET"])
def get_task(tid):
    t = Task.query.get_or_404(tid)
    return jsonify(t.to_dict()), 200

@app.route("/tasks/<int:tid>", methods=["PUT"])
def update_task(tid):
    t = Task.query.get_or_404(tid)
    data = request.get_json() or {}
    if "title" in data: t.title = data.get("title") or t.title
    if "description" in data: t.description = data.get("description")
    if "status" in data: t.status = data.get("status")
    db.session.commit()
    return jsonify(t.to_dict()), 200

@app.route("/tasks/<int:tid>", methods=["DELETE"])
def delete_task(tid):
    t = Task.query.get_or_404(tid)
    db.session.delete(t)
    db.session.commit()
    return "", 204

# --------------------------
# HABITS endpoints
# --------------------------
@app.route("/habits", methods=["GET"])
def list_habits():
    hs = Habit.query.order_by(Habit.id.asc()).all()
    return jsonify([h.to_dict() for h in hs]), 200

@app.route("/habits", methods=["POST"])
def create_habit():
    data = request.get_json() or {}
    name = data.get("name")
    frequency = data.get("frequency","daily")
    if not name:
        return jsonify({"error":"name is required"}), 400
    h = Habit(name=name, frequency=frequency)
    db.session.add(h)
    db.session.commit()

    # Award badges: first habit + getting started
    b1 = award_badge("Habit Seed", emoji="🌱", description="Added your first habit", reason="first_habit")
    b2 = award_badge("Getting Started", emoji="🚀", description="First activity in the app", reason="getting_started")

    resp = h.to_dict()
    if b1:
        resp["badge_awarded"] = b1.to_dict()
    elif b2:
        resp["badge_awarded"] = b2.to_dict()
    return jsonify(resp), 201

@app.route("/habits/<int:hid>", methods=["GET"])
def get_habit(hid):
    h = Habit.query.get_or_404(hid)
    return jsonify(h.to_dict()), 200

@app.route("/habits/<int:hid>", methods=["PUT"])
def update_habit(hid):
    h = Habit.query.get_or_404(hid)
    data = request.get_json() or {}
    if "name" in data: h.name = data.get("name") or h.name
    if "frequency" in data: h.frequency = data.get("frequency") or h.frequency
    db.session.commit()
    return jsonify(h.to_dict()), 200

@app.route("/habits/<int:hid>", methods=["DELETE"])
def delete_habit(hid):
    h = Habit.query.get_or_404(hid)
    db.session.delete(h)
    db.session.commit()
    return "", 204

@app.route("/habits/<int:hid>/complete", methods=["POST"])
def complete_habit(hid):
    """
    Mark habit done today. Streak logic:
    - if last_completed == today -> do nothing
    - if last_completed == yesterday -> streak += 1
    - else -> streak = 1
    Award streak badges at 7 and 10 days.
    """
    h = Habit.query.get_or_404(hid)
    today = date.today()
    today_iso = today.isoformat()

    if h.last_completed == today_iso:
        return jsonify(h.to_dict()), 200

    badge_awarded = None

    if h.last_completed:
        try:
            last_date = datetime.fromisoformat(h.last_completed).date()
            delta = (today - last_date).days
            if delta == 1:
                h.streak = (h.streak or 0) + 1
            else:
                h.streak = 1
        except Exception:
            h.streak = 1
    else:
        h.streak = 1

    h.last_completed = today_iso
    db.session.commit()

    # Award streak badges
    if h.streak >= 7:
        b = award_badge("7-Day Streak", emoji="🔥", description="Completed a habit 7 days in a row", reason=f"streak_{hid}_7")
        if b:
            badge_awarded = b
    if h.streak >= 10:
        b2 = award_badge("Consistency Champ", emoji="🏅", description="10+ day streak!", reason=f"streak_{hid}_10")
        if b2:
            badge_awarded = b2 or badge_awarded

    resp = h.to_dict()
    if badge_awarded:
        resp["badge_awarded"] = badge_awarded.to_dict()
    return jsonify(resp), 200

# --------------------------
# EXPENSES endpoints
# --------------------------
@app.route("/expenses", methods=["GET"])
def list_expenses():
    q = Expense.query.order_by(Expense.date.desc())
    period = request.args.get("period")
    if period:
        # simple filter by prefix like '2025-10'
        q = q.filter(Expense.date.like(f"{period}%"))
    rows = q.all()
    return jsonify([r.to_dict() for r in rows]), 200

@app.route("/expenses", methods=["POST"])
def create_expense():
    data = request.get_json() or {}
    try:
        amount = float(data.get("amount"))
    except Exception:
        return jsonify({"error":"amount required and must be numeric"}), 400
    category = data.get("category") or "misc"
    d = data.get("date") or date.today().isoformat()
    note = data.get("note")
    e = Expense(amount=amount, category=category, date=d, note=note)
    db.session.add(e)
    db.session.commit()

    # Award badge for first expense
    b = award_badge("Saver Starter", emoji="💸", description="Logged your first expense", reason="first_expense")
    b2 = award_badge("Getting Started", emoji="🚀", description="First activity in the app", reason="getting_started")
    resp = e.to_dict()
    if b:
        resp["badge_awarded"] = b.to_dict()
    elif b2:
        resp["badge_awarded"] = b2.to_dict()
    return jsonify(resp), 201

@app.route("/expenses/<int:eid>", methods=["GET"])
def get_expense(eid):
    e = Expense.query.get_or_404(eid)
    return jsonify(e.to_dict()), 200

@app.route("/expenses/<int:eid>", methods=["PUT"])
def update_expense(eid):
    e = Expense.query.get_or_404(eid)
    data = request.get_json() or {}
    if "amount" in data:
        try:
            e.amount = float(data.get("amount"))
        except:
            pass
    if "category" in data:
        e.category = data.get("category")
    if "date" in data:
        e.date = data.get("date")
    if "note" in data:
        e.note = data.get("note")
    db.session.commit()
    return jsonify(e.to_dict()), 200

@app.route("/expenses/<int:eid>", methods=["DELETE"])
def delete_expense(eid):
    e = Expense.query.get_or_404(eid)
    db.session.delete(e)
    db.session.commit()
    return "", 204

# --------------------------
# BADGES endpoints
# --------------------------
@app.route("/badges", methods=["GET"])
def get_badges():
    badges = Badge.query.order_by(Badge.date_awarded.desc()).all()
    return jsonify([b.to_dict() for b in badges]), 200

@app.route("/badges/recent", methods=["GET"])
def get_recent_badges():
    badges = Badge.query.order_by(Badge.date_awarded.desc()).limit(10).all()
    return jsonify([b.to_dict() for b in badges]), 200

# --------------------------
# Summaries (simple helpers)
# --------------------------
@app.route("/summary/habits", methods=["GET"])
def summary_habits():
    hs = Habit.query.all()
    today = date.today().isoformat()
    out = []
    for h in hs:
        due_today = (h.frequency == "daily")
        out.append({
            "id": h.id, "name": h.name, "streak": h.streak, "last_completed": h.last_completed, "due_today": due_today
        })
    return jsonify(out), 200

@app.route("/summary/expenses", methods=["GET"])
def summary_expenses():
    period = request.args.get("period")
    q = Expense.query
    if period == "month" or period is None:
        ym = date.today().strftime("%Y-%m")
        q = q.filter(Expense.date.like(f"{ym}%"))
    else:
        q = q.filter(Expense.date.like(f"{period}%"))
    rows = q.all()
    totals = {}
    for r in rows:
        totals[r.category] = totals.get(r.category, 0) + (r.amount or 0)
    return jsonify(totals), 200

# --------------------------
# Run
# --------------------------
if __name__ == "__main__":
    # debug True is convenient for development (shows tracebacks)
    app.run(debug=True, host="0.0.0.0", port=5000)
