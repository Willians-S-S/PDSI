from datetime import datetime
from fastapi import File, Form, HTTPException, status, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from http import HTTPStatus
from sqlalchemy.orm import Session
import uuid
from predpeso.models.models import UserModel, UserFarmRole
from predpeso.schemas.user_schemas import UserRequest, UserResponse, UserUpdate
from predpeso.commons.image import save_image, delete_image
from predpeso.security.password_hash import get_password_hash, verify_password
from predpeso.security.jwt_token import create_acess_token

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
    
    def update(self, user: UserUpdate, user_id: str, current_user: UserModel) -> UserResponse:

        if(current_user.id != user_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não autorizado.")

        for fild, value in user.model_dump().items():
            if value:
                print(fild, value)
                if fild == "password":
                    value = get_password_hash(value)
                setattr(current_user, fild, value)

        self.db_session.commit()
        
        return current_user

    
    def delete(self, user_id: str) -> dict:
        user_on_db = self.db_session.query(UserModel).filter_by(id = user_id).first()

        if(not user_on_db):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Usuário não encontrado.")
        
        delete_image(user_on_db.profile_picture)    

        for farm in user_on_db.farms:
            for animal in farm.animals:
                delete_image(animal.image_url)
                

        self.db_session.delete(user_on_db)
        self.db_session.commit()

        return {status.HTTP_204_NO_CONTENT: "Usuário deletado com sucesso."}

    def login(self, form_data: OAuth2PasswordRequestForm):
        user_on_db = self.db_session.query(UserModel).filter_by(username = form_data.username).first()

        if not user_on_db or not verify_password(form_data.password, user_on_db.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username ou senha incorretos.")
        
        access_token = create_acess_token(data={"sub": user_on_db.username})    

        return {"access_token": access_token, "token_type": "bearer"}
    