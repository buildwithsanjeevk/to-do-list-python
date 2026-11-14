# Simple To-Do API with FastAPI

A clean, modern, and fully-featured RESTful To-Do API built using **FastAPI** and **Pydantic v2**.

---

## Features

- **Full CRUD Operations**: Create, read, update (full and partial), and delete tasks.
- **Filtering & Search**: Filter by completion status (`completed`), `priority` (`low`, `medium`, `high`), or keyword search in title and description.
- **Pagination**: Supports `limit` and `offset` query parameters.
- **Automatic Interactive Docs**: Swagger UI (`/docs`) and ReDoc (`/redoc`) generated out of the box.
- **Data Validation & Schemas**: Enforced with Pydantic models.
- **Unit Tested**: Full test coverage with `pytest` and `httpx`.

---

## Project Structure

```text
.
├── main.py            # FastAPI application & route definitions
├── test_main.py       # Automated test suite using pytest & TestClient
├── pyproject.toml     # Project metadata and dependencies
├── uv.lock            # Locked dependency versions
└── README.md          # Documentation & usage instructions
```

---

## Getting Started

Run the following commands from the `To-Do/` directory (use `cd To-Do` first if you are in the workspace root).

### 1. Install dependencies

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if it is not already installed, then sync the project dependencies:

```bash
uv sync
```

This creates a `.venv` virtual environment and installs the locked dependencies, including the development dependencies used for testing.

### 2. Run the Development Server

Start the API with Uvicorn:

```bash
uv run uvicorn main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

### 3. Interactive API Documentation

FastAPI provides interactive documentation:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Root welcome endpoint |
| `POST` | `/todos/` | Create a new to-do task |
| `GET` | `/todos/` | List all tasks (with optional filter, search, & pagination) |
| `GET` | `/todos/{todo_id}` | Retrieve details for a single task |
| `PUT` | `/todos/{todo_id}` | Full update / replace a task |
| `PATCH` | `/todos/{todo_id}` | Partial update of a task (e.g. mark done) |
| `DELETE` | `/todos/{todo_id}` | Delete a task |

---

## Example Usage with cURL

### Create a To-Do:
```bash
curl -X POST "http://127.0.0.1:8000/todos/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, and bread",
    "priority": "high"
  }'
```

### List all To-Dos:
```bash
curl -X GET "http://127.0.0.1:8000/todos/"
```

### Filter To-Dos by Priority:
```bash
curl -X GET "http://127.0.0.1:8000/todos/?priority=high"
```

### Mark a Task as Completed (PATCH):
```bash
curl -X PATCH "http://127.0.0.1:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Delete a Task:
```bash
curl -X DELETE "http://127.0.0.1:8000/todos/1"
```

---

## Running the Tests

To run the automated test suite:

```bash
uv run pytest -v
```
