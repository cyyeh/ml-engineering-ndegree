# Backend for Dog Breed Classifier

If you want to see the frontend part, please check out [here](https://github.com/cyyeh/dog-breed-classifier-web).

## Commands

- local development without docker:
  - `pip install pipenv` (If you don't have `pipenv` installed)
  - `pipenv install`
  - `pipenv run uvicorn main:app --reload`

Below commands are already written in `Makefile`, please checkout and change any setting you need first.
- local development using docker:
  - `make docker-dev`
- build a docker image:
  - `make docker-build`
- deploy a docker image:
  - `make docker-deploy`
