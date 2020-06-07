from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import os
from dog_breed_classifier import DogBreedPrediction
from utility import download_blob

# keep model as global variable so we don't have to reload
# it in case of warm invocations
model = None

app = FastAPI()


@app.get('/healthcheck')
def read_healthcheck():
    return 'healthy'


@app.post('/classify-dog-breeds')
def classify_dog_breeds(img_path: str):
    global model
    BUCKET_NAME = os.getenv('BUCKET_NAME', 'dog-breed-classifier')
    SOURCE_BLOB_NAME = os.getenv('SOURCE_BLOB_NAME', 'model_transfer.pt')
    DESTINATION_FILE_NAME = f'/tmp/{SOURCE_BLOB_NAME}'

    if model is None:
        download_blob(BUCKET_NAME, SOURCE_BLOB_NAME, DESTINATION_FILE_NAME)
        model = DogBreedPrediction(DESTINATION_FILE_NAME)

    '''
    # testing
    download_blob(BUCKET_NAME, 'testing/Brittany_02625.jpg',
                  'tmp/Brittany_02625.jpg')
    download_blob(BUCKET_NAME, 'testing/sky.jpeg', 'tmp/sky.jpeg')

    return model.predict('tmp/Brittany_02625.jpg')
    '''
