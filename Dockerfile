FROM python:3.10

WORKDIR /app

COPY ./app .

RUN pip install -r requirements.txt
RUN pip install fastapi uvicorn

EXPOSE 8000

CMD ["sh", "start.sh"]