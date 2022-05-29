FROM python:3.8-slim-buster

WORKDIR /app
RUN apt-get update -y
RUN apt-get install -y curl
RUN pip install --upgrade pip


COPY . /app/

RUN pip install -r requirements.txt

CMD [ "python3", "./main.py"]