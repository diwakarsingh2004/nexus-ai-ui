
from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from pathlib import Path

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "nexus.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                technology TEXT NOT NULL DEFAULT 'Python, AI',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM workflows"
        ).fetchone()[0]

        if count == 0:
            demo_workflows = [
                (
                    "Customer Support Agent",
                    "Answer customer questions with an AI assistant.",
                    "Python, LLM, RAG"
                ),
                (
                    "Resume Analyzer",
                    "Analyze resumes and match job requirements.",
                    "Python, NLP, AI"
                ),
                (
                    "Lead Qualification Bot",
                    "Categorize leads based on customer interest.",
                    "Python, Automation"
                )
            ]

            conn.executemany("""
                INSERT INTO workflows (name, description, technology)
                VALUES (?, ?, ?)
            """, demo_workflows)


@app.route("/")
def home():
    return send_from_directory(str(BASE_DIR), "index.html")


@app.get("/api/health")
def health():
    return jsonify({
        "status": "success",
        "message": "Nexus AI backend is running"
    })


@app.get("/api/workflows")
def get_workflows():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT id, name, description, technology, created_at
            FROM workflows
            ORDER BY id DESC
        """).fetchall()

    return jsonify([dict(row) for row in rows])


@app.post("/api/workflows")
def create_workflow():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    description = data.get(
        "description",
        "New AI workflow"
    ).strip()
    technology = data.get(
        "technology",
        "Python, AI"
    ).strip()

    if not name:
        return jsonify({
            "error": "Workflow name is required"
        }), 400

    if len(name) > 100:
        return jsonify({
            "error": "Workflow name must be under 100 characters"
        }), 400

    if not description or len(description) > 500:
        return jsonify({
            "error": "Description must be between 1 and 500 characters"
        }), 400

    if len(technology) > 150:
        return jsonify({
            "error": "Technology must be under 150 characters"
        }), 400

    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO workflows (name, description, technology)
            VALUES (?, ?, ?)
        """, (name, description, technology))

        workflow_id = cursor.lastrowid

        row = conn.execute("""
            SELECT id, name, description, technology, created_at
            FROM workflows
            WHERE id = ?
        """, (workflow_id,)).fetchone()

    return jsonify(dict(row)), 201


@app.get("/api/stats")
def get_stats():
    with get_db() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM workflows"
        ).fetchone()[0]

    return jsonify({
        "total_workflows": total,
        "total_runs": 2480,
        "success_rate": 98.6,
        "avg_response_seconds": 1.2
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
