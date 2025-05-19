from datetime import datetime
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session
import uuid

from predpeso.commons.image import delete_image
from predpeso.models.models import FarmModel, UserModel, UserFarmAssociation
from predpeso.schemas.farm_schemas import FarmRequest, FarmResponse, FarmUpdate

class FarmService:

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
    
    def add(self, farm: FarmRequest) -> FarmResponse:

        user_on_db = self.db_session.query(UserModel).filter_by(id = farm.user_id).first()

        if not user_on_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Usuário não encontrado.")
        
        date_created_and_updated = datetime.now()

        farm_data = farm.model_dump()
        farm_data.pop("user_id", None) 
        farm_on_db = FarmModel(**farm_data, id=str(uuid.uuid4()), created_at=date_created_and_updated, updated_at=date_created_and_updated)

        self.db_session.add(farm_on_db)
        self.db_session.commit()

        associantion = UserFarmAssociation(user_id=user_on_db.id, farm_id=farm_on_db.id)
        self.db_session.add(associantion)
        self.db_session.commit()

        return farm_on_db
    
    def get(self, farm_id: str) -> FarmResponse:
        farm_on_db = self.db_session.query(FarmModel).filter_by(id = farm_id).first()

        if(not farm_on_db):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Fazenda não encontrado."
                )
        
        return farm_on_db
    
    def get_all(self) -> list[FarmResponse]:
        farms_on_db = self.db_session.query(FarmModel).all()

        return farms_on_db
    
    def update(self, farm: FarmUpdate, farm_id: str, current_user: UserModel):

        is_user_farm_owner = self.db_session.query(FarmModel).filter_by(id = farm_id, user_id = current_user.id).first()

        if not is_user_farm_owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Fazenda não encontrado.")

        for fild, value in farm.model_dump().items():
            if value:
                print(fild, value)
                setattr(is_user_farm_owner, fild, value)

        self.db_session.commit()
        
        return is_user_farm_owner

    
    def delete(self, farm_id: str) -> dict:
        farm_on_db = self.db_session.query(FarmModel).filter_by(id = farm_id).first()

        if(not farm_on_db):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Fazenda não encontrado.")
        
        for animal in farm_on_db.animals:
            delete_image(animal.image_url)

        self.db_session.delete(farm_on_db)
        self.db_session.commit()

        return {status.HTTP_204_NO_CONTENT: "Fazenda deletado com sucesso."}

        
    