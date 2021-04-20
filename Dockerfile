FROM python:3.8

ENV DIRPATH=/usr/cultr

RUN mkdir -p $DIRPATH
COPY . $DIRPATH
WORKDIR $DIRPATH

RUN python3 -m venv venv
RUN . $DIRPATH/venv/bin/activate && pip install -r requirements.txt; exit 0

EXPOSE 5000

CMD . $DIRPATH/venv/bin/activate && exec python3 -m "uvicorn" cultr.app:app --host 0.0.0.0 --port 5000
