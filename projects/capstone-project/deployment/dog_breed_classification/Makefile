LOCAL_PORT = 5000
DOCKER_PORT = 8080
PROJECT_ID = deep-learning-279406
IMAGE_NAME = dog-breed-classifier
GCR_HOST = asia.gcr.io
GOOGLE_APPLICATION_CREDENTIALS = /Users/cyyeh/deep-learning-5cfd37943c26.json

dev:
	docker run -p $(LOCAL_PORT):$(DOCKER_PORT) -e PORT=$(DOCKER_PORT) -e GOOGLE_APPLICATION_CREDENTIALS=$(GOOGLE_APPLICATION_CREDENTIALS) -v $$GOOGLE_APPLICATION_CREDENTIALS:$(GOOGLE_APPLICATION_CREDENTIALS):ro ${GCR_HOST}/$(PROJECT_ID)/$(IMAGE_NAME)
submit:
	gcloud builds submit --tag ${GCR_HOST}/$(PROJECT_ID)/$(IMAGE_NAME)
submit-no-cache:
	gcloud builds submit --no-cache --tag ${GCR_HOST}/$(PROJECT_ID)/$(IMAGE_NAME)
build:
	docker build -t ${GCR_HOST}/${PROJECT_ID}/${IMAGE_NAME} .
deploy:
	gcloud run deploy --image ${GCR_HOST}/$(PROJECT_ID)/$(IMAGE_NAME) --platform managed