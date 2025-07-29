FROM python:3.11-slim-bullseye as build

RUN pip install requests

WORKDIR /app

#COPY inviter.py /app

COPY . .

CMD [ "python", "/app/inviter.py" ]