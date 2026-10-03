import os
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class TaskModel(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task API", version="1.0.0", description="Production-style REST API built with Python and FastAPI.")

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

class Task(TaskCreate):
    id: int
    completed: bool = False
    model_config = {"from_attributes": True}

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = TaskModel(title=payload.title, completed=False)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.get("/tasks", response_model=list[Task])
def list_tasks(db: Session = Depends(get_db)):
    return list(db.scalars(select(TaskModel).order_by(TaskModel.id)).all())

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(TaskModel, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.patch("/tasks/{task_id}/complete", response_model=Task)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(TaskModel, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.completed = True
    db.commit()
    db.refresh(task)
    return task
