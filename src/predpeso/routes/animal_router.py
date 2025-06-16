from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import Optional, List

from predpeso.models.models import UserModel, AnimalModel
from predpeso.schemas.animal_schemas import AnimalRequest, AnimalResponse, AnimalUpdate
from predpeso.security.jwt_token import get_current_user
from predpeso.services.animal_service import AnimalService
from predpeso.db.connection import get_db

animal_router = APIRouter(prefix='/animal', tags=["Animals"])


def _get_animal_or_404(db: Session, animal_id: str) -> AnimalModel:
    """Busca um animal pelo ID ou levanta um erro 404."""
    animal_db = db.query(AnimalModel).filter_by(id=animal_id).first()
    if not animal_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal não encontrado.")
    return animal_db

def _authorize_user_for_farm(farm_id: str, current_user: UserModel):
    """Verifica se o usuário atual está associado à fazenda especificada."""
    if farm_id not in [farm.id for farm in current_user.farms]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso não autorizado a esta fazenda.")

def _prepare_animal_response(animal: AnimalModel) -> dict:
    """Prepara o dicionário de resposta, calculando o peso atual a partir do histórico."""
    response_data = AnimalResponse.model_validate(animal).model_dump()
    
    # Ordena o histórico do mais recente para o mais antigo
    if animal.historys:
        latest_history = sorted(animal.historys, key=lambda h: h.created_at, reverse=True)[0]
        # Pega o peso do registro mais recente, seja ele de inferência ou manual
        response_data['current_weight'] = latest_history.current_weight or latest_history.weight_manual
    else:
        response_data['current_weight'] = None
        
    return response_data

# --- ROUTES ---

@animal_router.post("/", response_model=AnimalResponse, status_code=status.HTTP_201_CREATED)
def create_animal(
    farm_id: str = Form(...),
    name: str = Form(...),
    gender: str = Form(...),
    image: UploadFile = File(...),
    breed: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    health_condition: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Cria um novo animal associado a uma fazenda, com sua primeira imagem e pesagem."""
    _authorize_user_for_farm(farm_id, current_user)
    
    # O schema AnimalRequest não é mais usado aqui, pois os dados vêm de um formulário
    animal_service = AnimalService(db_session=db)
    new_animal = animal_service.add(
        name=name, breed=breed, age=age, gender=gender,
        health_condition=health_condition, farm_id=farm_id, image=image
    )
    return _prepare_animal_response(new_animal)


@animal_router.get("/by-farm/{farm_id}", response_model=List[AnimalResponse])
def get_all_animals_from_farm(
    farm_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Lista todos os animais de uma fazenda específica."""
    _authorize_user_for_farm(farm_id, current_user)
    
    animal_service = AnimalService(db_session=db)
    animals = animal_service.get_all(farm_id=farm_id)
    
    # Prepara a resposta para cada animal na lista
    return [_prepare_animal_response(animal) for animal in animals]


@animal_router.get("/{animal_id}", response_model=AnimalResponse)
def get_animal_by_id(
    animal_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Busca um animal específico pelo seu ID."""
    animal_db = _get_animal_or_404(db, animal_id)
    _authorize_user_for_farm(animal_db.farm_id, current_user)
    
    return _prepare_animal_response(animal_db)


@animal_router.post("/{animal_id}/history/inference", response_model=AnimalResponse)
def create_inference_history(
    animal_id: str,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    # current_user: UserModel = Depends(get_current_user)
):
    """
    Cria um novo registro de histórico para um animal a partir da inferência de uma nova imagem.
    (Rota mais RESTful que o antigo PUT /inference)
    """
    animal_db = _get_animal_or_404(db, animal_id)
    # _authorize_user_for_farm(animal_db.farm_id, current_user)
    
    animal_service = AnimalService(db_session=db)
    updated_animal = animal_service.inference(animal_id=animal_id, image=image)
    return _prepare_animal_response(updated_animal)


@animal_router.put("/{animal_id}", response_model=AnimalResponse)
def update_animal(
    animal_id: str, 
    animal_update: AnimalUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Atualiza os dados de um animal. Permite também registrar um peso manual."""
    animal_db = _get_animal_or_404(db, animal_id)
    _authorize_user_for_farm(animal_db.farm_id, current_user)
    
    animal_service = AnimalService(db_session=db)
    updated_animal = animal_service.update(animal_id=animal_id, animal_update=animal_update)
    return _prepare_animal_response(updated_animal)


@animal_router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_animal(
    animal_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Deleta um animal e todo o seu histórico."""
    animal_db = _get_animal_or_404(db, animal_id)
    _authorize_user_for_farm(animal_db.farm_id, current_user)
    
    AnimalService(db_session=db).delete(animal_id=animal_id)
    
    # Uma resposta 204 NÃO DEVE ter corpo. Retornar None ou um Response vazio.
    return Response(status_code=status.HTTP_204_NO_CONTENT)