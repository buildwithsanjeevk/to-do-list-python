from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Todo API",
    description="A simple, fast, and feature-rich To-Do API built with FastAPI.",
    version="1.0.0",
)


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Title of the to-do item")
    description: Optional[str] = Field(None, max_length=500, description="Optional detailed description")
    completed: bool = Field(default=False, description="Whether the task is finished")
    priority: Priority = Field(default=Priority.MEDIUM, description="Priority level: low, medium, or high")


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    completed: Optional[bool] = None
    priority: Optional[Priority] = None


class TodoResponse(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime


# In-memory storage and ID counter
todos_db: dict[int, dict] = {}
id_counter: int = 1


@app.get("/", tags=["Root"])
def read_root():
    """Welcome endpoint providing basic API details and documentation link."""
    return {
        "message": "Welcome to the FastAPI Todo API!",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.post(
    "/todos/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Todos"],
    summary="Create a new To-Do item",
)
def create_todo(todo_in: TodoCreate):
    """Create a new To-Do task with title, description, priority, and completion status."""
    global id_counter
    now = datetime.now(timezone.utc)
    todo_id = id_counter
    id_counter += 1

    new_todo = {
        "id": todo_id,
        "title": todo_in.title,
        "description": todo_in.description,
        "completed": todo_in.completed,
        "priority": todo_in.priority,
        "created_at": now,
        "updated_at": now,
    }
    todos_db[todo_id] = new_todo
    return new_todo


@app.get(
    "/todos/",
    response_model=List[TodoResponse],
    tags=["Todos"],
    summary="List all To-Do items",
)
def get_todos(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search in title or description"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max number of items to return"),
):
    """Retrieve all to-do items with optional filtering, search, and pagination."""
    items = list(todos_db.values())

    if completed is not None:
        items = [item for item in items if item["completed"] == completed]

    if priority is not None:
        items = [item for item in items if item["priority"] == priority]

    if search:
        query_lower = search.lower()
        items = [
            item
            for item in items
            if query_lower in item["title"].lower()
            or (item["description"] and query_lower in item["description"].lower())
        ]

    # Apply pagination
    return items[offset : offset + limit]


@app.get(
    "/todos/{todo_id}",
    response_model=TodoResponse,
    tags=["Todos"],
    summary="Get a specific To-Do item",
)
def get_todo(todo_id: int):
    """Fetch details of a single to-do task by its ID."""
    if todo_id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found",
        )
    return todos_db[todo_id]


@app.put(
    "/todos/{todo_id}",
    response_model=TodoResponse,
    tags=["Todos"],
    summary="Replace/Full update a To-Do item",
)
def update_todo(todo_id: int, todo_in: TodoCreate):
    """Completely update an existing to-do task."""
    if todo_id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found",
        )

    now = datetime.now(timezone.utc)
    item = todos_db[todo_id]
    item["title"] = todo_in.title
    item["description"] = todo_in.description
    item["completed"] = todo_in.completed
    item["priority"] = todo_in.priority
    item["updated_at"] = now
    return item


@app.patch(
    "/todos/{todo_id}",
    response_model=TodoResponse,
    tags=["Todos"],
    summary="Partially update a To-Do item",
)
def patch_todo(todo_id: int, todo_in: TodoUpdate):
    """Update only specified fields of an existing to-do task (e.g. mark completed)."""
    if todo_id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found",
        )

    item = todos_db[todo_id]
    update_data = todo_in.model_dump(exclude_unset=True)

    if update_data:
        for field, value in update_data.items():
            item[field] = value
        item["updated_at"] = datetime.now(timezone.utc)

    return item


@app.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Todos"],
    summary="Delete a To-Do item",
)
def delete_todo(todo_id: int):
    """Delete a to-do item by its ID."""
    if todo_id not in todos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found",
        )
    del todos_db[todo_id]
    return None
