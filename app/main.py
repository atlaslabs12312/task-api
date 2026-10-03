import os
from datetime import datetime, timezone
from typing import Generator

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, Integer, String, create_engine, select
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


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task API",
    version="1.1.0",
    description="Production-style REST API built with Python and FastAPI.",
)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class Task(TaskCreate):
    id: int
    completed: bool = False
    model_config = {"from_attributes": True}


class AuditLogResponse(BaseModel):
    id: int
    action: str
    resource: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_role(
    x_role: str = Header(default="viewer", alias="X-Role"),
) -> str:
    allowed_roles = {"viewer", "editor", "admin"}
    if x_role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Invalid role")
    return x_role


def require_editor(role: str = Depends(require_role)) -> str:
    if role not in {"editor", "admin"}:
        raise HTTPException(status_code=403, detail="Editor role required")
    return role


def write_audit_log(
    db: Session,
    *,
    action: str,
    resource: str,
    role: str,
) -> None:
    db.add(AuditLog(action=action, resource=resource, role=role))
    db.commit()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    role: str = Depends(require_editor),
):
    task = TaskModel(title=payload.title, completed=False)
    db.add(task)
    db.commit()
    db.refresh(task)
    write_audit_log(db, action="create", resource=f"task:{task.id}", role=role)
    return task


@app.get("/tasks", response_model=list[Task])
def list_tasks(
    q: str | None = Query(default=None, min_length=1, max_length=200),
    db: Session = Depends(get_db),
    role: str = Depends(require_role),
):
    statement = select(TaskModel).order_by(TaskModel.id)
    if q:
        statement = statement.where(TaskModel.title.ilike(f"%{q}%"))
    tasks = list(db.scalars(statement).all())
    write_audit_log(db, action="list", resource="tasks", role=role)
    return tasks


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    role: str = Depends(require_role),
):
    task = db.get(TaskModel, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    write_audit_log(db, action="read", resource=f"task:{task_id}", role=role)
    return task


@app.patch("/tasks/{task_id}/complete", response_model=Task)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    role: str = Depends(require_editor),
):
    task = db.get(TaskModel, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.completed = True
    db.commit()
    db.refresh(task)
    write_audit_log(db, action="complete", resource=f"task:{task_id}", role=role)
    return task


@app.get("/audit-logs", response_model=list[AuditLogResponse])
def list_audit_logs(
    db: Session = Depends(get_db),
    role: str = Depends(require_role),
):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return list(db.scalars(select(AuditLog).order_by(AuditLog.id)).all())
