FROM python:3.10

RUN mkdir /book_broker_app

WORKDIR /book_broker_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

WORKDIR app

CMD python main.py