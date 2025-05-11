from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from http import HTTPStatus
from jwt import decode, encode
from jwt.exceptions import PyJWTError 
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

from predpeso.db.connection import get_db
from predpeso.models.models import UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


SECRET_KEY = "senhaPorEnquanto"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_acess_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({'exp':expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')

        if not username:
            raise credentials_exception
        
    except PyJWTError:
        raise credentials_exception
    
    user_on_db = db.query(UserModel).filter_by(username=username).first()
    
    if not user_on_db:
            raise credentials_exception

    return user_on_db
    
    
