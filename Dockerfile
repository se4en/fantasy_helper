FROM python:3.8-slim

WORKDIR /fantasy_help_bot

COPY requirements.txt /fantasy_help_bot/
COPY geckodriver-v0.27.0-linux64.tar.gz /fantasy_help_bot/
COPY chromedriver_linux64 /fantasy_help_bot/

RUN pip install -r /fantasy_help_bot/requirements.txt

RUN apt-get update
RUN apt-get install -y libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1



RUN chmod +x chromedriver
RUN cp chromedriver /usr/local/bin/

#RUN unrar e chromedriver_linux64.zip
#RUN tar -xvzf geckodriver-v0.27.0-linux64.tar.gz

#RUN rm geckodriver-v0.27.0-linux64.tar.gz
#RUN rm chromedriver_linux64.zip

#RUN chmod +x geckodriver
#RUN chmod -x chromedriver

#RUN cp chromedriver /usr/local/bin/
#RUN cp geckodriver /usr/local/bin/

COPY . /fantasy_help_bot/

CMD python3 /fantasy_help_bot/app.py