from datetime import datetime
from fastapi import HTTPException, Form, File, UploadFile
from fastapi import status
import uuid

from sqlalchemy.orm import Session

from predpeso.commons.inference import Inference
from predpeso.commons.image import save_image
# AJUSTE: O schema AnimalUpdate não estava sendo importado
from predpeso.schemas.animal_schemas import AnimalRequest, AnimalResponse, AnimalUpdate
# AJUSTE: Importar todos os modelos necessários
from predpeso.models.models import AnimalModel, FarmModel, History

ENTENY = "Animal"
# MELHORIA: Usar uma constante para o caminho das imagens é bom, 
# mas certifique-se de que o diretório existe ou crie-o na inicialização do app.
PATH_IMAGE = "/home/willians/Documentos/UFPI/PDSI/PDSI/src/predpeso/upload_image/"

class AnimalService:

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
    
    def add(self, 
            name: str,
            gender: str,
            farm_id: str,
            image: UploadFile,
            breed: str | None = None,
            age: int | None = None,
            health_condition: str | None = None
            ) -> AnimalModel: # Note: O serviço retorna o modelo, a rota formata a resposta.
        
        farm_on_db = self.db_session.query(FarmModel).filter_by(id=farm_id).first()
        if not farm_on_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Fazenda não encontrada.")
        
        animal_request_data = {
            "name": name, "breed": breed, "age": age,
            "gender": gender, "health_condition": health_condition,
            "farm_id": farm_id
        }
        animal_data = AnimalRequest(**animal_request_data)

        date_created_and_updated = datetime.now()
        image_db_filename = save_image(image)
        full_image_path = PATH_IMAGE + image_db_filename

        # PASSO 1: Tentamos obter o peso. Ele pode ser um número ou None.
        current_weight = Inference.predict_weight(full_image_path)
        
        # DEBUG: Adicione esta linha para ver o que está na variável.
        print(f"VALOR DE current_weight RECEBIDO DA INFERÊNCIA: {current_weight}")

        ### PASSO 2: PONTO CRÍTICO DE VERIFICAÇÃO ###
        # Este bloco DEVE existir exatamente aqui.
        if current_weight is None:
            # Se a inferência falhou, o programa PARA AQUI e envia um erro 400.
            # As linhas abaixo NUNCA serão executadas.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não foi possível processar a imagem. Verifique se o arquivo é válido e tente novamente."
            )

        ### PASSO 3: SE CHEGAMOS AQUI, current_weight É UM NÚMERO ###
        # Agora, e somente agora, é seguro continuar a lógica de criação.
        
        animal_on_db = AnimalModel(
            **animal_data.model_dump(), 
            id=str(uuid.uuid4()), 
            created_at=date_created_and_updated, 
            updated_at=date_created_and_updated, 
            image_url=image_db_filename
        )
        self.db_session.add(animal_on_db)

        # A chamada de round() agora é 100% segura.
        self.add_history(
            current_weight=round(current_weight, 2), 
            created_at=date_created_and_updated, 
            # image_url=image_db_filename, 
            animal_id=animal_on_db.id
        )

        farm_on_db.animal_quantity += 1

        self.db_session.commit()
        self.db_session.refresh(animal_on_db)

        return animal_on_db
    
    def get(self, animal_id: str) -> AnimalResponse:
        animal_on_db = self.db_session.query(AnimalModel).filter_by(id=animal_id).first()
        if not animal_on_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"{ENTENY} não encontrado."
            )
        return animal_on_db
    
    def get_all(self, farm_id: str) -> list[AnimalResponse]:
        # MELHORIA: É uma boa prática filtrar animais por fazenda.
        farm_on_db = self.db_session.query(FarmModel).filter_by(id=farm_id).first()
        if not farm_on_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="Fazenda não encontrada.")
        
        animals_on_db = self.db_session.query(AnimalModel).filter_by(farm_id=farm_id).all()
        return animals_on_db
    
    def inference(self, animal_id: str = Form(...), image: UploadFile = File(...)) -> AnimalResponse:
        animal_on_db = self.db_session.query(AnimalModel).filter_by(id=animal_id).first()
        if not animal_on_db:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"{ENTENY} não encontrado.")
        
        date_updated = datetime.now()
        
        # AJUSTE: Corrigido o nome da variável de image para image_db_filename
        image_db_filename = save_image(image)
        current_weight = Inference.predict_weight(PATH_IMAGE + image_db_filename)

        # AJUSTE: Atualiza a data e a imagem principal do animal. Não se mexe no peso aqui.
        animal_on_db.updated_at = date_updated
        # animal_on_db.image_url = image_db_filename

        # AJUSTE: Cria um NOVO registro no histórico com o novo peso e a nova imagem.
        self.add_history(
            current_weight=round(current_weight, 2), 
            created_at=date_updated, 
            # image_url=image_db_filename, 
            animal_id=animal_on_db.id
        )

        self.db_session.commit()
        self.db_session.refresh(animal_on_db)

        return animal_on_db
    
    def update(self, animal_id: str, animal_update: AnimalUpdate) -> AnimalResponse:
        animal_on_db = self.db_session.query(AnimalModel).filter_by(id=animal_id).first()
        if not animal_on_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"{ENTENY} não encontrado.")

        # MELHORIA: Usar model_dump com exclude_unset=True é mais idiomático e seguro.
        update_data = animal_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(animal_on_db, field, value)
        
        # MELHORIA: Sempre atualize o `updated_at` em uma operação de update.
        animal_on_db.updated_at = datetime.now()

        self.db_session.commit()
        self.db_session.refresh(animal_on_db)
        
        return animal_on_db

    def delete(self, animal_id: str) -> dict:
        animal_on_db = self.db_session.query(AnimalModel).filter_by(id=animal_id).first()
        if not animal_on_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"{ENTENY} não encontrado.")
        
        # MELHORIA: Decrementar a contagem de animais na fazenda.
        farm = self.db_session.query(FarmModel).filter_by(id=animal_on_db.farm_id).first()
        if farm:
            farm.animal_quantity -= 1

        # MELHORIA: A deleção do histórico é automática devido ao `cascade` e `ondelete="CASCADE"`.
        # A linha abaixo não é necessária e pode ser removida.
        # self.db_session.query(History).filter(History.animal_id == animal_id).delete() 
        
        self.db_session.delete(animal_on_db)
        self.db_session.commit()

        # MELHORIA: Retorno padrão para deleção bem-sucedida.
        return {"detail": f"{ENTENY} deletado com sucesso."}

    # AJUSTE: Assinatura do método corrigida para corresponder ao modelo History.
    def add_history(self, current_weight: float, created_at: datetime, animal_id: str, weight_manual: float | None = None):
        history = History(
            id=str(uuid.uuid4()), 
            current_weight=current_weight,
            weight_manual=weight_manual, 
            created_at=created_at, 
            # image_url=image_url, 
            animal_id=animal_id
        )
        self.db_session.add(history)