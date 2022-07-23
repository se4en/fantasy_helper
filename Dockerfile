FROM python:3.8-buster

RUN apt-get update -y && apt-get install -y python3-pip python3-dev build-essential

WORKDIR /bot
COPY requirements.txt /bot/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /bot

CMD ["python", "app.py"]
