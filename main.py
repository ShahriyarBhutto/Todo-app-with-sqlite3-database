from typing import Annotated
from fastapi import Depends, FastAPI, Path, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import models
from models import Todos
from database import SessionLocal, engine


app = FastAPI()


models.Base.metadata.create_all(bind = engine)

def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=3, max_length=200)
    complete: bool
    priority: int = Field(gt=0, lt=6)

# show all todos:

@app.get("/" ,status_code= status.HTTP_200_OK)
async def all_todos(db: db_dependency):
    return db.query(Todos).all()


# Find Todo by Id:

@app.get("/todos/{todo_id}",status_code=status.HTTP_200_OK)
async def get_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo_model

# Post A Todo:

@app.post("/todos", status_code= status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()


# Update a Todo:

@app.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update(db:db_dependency, todo_request: TodoRequest, todo_id: int):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="No todo found")
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.complete = todo_request.complete
    todo_model.priority = todo_request.priority
    db.add(todo_model)
    db.commit()
