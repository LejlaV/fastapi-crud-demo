from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List
from fastapi import HTTPException
import sqlite3

app = FastAPI()

db = sqlite3.connect("tasks.db", check_same_thread=False)
db.row_factory = sqlite3.Row
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'medium',
    created_at TEXT NOT NULL
)
""")

db.commit()

class TaskCreate(BaseModel):
    title: str
    description: str
    status: str = "pending"
    priority: str = "medium"

class TaskResponse(TaskCreate):
    id: int
    created_at: datetime

def map_row_to_task(row: sqlite3.Row) -> TaskResponse:
    return TaskResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        status=row["status"],
        priority=row["priority"],
        created_at=datetime.fromisoformat(row["created_at"])
    )

@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate) -> TaskResponse:
    """Create a new task and return it."""

    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    created_at = datetime.utcnow()

    try:
        cursor.execute(
            "INSERT INTO tasks (title, description, status, priority, created_at) VALUES (?, ?, ?, ?, ?)",
            (task.title, task.description, task.status, task.priority, created_at.isoformat())
        )
        db.commit()

        task_id = cursor.lastrowid

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()

    except Exception:
        raise HTTPException(status_code=500, detail="Database error")

    return map_row_to_task(row)


@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks() -> List[TaskResponse]:
    """Return all tasks."""

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    return [map_row_to_task(row) for row in rows]

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskCreate) -> TaskResponse:
    """Update an existing task."""

    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    try:
        cursor.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, status = ?, priority = ?
            WHERE id = ?
            """,
            (task.title, task.description, task.status, task.priority, task_id)
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")

        db.commit()

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Database error")

    return map_row_to_task(row)

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    """Delete a task by ID."""

    try:
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")

        db.commit()

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Database error")

    return None