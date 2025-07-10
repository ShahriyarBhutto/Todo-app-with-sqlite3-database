from typing import Annotated
from fastapi import Depends, FastAPI, Path, HTTPException
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

# show all todos:

@app.get("/")
async def all_todos(db: db_dependency):
    return db.query(Todos).all()


# Find Todo by Id:

@app.get("/todos/{todo_id}")
async def get_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo_model
