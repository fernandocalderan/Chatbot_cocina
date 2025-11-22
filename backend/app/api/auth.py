import datetime
import jwt
from fastapi import Header, HTTPException, status, Depends, APIRouter
from pydantic import BaseModel

from app.core.config import get_settings
from app.api.deps import get_db
from app.models.users import User

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginInput(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(payload: LoginInput, db=Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.hashed_password or user.hashed_password != payload.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials")
    settings = get_settings()
    if not settings.jwt_secret:
        raise HTTPException(status_code=500, detail="jwt_secret_not_configured")
    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=settings.jwt_exp_hours)
    token = jwt.encode({"sub": str(user.id), "exp": exp}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return {"access_token": token, "token_type": "bearer"}


async def require_auth(
    authorization: str | None = Header(default=None), x_api_key: str | None = Header(default=None)
):
    settings = get_settings()
    # Si hay API token configurado, permitirlo
    if settings.panel_api_token and x_api_key == settings.panel_api_token:
        return True

    # JWT obligatorio si jwt_secret está configurado
    if settings.jwt_secret:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing_token")
        token = authorization.split()[1]
        try:
            jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token")
        return True

    # Si no hay secretos configurados, dejar pasar (modo dev)
    return True
