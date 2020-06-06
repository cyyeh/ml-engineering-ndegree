import os
from google.cloud import storage
from dog_breed_classifier import DogBreedPrediction

# keep model as global variable so we don't have to reload
# it in case of warm invocations
model = None

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket"""
    storage_client = storage.Client()
    bucket =  storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    
    blob.download_to_filename(destination_file_name)
    
    print(f'Blob {source_blob_name} is downloaded to {destination_file_name}.')
    
# cloud function entry point
def handler(request):
    global model
    BUCKET_NAME = os.getenv('BUCKET_NAME', 'dog-breed-classifier')
    SOURCE_BLOB_NAME = os.getenv('SOURCE_BLOB_NAME', 'model_transfer.pt')
    DESTINATION_FILE_NAME = f'/tmp/{SOURCE_BLOB_NAME}'
    
    if model is None:
        download_blob(BUCKET_NAME, SOURCE_BLOB_NAME, DESTINATION_FILE_NAME)
        model = DogBreedPrediction(DESTINATION_FILE_NAME)
        
    # testing
    download_blob(BUCKET_NAME, 'testing/Brittany_02625.jpg', 'tmp/Brittany_02625.jpg')
    print(model.predict('tmp/Brittany_02625.jpg'))
    print()
    download_blob(BUCKET_NAME, 'testing/sky.jpeg', 'tmp/sky.jpeg')
    print(model.predict('tmp/sky.jpeg'))
    
    return 'Testing'