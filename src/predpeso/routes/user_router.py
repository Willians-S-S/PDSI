from fastapi import APIRouter, Depends, Form, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from predpeso.db.connection import get_db
from predpeso.models.models import UserModel, UserFarmRole
from predpeso.schemas.user_schemas import UserRequest, UserResponse, UserUpdate
from predpeso.services.user_service import UserService
from predpeso.schemas.token_schemas import Token
from predpeso.security.jwt_token import get_current_user



user_router = APIRouter(prefix='/user')

@user_router.post("/", response_model=UserResponse)
def creat_user(name: str = Form(...), 
               username: str = Form(...), 
               email: str = Form(...), 
               password: str = Form(...), 
               cpf: str = Form(...), 
               role: UserFarmRole = Form(...), 
               image: UploadFile = File(...), 
               db: Session = Depends(get_db) ):
    
    return UserService(db_session=db).add(name=name, 
                                          username=username, 
                                          email=email, 
                                          password=password, 
                                          cpf=cpf,
                                          role=role,
                                          image=image)

def get_all(db: Session = Depends(get_db)):
    return UserService(db_session=db).get_all()

@user_router.put("/{id_user}", response_model=UserResponse)
def upadate_user(user: UserUpdate, 
                 id_user: str, 
                 db: Session = Depends(get_db),
                 current_user: UserModel = Depends(get_current_user)):
    return UserService(db_session=db).update(user=user, user_id=id_user, current_user=current_user)

@user_router.delete("/", status_code=204)
def delete( db: Session = Depends(get_db),
           current_user=Depends(get_current_user)):
    return UserService(db_session=db).delete(user_id=current_user.id)

@user_router.post("/token", response_model=Token,)
def longin_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return UserService(db_session=db).login(form_data=form_data)