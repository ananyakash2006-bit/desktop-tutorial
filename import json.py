# app.py
from flask import Flask, jsonify, request, send_file, abort
from pathlib import Path
import json
import datetime

DATA_FILE = Path("library_data.json")
FRONTEND_PATH = Path("/mnt/data/library-manager-fixed.html")  # <-- path to the HTML you already have

app = Flask(__name__, static_folder=None)

# -------------------------
# Data helpers (file-based)
# -------------------------
def load_data():
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {"books": [], "issued": []}

def save_data(data):
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def next_book_id(data):
    if not data["books"]:
        return 1
    return max(b["id"] for b in data["books"]) + 1

# -------------------------
# Routes: frontend
# -------------------------
@app.route("/", methods=["GET"])
def serve_frontend():
    # Serve the single-file HTML you have available locally
    if not FRONTEND_PATH.exists():
        return "<h2>Frontend file not found</h2><p>Make sure FRONTEND_PATH points to the HTML file.</p>", 404
    return send_file(str(FRONTEND_PATH))

# -------------------------
# Routes: API
# -------------------------
@app.route("/api/books", methods=["GET"])
def api_list_books():
    data = load_data()
    return jsonify(data["books"])

@app.route("/api/books", methods=["POST"])
def api_add_book():
    payload = request.get_json() or {}
    title = (payload.get("title") or "").strip()
    author = (payload.get("author") or "").strip()
    try:
        total_copies = int(payload.get("total_copies", 1))
    except (ValueError, TypeError):
        return jsonify({"error": "total_copies must be an integer"}), 400

    if not title:
        return jsonify({"error": "title required"}), 400

    data = load_data()
    book = {
        "id": next_book_id(data),
        "title": title,
        "author": author,
        "total_copies": total_copies,
        "available_copies": total_copies,
        "isbn": payload.get("isbn", ""),
        "category": payload.get("category", ""),
        "added": int(datetime.datetime.utcnow().timestamp() * 1000),
        "borrower": "",
        "due": ""
    }
    data["books"].append(book)
    save_data(data)
    return jsonify(book), 201

@app.route("/api/books/<int:book_id>", methods=["PUT"])
def api_update_book(book_id):
    payload = request.get_json() or {}
    data = load_data()
    book = next((b for b in data["books"] if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "not found"}), 404

    # update fields allowed
    for key in ("title", "author", "isbn", "category", "borrower", "due"):
        if key in payload:
            book[key] = payload[key]

    if "total_copies" in payload:
        try:
            total = int(payload["total_copies"])
        except (ValueError, TypeError):
            return jsonify({"error": "invalid total_copies"}), 400
        # adjust available_copies proportionally (simple approach)
        diff = total - book.get("total_copies", total)
        book["total_copies"] = total
        book["available_copies"] = max(0, book.get("available_copies", 0) + diff)

    if "available_copies" in payload:
        try:
            book["available_copies"] = int(payload["available_copies"])
        except (ValueError, TypeError):
            pass

    save_data(data)
    return jsonify(book)

@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def api_delete_book(book_id):
    data = load_data()
    before = len(data["books"])
    data["books"] = [b for b in data["books"] if b["id"] != book_id]
    # remove related issued records
    data["issued"] = [r for r in data["issued"] if r["book_id"] != book_id]
    save_data(data)
    return jsonify({"deleted": before - len(data["books"])})

@app.route("/api/toggle/<int:book_id>", methods=["POST"])
def api_toggle_book(book_id):
    """
    Toggle borrowed/available.
    Request JSON:
      { "action": "borrow", "borrower":"Name", "due":"YYYY-MM-DD" }
      or
      { "action": "return", "student":"Name" }
    """
    payload = request.get_json() or {}
    action = payload.get("action")
    data = load_data()
    book = next((b for b in data["books"] if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "book not found"}), 404

    if action == "borrow":
        if book["available_copies"] <= 0:
            return jsonify({"error": "no copies available"}), 400
        borrower = (payload.get("borrower") or "").strip()
        due = payload.get("due", "")
        if not borrower:
            return jsonify({"error": "borrower required"}), 400
        # record issue
        issue_record = {"book_id": book_id, "student": borrower, "due": due, "issued_at": int(datetime.datetime.utcnow().timestamp() * 1000)}
        data["issued"].append(issue_record)
        book["available_copies"] -= 1
        book["borrower"] = borrower
        book["due"] = due
        save_data(data)
        return jsonify(issue_record), 201

    elif action == "return":
        student = (payload.get("student") or "").strip()
        # find a matching issue record and remove one
        for i, rec in enumerate(data["issued"]):
            if rec["book_id"] == book_id and (not student or rec["student"].lower() == student.lower()):
                data["issued"].pop(i)
                book["available_copies"] = min(book["total_copies"], book.get("available_copies", 0) + 1)
                # if no more outstanding issues, clear borrower/due
                outstanding = any(r["book_id"] == book_id for r in data["issued"])
                if not outstanding:
                    book["borrower"] = ""
                    book["due"] = ""
                save_data(data)
                return jsonify({"returned": True})
        return jsonify({"error": "no matching issue record"}), 404

    else:
        return jsonify({"error": "invalid action"}), 400

@app.route("/api/issued", methods=["GET"])
def api_issued():
    data = load_data()
    # attach book title for convenience
    issued = []
    for rec in data["issued"]:
        book = next((b for b in data["books"] if b["id"] == rec["book_id"]), None)
        issued.append({**rec, "title": book["title"] if book else "Unknown"})
    return jsonify(issued)

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    # create data file if missing
    if not DATA_FILE.exists():
        save_data({"books": [], "issued": []})
    print("Serving frontend from:", FRONTEND_PATH)
    print("Open http://127.0.0.1:5000/ to view the GUI.")
    app.run(debug=True)
