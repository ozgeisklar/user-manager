from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.user_model import UserCreate, UserUpdate, UserDelete
from db.schemas import User
from db.auth_token import get_password_encrypted


def get_all_users_from_db(db: Session):
    users = db.query(User).all()
    return users

def get_user_by_id_from_db(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    return user

def create_user_from_db(user: UserCreate, db: Session):
    db_user = User(name=user.name, surname=user.surname, username=user.username, email=user.email, password=get_password_encrypted(user.password),role = user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_from_db(user_id: int, user: UserUpdate, db: Session):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.name is not None:
        db_user.name = user.name
    if user.surname is not None:
        db_user.surname = user.surname
    if user.username is not None:
        db_user.username = user.username
    if user.email is not None:
        db_user.email = user.email
    if user.password is not None:
        db_user.password = user.password
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user_from_db(user_id:int,user: UserDelete, db: Session):
    db_user = db.query(User).filter(User.id == user_id).first() 
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.refresh(db_user)
    db.commit()

    return db_user

