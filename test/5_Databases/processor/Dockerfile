# basic Python image
FROM python:3.10

RUN pip install pika
RUN pip install sqlalchemy
RUN pip install psycopg2

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app/processor

COPY processor.py .
COPY database.db .

CMD [ "python", "processor.py" ]
