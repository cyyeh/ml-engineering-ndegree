gcloud functions deploy classify-dog-breeds --allow-unauthenticated --entry-point=handler --memory=2048MB --runtime=python37 --source=gs://dog-breed-classifier/project.zip --trigger-http
