FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY Common Common
COPY Gateway/requirements.txt .
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

RUN ls -al

COPY Gateway/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "8"]