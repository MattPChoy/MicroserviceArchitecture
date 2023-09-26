FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

WORKDIR /usr/src/app/Gateway


COPY . /app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]