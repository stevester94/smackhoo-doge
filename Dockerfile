FROM python:3.11

WORKDIR /app

ADD requirements.txt .
#RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

ADD server.py .
ADD utils.py .
ADD html html

