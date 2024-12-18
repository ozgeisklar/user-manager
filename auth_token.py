from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta,timezone
from typing import Optional
from db.database import get_db
from db.schemas import User,RefreshToken
from db.enums import RoleType
from enum import Enum



SECRET_KEY = "8c1e861c388b4f16cf33624a734f7624e578d7d2a6f8cb2cc4252e569cf50704"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login_access_token")



def get_user_by_username(db:Session, username: str):
    return db.query(User).filter(User.username== username).first()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_encrypted(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str,db: Session):
    user = get_user_by_username(db=db,username=username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if "role" in to_encode and isinstance(to_encode["role"], Enum):
        to_encode["role"] = to_encode["role"].value  # Enum'u string'e dönüştür
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: int,role:RoleType, expires_in_days: int, db: Session) -> RefreshToken:
    to_encode = {
        "sub": user_id,
        "role": role.value,
        "exp": datetime.utcnow() + timedelta(days=expires_in_days)
    }
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    refresh_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
        created_at=datetime.utcnow()
    )

    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token

def delete_refresh_tokens(user_id:int, db: Session):
    tokens_deleted = db.query(RefreshToken).filter_by(user_id=user_id).delete()
    db.commit()

    if tokens_deleted == 0:
        raise ValueError("No token for this user")
    
def validate_refresh_token(token: str, db: Session) -> RefreshToken:
    refresh_token = db.query(RefreshToken).filter_by(token=token).first()

    if not refresh_token:
        raise ValueError("Invalid refresh token")
 
    if refresh_token.expires_at < datetime.utcnow().replace(tzinfo=timezone.utc):
        raise ValueError("Refresh token expired")

    return refresh_token

# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"username": username, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def role_required(required_role: str):
    def check_role(user_data: dict = Depends(get_current_user)):
        if user_data["role"] != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return user_data
    return check_role