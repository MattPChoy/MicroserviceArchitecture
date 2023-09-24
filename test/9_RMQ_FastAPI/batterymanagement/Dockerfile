FROM python:3.8

WORKDIR /app
COPY . /app
ENV PYTHONUNBUFFERED=1

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
