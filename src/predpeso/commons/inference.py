import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense
from tensorflow.keras.applications import InceptionResNetV2

# Caminho do arquivo de pesos do modelo treinado
WEIGHTS_PATH = "/home/will/Documentos/Projetos/predpeso-python/predpeso/src/predpeso/h5/ImgOriginalV1Fold_0.h5"

# Variável global para armazenar o modelo carregado
MODEL = None

class Inference:
    """
    Classe para realizar inferência de peso a partir de imagens.
    """

    @staticmethod
    def preprocess_image(image_path, target_size=(256, 256)):
        """ Carrega e pré-processa uma imagem para inferência. """
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise FileNotFoundError(f"Não foi possível carregar a imagem: {image_path}")

            img = cv2.resize(img, target_size)
            img = img.reshape(1, *target_size, 3)  # Adiciona dimensão do lote
            img = img / 255.0  # Normaliza os pixels
            return img

        except Exception as e:
            print(f"Erro ao pré-processar a imagem: {e}")
            return None

    @staticmethod
    def build_model(input_shape=(256, 256, 3)):
        """ Constrói o modelo apenas uma vez e reutiliza. """
        global MODEL
        if MODEL is None:
            print("Carregando modelo pela primeira vez...")
            modelo_base = InceptionResNetV2(
                weights='imagenet',
                include_top=False,
                input_shape=input_shape
            )

            MODEL = Sequential([
                modelo_base,
                GlobalAveragePooling2D(),
                Dense(1, activation='linear')
            ])
            
            # Carregar os pesos treinados
            MODEL.load_weights(WEIGHTS_PATH)
            print("Modelo carregado e pronto para predição!")

        return MODEL

    @staticmethod
    def predict_weight(image_path):
        """ Faz a predição do peso a partir de uma imagem. """
        try:
            model = Inference.build_model()  # Reutiliza o modelo carregado

            # Pré-processar a imagem
            input_image = Inference.preprocess_image(image_path)
            if input_image is None:
                print("Erro ao pré-processar a imagem.")
                return None

            # Fazer a predição
            predicted_weight = model.predict(input_image)[0][0]
            return predicted_weight

        except Exception as e:
            print(f"Erro durante a predição: {e}")
            return None

