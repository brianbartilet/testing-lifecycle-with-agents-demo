"""
Todo API - Example application backend.

Simple CRUD REST API for a Todo application.
Used as the target application for the AI-driven testing lifecycle.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime

app = FastAPI(
    title="Todo API",
    description="Simple Todo REST API for testing lifecycle demonstration",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
_todos: dict = {}


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Todo title")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    completed: bool = Field(False, description="Completion status")


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None


class Todo(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: str
    updated_at: str


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "service": "todo-api"}


@app.get("/todos", response_model=List[Todo], tags=["todos"])
def list_todos(completed: Optional[bool] = None):
    """List all todos, optionally filtered by completion status."""
    items = list(_todos.values())
    if completed is not None:
        items = [t for t in items if t["completed"] == completed]
    return items


@app.post("/todos", response_model=Todo, status_code=201, tags=["todos"])
def create_todo(payload: TodoCreate):
    """Create a new todo item."""
    todo_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    todo = {
        "id": todo_id,
        "title": payload.title,
        "description": payload.description,
        "completed": payload.completed,
        "created_at": now,
        "updated_at": now,
    }
    _todos[todo_id] = todo
    return todo


@app.get("/todos/{todo_id}", response_model=Todo, tags=["todos"])
def get_todo(todo_id: str):
    """Get a single todo by ID."""
    if todo_id not in _todos:
        raise HTTPException(status_code=404, detail=f"Todo '{todo_id}' not found")
    return _todos[todo_id]


@app.put("/todos/{todo_id}", response_model=Todo, tags=["todos"])
def update_todo(todo_id: str, payload: TodoUpdate):
    """Update an existing todo."""
    if todo_id not in _todos:
        raise HTTPException(status_code=404, detail=f"Todo '{todo_id}' not found")
    todo = _todos[todo_id]
    if payload.title is not None:
        todo["title"] = payload.title
    if payload.description is not None:
        todo["description"] = payload.description
    if payload.completed is not None:
        todo["completed"] = payload.completed
    todo["updated_at"] = datetime.utcnow().isoformat()
    _todos[todo_id] = todo
    return todo


@app.delete("/todos/{todo_id}", status_code=204, tags=["todos"])
def delete_todo(todo_id: str):
    """Delete a todo by ID."""
    if todo_id not in _todos:
        raise HTTPException(status_code=404, detail=f"Todo '{todo_id}' not found")
    del _todos[todo_id]
