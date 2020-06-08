LOCAL_PORT = 5000
DOCKER_PORT = 8080
DOCKERHUB_ID = chihyuyeh
PROJECT_ID = deep-learning-279406
IMAGE_NAME = dog-breed-classifier
GOOGLE_APPLICATION_CREDENTIALS = /Users/cyyeh/deep-learning-5cfd37943c26.json

dev-gcp:
	docker run -p $(LOCAL_PORT):$(DOCKER_PORT) -e PORT=$(DOCKER_PORT) -e GOOGLE_APPLICATION_CREDENTIALS=$(GOOGLE_APPLICATION_CREDENTIALS) -v $$GOOGLE_APPLICATION_CREDENTIALS:$(GOOGLE_APPLICATION_CREDENTIALS):ro gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)
dev-docker:
	docker run -p $(LOCAL_PORT):$(DOCKER_PORT) -e PORT=$(DOCKER_PORT) -e GOOGLE_APPLICATION_CREDENTIALS=$(GOOGLE_APPLICATION_CREDENTIALS) -v $$GOOGLE_APPLICATION_CREDENTIALS:$(GOOGLE_APPLICATION_CREDENTIALS):ro ${DOCKERHUB_ID}/${IMAGE_NAME}
build-gcp:
	gcloud builds submit --tag gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)
build-no-cache-gcp:
	gcloud builds submit --no-cache --tag gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)
build-docker:
	docker build -t ${DOCKERHUB_ID}/${IMAGE_NAME} .
deploy-gcp:
	gcloud run deploy --image gcr.io/$(PROJECT_ID)/$(IMAGE_NAME) --platform managed
deploy-docker:
	docker push ${DOCKERHUB_ID}/${IMAGE_NAME}