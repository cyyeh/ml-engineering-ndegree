LOCAL_PORT = 5000
DOCKER_PORT = 8080
PROJECT_ID = deep-learning-279406
IMAGE_NAME = dog-breed-classifier
GOOGLE_APPLICATION_CREDENTIALS = /Users/cyyeh/deep-learning-5cfd37943c26.json

dev:
	docker run -p $(LOCAL_PORT):$(DOCKER_PORT) -e PORT=$(DOCKER_PORT) -e GOOGLE_APPLICATION_CREDENTIALS=$(GOOGLE_APPLICATION_CREDENTIALS) -v $$GOOGLE_APPLICATION_CREDENTIALS:$(GOOGLE_APPLICATION_CREDENTIALS):ro gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)
build:
	gcloud builds submit --tag gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)
deploy:
	gcloud run deploy --image gcr.io/$(PROJECT_ID)/$(IMAGE_NAME) --platform managed