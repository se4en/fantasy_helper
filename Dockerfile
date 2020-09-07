FROM python:3.8-slim

WORKDIR /fantasy_help_bot

COPY requirements.txt /fantasy_help_bot/

RUN pip install -r /fantasy_help_bot/requirements.txt

RUN apt-get update
RUN apt-get -y install wget

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz \
&& tar -xvzf geckodriver-v0.27.0-linux64.tar.gz
RUN rm geckodriver-v0.27.0-linux64.tar.gz
RUN chmod +x geckodriver
RUN cp geckodriver /usr/local/bin/

COPY . /fantasy_help_bot/

CMD python3 /fantasy_help_bot/app.py