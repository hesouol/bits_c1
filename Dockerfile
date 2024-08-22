FROM python:3.9-slim

ENV APP_HOME="/home/bitso"
ENV PYTHONFAULTHANDLER=1
RUN useradd --create-home bitso
WORKDIR ${APP_HOME}

COPY . ${APP_HOME}
RUN pip install -r requirements.txt

RUN chown -R bitso:bitso .
USER bitso

ENTRYPOINT ["python3","src/bitso_etl.py"]
