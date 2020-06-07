# Backend for Dog Breed Classifier

If you want to see the frontend part, please check out [here](https://github.com/cyyeh/dog-breed-classifier-web).

## Commands for Local Development

- `uvicorn main:app --reload`

## Commands for deploying to Cloud Run

reference: https://cloud.google.com/run/docs/quickstarts/build-and-deploy

- Build your container image using Cloud Build, by running the following command from the directory containing the Dockerfile
  - `gcloud builds submit --tag gcr.io/PROJECT-ID/PROJECT-NAME`
    - get `PROJECT-ID` by `gcloud config get-value project`
    - by `PROJECT-NAME`, you can decide what you want
- Deploying to Cloud Run
  - `gcloud run deploy --image gcr.io/PROJECT-ID/PROJECT-NAME --platform managed`
