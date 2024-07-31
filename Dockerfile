FROM python:3.10

RUN apt-get update && apt-get install
RUN pip install --upgrade pip
RUN pip install --upgrade pip setuptools wheel
RUN apt-get install poppler-utils -y
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /home/nano

COPY smiles.py smiles.py
COPY input input

RUN python smiles.py

