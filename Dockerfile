FROM python:3.12-alpine

WORKDIR /memorify

COPY ./requirements.txt /memorify/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /memorify/app

CMD ["fastapi", "run", "app/main.py", "--port", "3000"]