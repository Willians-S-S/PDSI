from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

image_router = APIRouter(prefix= "/images")

IMAGES_DIR = "/home/willians/Documentos/UFPI/PDSI/PDSI/src/predpeso/upload_image"

@image_router.get("/{image_name}")
def get_image(image_name: str):
    image_path = os.path.join(IMAGES_DIR, image_name)
    if os.path.exists(image_path):
        return FileResponse(image_path)
    raise HTTPException(status_code=404, detail="Imagem não encontrada")

