FROM python:3.9.5

RUN mkdir /avocato_privet

WORKDIR /avocato_privet

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

WORKDIR .

