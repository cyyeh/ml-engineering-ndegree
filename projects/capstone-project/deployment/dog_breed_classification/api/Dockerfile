FROM python:3.6-slim

ENV APP_HOME /app
WORKDIR $APP_HOME

COPY . ./

RUN pip install -r requirements.txt

CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT