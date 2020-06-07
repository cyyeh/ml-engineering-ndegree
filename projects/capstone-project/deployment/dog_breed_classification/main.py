import re
import os
import base64
from io import BytesIO

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google.cloud import logging

from dog_breed_classifier import DogBreedPrediction
from utility import download_blob

logging_client = logging.Client()
logger = logging_client.logger("dog-breed-classifier")

# keep model as global variable so we don't have to reload
# it in case of warm invocations
model = None

app = FastAPI()


class ImageData(BaseModel):
    base64: str


@app.get('/healthcheck')
def read_healthcheck():
    return 'healthy'


@app.post('/classify-dog-breeds')
def classify_dog_breeds(img_data: ImageData):
    global model
    BUCKET_NAME = os.getenv('BUCKET_NAME', 'dog-breed-classifier')
    SOURCE_BLOB_NAME = os.getenv('SOURCE_BLOB_NAME', 'model_transfer.pt')
    DESTINATION_FILE_NAME = f'/tmp/{SOURCE_BLOB_NAME}'

    if model is None:
        logger.log_text(f'Initial startup, model content: {model}')
        download_blob(BUCKET_NAME, SOURCE_BLOB_NAME, DESTINATION_FILE_NAME)
        model = DogBreedPrediction(DESTINATION_FILE_NAME)

    # check input data is really an image
    BASE64_IMAGE_PATTERN = '^data:image/.+;base64,'
    if re.match(BASE64_IMAGE_PATTERN, img_data.base64):
        img_data = re.sub(BASE64_IMAGE_PATTERN, '', img_data.base64)
        img_path = BytesIO(base64.b64decode(img_data))
        return model.predict(img_path)
    else:
        return {
            'dog_detected': False,
            'message': 'No image file found, please check again.'
        }
