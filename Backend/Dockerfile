FROM python:3
# install postgress-client
RUN apt-get update && apt-get install -y postgresql-client

ENV PYTHONUNBUFFERED 1
WORKDIR /code
COPY . /code/
RUN chmod +x /code/wait_for_db.sh
RUN pip install -r requirements.txt