from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class HistoryResponse(BaseModel):
    """
    Schema para a resposta da API ao consultar um registro de histórico.
    Reflete exatamente os campos do modelo History do SQLAlchemy.
    """
    id: str
    created_at: datetime

    # Estes campos correspondem diretamente às colunas no modelo History.
    # São opcionais porque a coluna no banco de dados é nullable=True.
    current_weight: Optional[float] = None
    weight_manual: Optional[float] = None

    # AJUSTE: O campo 'image_url' foi REMOVIDO daqui.
    # MOTIVO: O modelo History do SQLAlchemy fornecido não possui este campo.
    # Manter este campo aqui causaria um erro na conversão do objeto.
    # image_url: Optional[str] = None

    # Esta configuração é essencial para a conversão de ORM -> Pydantic.
    model_config = ConfigDict(from_attributes=True)