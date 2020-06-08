LOCAL_PORT = 5000
DOCKER_PORT = 8080
DOCKERHUB_ID = chihyuyeh
PROJECT_ID = deep-learning-279406
IMAGE_NAME = dog-breed-classifier
GOOGLE_APPLICATION_CREDENTIALS = /Users/cyyeh/deep-learning-5cfd37943c26.json

gcp-dev:
	docker run -p $(LOCAL_PORT):$(DOCKER_PORT) -e PORT=$(DOCKER_PORT) -e GOOGLE_APPLICATION_CREDENTIALS=$(GOOGLE_APPLICATION_CREDENTIALS) -v $$GOOGLE_APPLICATION_CREDENTIALS:$(GOOGLE_APPLICATION_CREDENTIALS):ro gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)
docker-dev:
	docker run -p $(LOCAL_PORT):$(DOCKER_PORT) -e PORT=$(DOCKER_PORT) -e GOOGLE_APPLICATION_CREDENTIALS=$(GOOGLE_APPLICATION_CREDENTIALS) -v $$GOOGLE_APPLICATION_CREDENTIALS:$(GOOGLE_APPLICATION_CREDENTIALS):ro ${DOCKERHUB_ID}/${IMAGE_NAME}
gcp-build:
	gcloud builds submit --tag gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)
gcp-build-no-cache:
	gcloud builds submit --no-cache --tag gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)
docker-build:
	docker build -t ${DOCKERHUB_ID}/${IMAGE_NAME} .
gcp-deploy:
	gcloud run deploy --image gcr.io/$(PROJECT_ID)/$(IMAGE_NAME) --platform managed
docker-deploy:
	docker push ${DOCKERHUB_ID}/${IMAGE_NAME}