from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import List

from core.security import SECRET_KEY, ALGORITHM
from models.schemas import TokenData

# This URL must match your login route (from Step 4)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Extracts and verifies the JWT token from the request header."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None or role is None:
            raise credentials_exception
            
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception
        
    return token_data

class RoleChecker:
    """
    Dependency class to check if the current user has the required role.
    Usage: Depends(RoleChecker(["ADMIN", "DOCTOR"]))
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Your role is {current_user.role}."
            )
        return current_user