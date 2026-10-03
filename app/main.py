from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Task API",
    version="1.0.0",
    description="Simple REST API built with Python and FastAPI.",
)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class Task(TaskCreate):
    id: int
    completed: bool = False


tasks = {}
next_id = 1


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(payload: TaskCreate):
    global next_id

    task = Task(
        id=next_id,
        title=payload.title,
    )

    tasks[next_id] = task
    next_id += 1

    return task


@app.get("/tasks", response_model=list[Task])
def list_tasks():
    return list(tasks.values())


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = tasks.get(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@app.patch("/tasks/{task_id}/complete", response_model=Task)
def complete_task(task_id: int):
    task = tasks.get(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    task.completed = True
    return task
