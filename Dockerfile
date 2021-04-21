FROM python:3.8

WORKDIR /cultr
COPY . .

RUN pip3 install -r requirements.txt; exit 0

EXPOSE 5000

CMD python3 -m "uvicorn" cultr.app:app --host 0.0.0.0 --port 5000
