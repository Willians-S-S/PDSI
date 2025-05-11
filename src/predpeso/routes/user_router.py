from fastapi import APIRouter, Depends, Form, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from predpeso.db.connection import get_db
from predpeso.models.models import UserModel
from predpeso.schemas.user_schemas import UserRequest, UserResponse, UserUpdate
from predpeso.services.user_service import UserService



user_router = APIRouter(prefix='/user')

@user_router.post("/", response_model=UserResponse)
def creat_user(name: str = Form(...), 
               username: str = Form(...), 
               email: str = Form(...), 
               password: str = Form(...), 
               cpf: str = Form(...), 
               role: str = Form(...), 
               image: UploadFile = File(...), 
               db: Session = Depends(get_db) ):
    
    return UserService(db_session=db).add(name=name, 
                                          username=username, 
                                          email=email, 
                                          password=password, 
                                          cpf=cpf,
                                          role=role,
                                          image=image)