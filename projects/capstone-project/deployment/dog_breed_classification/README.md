# Backend for Dog Breed Classifier

If you want to see the frontend part, please check out [here](https://github.com/cyyeh/dog-breed-classifier-web).

## Commands for Local Development

- Without Using Docker
  - setup development environment: `pipenv install`
  - local development: `pipenv run uvicorn main:app --reload`
- Using Docker
  - `PORT=8080 && docker run -p 5000:${PORT} -e PORT=${PORT} -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/FILE_NAME.json -v $GOOGLE_APPLICATION_CREDENTIALS:/tmp/keys/FILE_NAME.json:ro gcr.io/PROJECT_ID/IMAGE`
    - get `PROJECT-ID` by `gcloud config get-value project`
    - `IMAGE` is your docker image name

## Commands for deploying to Cloud Run

reference: https://cloud.google.com/run/docs/quickstarts/build-and-deploy

- Build your container image using Cloud Build, by running the following command from the directory containing the Dockerfile
  - `gcloud builds submit --tag gcr.io/PROJECT-ID/PROJECT-NAME`
    - get `PROJECT-ID` by `gcloud config get-value project`
    - by `PROJECT-NAME`, you can decide what you want
- Deploying to Cloud Run
  - `gcloud run deploy --image gcr.io/PROJECT-ID/PROJECT-NAME --platform managed`
