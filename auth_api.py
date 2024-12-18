from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from db.database import get_db
from models.auth_model import Token,RefreshTokenRequest,LogoutRequest
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from db.auth_token import (authenticate_user,
                           create_access_token,
                           create_refresh_token,
                           delete_refresh_tokens,
                           validate_refresh_token,
                           get_current_user,
                           role_required)

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 2

auth_router = APIRouter(prefix="/auth")

@auth_router.post("/login_access_token",response_model=Token)
async def login_access_token(db: Session = Depends(get_db),form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password,db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username,"role": user.role}, expires_delta=access_token_expires)
    
    refresh_token = create_refresh_token(user_id=user.id,role=user.role, expires_in_days=REFRESH_TOKEN_EXPIRE_DAYS, db=db)
    
    token= Token(access_token=access_token,token_type="bearer", refresh_token=refresh_token.token)
    response = JSONResponse(content=token.dict(), status_code=status.HTTP_200_OK)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token.token, httponly=True)
    return response

@auth_router.post("/refresh_token", response_model=Token)
async def refresh_token(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        validated_token = validate_refresh_token(token=body.refresh_token, db=db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": validated_token.user_id}, expires_delta=access_token_expires)
    
    token = Token(access_token=access_token, token_type="bearer", refresh_token=body.refresh_token)
    response = JSONResponse(content=token.dict(), status_code=status.HTTP_200_OK)

    return response
    
@auth_router.post("/logout")
async def logout(body:LogoutRequest, db: Session = Depends(get_db)):
    
    delete_refresh_tokens(user_id=body.user_id,db=db)
    
    response = JSONResponse(content={"message": "Logout successful"}, status_code=status.HTTP_200_OK)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@auth_router.get("/dummy_function")
async def dummy_function(current_user: int = Depends(get_current_user)):
    return {"message": "You have access", "user_name": current_user}

@auth_router.get("/admin_only")
def admin_only(user_data: dict = Depends(role_required("admin"))):
    return {"message": "Welcome, Admin!"}

@auth_router.get("/user_only")
def user_only(user_data: dict = Depends(role_required("user"))):
    return {"message": "Welcome, User!"}
