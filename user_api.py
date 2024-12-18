from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from models.user_model import UserCreate, UserUpdate, UserDelete, UserGet
from db.crud import get_all_users_from_db,get_user_by_id_from_db,create_user_from_db,update_user_from_db,delete_user_from_db
from db.database import get_db


user_router = APIRouter(prefix="/users")


@user_router.get("/get_all/", response_model=list[UserGet])
def get_all_users(db: Session = Depends(get_db)):
    users = get_all_users_from_db(db=db)
    return users

@user_router.get("/get_user_id/{user_id}", response_model=UserGet)
def get_user_by_id(user_id: int,db : Session = Depends(get_db)):
    user = get_user_by_id_from_db(user_id=user_id,db=db)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


@user_router.post("/create_user/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    created_user = create_user_from_db(user=user,db=db)
    return created_user

@user_router.put("/update_user/{user_id}")
def update_user_by_email(user_id: int, user:UserUpdate, db: Session = Depends(get_db)):
    updated_user = update_user_from_db(user_id=user_id, user=user, db=db)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}

@user_router.delete("/delete_user/{user_id}")
def delete_user(user_id:int,user: UserDelete, db: Session = Depends(get_db)):
    deleted_user = delete_user_from_db(user_id=user_id, user=user, db=db)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}