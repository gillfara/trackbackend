from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError
import jwt
from pydantic import BaseModel
from models import User
from sqlmodel import Session, select
from database import engine
from fastapi import  status, Header, HTTPException
from datetime import datetime, timedelta, timezone


SECRET = "helloworld"
ALGORITHM = "HS256"


# def get_session():
#     with Session(engine) as session:
#         yield session


class Token(BaseModel):
    token: str
    type: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password, hash):
    return pwd_context.verify(password, hash)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    with Session(engine) as session:
        # print(username)
        user = session.exec(select(User).where(User.username == username)).first()
        # print(user)
    if not user:
        return False
    return user


def authenticate_user(username: str, password: str):
    user = get_user(username)
    # print(user)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expires})
    jwt_encode = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return jwt_encode


async def get_current_user(token: str | None = Header(None)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if token:
            payload = jwt.decode(token.split(" ")[1], SECRET, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None:
                raise credential_exception
        else:
            raise credential_exception
    except InvalidTokenError:
        raise credential_exception
    user = get_user(username)
    if user is None:
        raise credential_exception
    return user
