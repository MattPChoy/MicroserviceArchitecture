FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY ./app.py /app/app.py
COPY ./requirements.txt /app/requirements.txt
ENV PYTHONUNBUFFERED=1

RUN pip install -r /app/requirements.txt
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]