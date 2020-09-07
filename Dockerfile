FROM python:3.8-slim

WORKDIR /fantasy_help_bot

COPY requirements.txt /fantasy_help_bot/
RUN pip install -r /fantasy_help_bot/requirements.txt

COPY . /fantasy_help_bot/

CMD python3 /fantasy_help_bot/app.py