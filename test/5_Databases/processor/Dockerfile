# basic Python image
FROM python:3.10

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app/processor

COPY processor.py .
COPY database.db .

CMD [ "python", "processor.py" ]
