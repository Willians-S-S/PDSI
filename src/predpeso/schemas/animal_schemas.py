from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

# Certifique-se de que o schema HistoryResponse está definido corretamente.
# Exemplo de como ele deveria ser:
class HistoryResponse(BaseModel):
    id: str
    current_weight: Optional[float] = None
    weight_manual: Optional[float] = None
    # image_url: Optional[str] = None
    created_at: datetime

    # Configuração para permitir que o Pydantic leia a partir de atributos de objetos (ORM)
    model_config = ConfigDict(from_attributes=True)


# --- Schemas do Animal ---

class AnimalRequest(BaseModel):
    """
    Schema para criar um novo animal.
    O nome, gênero e ID da fazenda são obrigatórios.
    """
    name: str
    gender: str
    farm_id: str 
    breed: Optional[str] = None
    age: Optional[int] = None
    health_condition: Optional[str] = None


class AnimalResponse(BaseModel):
    """
    Schema para a resposta da API ao consultar um animal.
    Inclui os dados do animal e seu histórico completo de pesagens.
    """
    id: str
    name: str
    breed: Optional[str] = None
    age: Optional[int] = None
    gender: str
    image_url: Optional[str] = None # Imagem mais recente do animal
    health_condition: Optional[str] = None
    
    # Este campo é derivado: será o peso do último registro no histórico.
    # Pode ser None se o animal ainda não tiver histórico.
    current_weight: Optional[float] = None 
    
    created_at: datetime
    updated_at: datetime
    farm_id: str 
    
    # Relação: um animal tem uma lista de históricos
    historys: list[HistoryResponse] = []

    # Configuração para permitir que o Pydantic leia a partir de atributos de objetos (ORM)
    model_config = ConfigDict(from_attributes=True)


class AnimalUpdate(BaseModel):
    """
    Schema para atualizar um animal existente.
    Todos os campos são opcionais.
    O usuário não deve poder alterar IDs ou timestamps diretamente.
    """
    name: Optional[str] = None
    breed: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    health_condition: Optional[str] = None

    # Adicionamos este campo para permitir um registro manual de peso.
    # O serviço irá criar um novo registro no History com este valor.
    weight_manual: Optional[float] = None