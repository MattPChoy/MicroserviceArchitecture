# basic Python image
FROM python:3.10

RUN pip install pika

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app/processor

COPY requester.py .
COPY database.db .

CMD [ "python", "processor.py" ]
