from datetime import datetime
from fastapi import File, Form, HTTPException, status, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from http import HTTPStatus
from sqlalchemy.orm import Session
import uuid
from predpeso.models.models import UserModel, UserFarmRole
from predpeso.schemas.user_schemas import UserRequest, UserResponse, UserUpdate

class UserService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        
    def add(self,
            name: str = Form(...),
            username: str = Form(...),
            email: str = Form(...),
            password: str = Form(...),
            cpf: str = Form(...),
            role: str = Form(...),  # Recebe como string
            image: UploadFile = File(...)
            ) -> UserResponse:
    
    
            
        user = {
            "name": name,
            "username": username,
            "email": email,
            "password": password,
            "cpf": cpf,
        }
        
        user = UserRequest(**user)
        role_enum = UserFarmRole(role)
        user.role = role_enum
        
        print(user)
        
        user_on_db = self.db_session.query(UserModel)\
            .filter(UserModel.email == user.email)\
            .first()
            
        if user_on_db:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já foi cadastrado."
            )
        
        user_on_db = self.db_session.query(UserModel)\
            .filter(UserModel.cpf == user.cpf)\
            .first()
            
        if user_on_db:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CPF já foi cadastrado."
            )
            
        date_created_and_updated = datetime.now()
        # user.profile_picture = save_image(image)
        
        user_on_db = UserModel(
            **user.model_dump(),
            id=str(uuid.uuid4()),
            created_at=date_created_and_updated,
            updated_at=date_created_and_updated
        )
        
        self.db_session.add(user_on_db)
        self.db_session.commit()
        
        return user_on_db
    
    def get(self, user_id: str) -> UserResponse:
        user_on_db = self.db_session.query(UserModel).filter_by(id = user_id).first()

        if(not user_on_db):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Usuário não encontrado."
                )
        
        return user_on_db
    
    def get_all(self) -> list[UserResponse]:
        users_on_db = self.db_session.query(UserModel).all()

        return users_on_db