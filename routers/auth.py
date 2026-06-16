from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.schemas import Token, UserInDB
from core.security import verify_password, create_access_token
from database import pool
import oracledb

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_user_from_db(username: str):
    """Fetch user from the database by username."""
    with pool.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT user_id, username, hashed_password, role, is_active, created_at FROM users WHERE username = :1",
                [username]
            )
            row = cursor.fetchone()
            if row:
                return UserInDB(
                    user_id=row[0],
                    username=row[1],
                    hashed_password=row[2],
                    role=row[3],
                    is_active=bool(row[4]),
                    created_at=row[5]
                )
    return None

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # 1. Fetch user from DB
    user = get_user_from_db(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Verify Password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Create JWT Token (include role inside it)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}