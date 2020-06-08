FROM python:3.6-slim

ENV APP_HOME /app
WORKDIR $APP_HOME

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . ./

CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT