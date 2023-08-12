FROM python:3.9-slim

RUN apt-get update -y && apt-get install -y python3-pip python3-dev build-essential

WORKDIR /fantasy_helper
COPY requirements.txt /fantasy_helper/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /fantasy_helper/
ENV PYTHONPATH "${PYTHONPATH}:/fantasy_helper"

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "fantasy_helper/app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
