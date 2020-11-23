FROM python:3.9.0

RUN mkdir /web
ADD . /web/
WORKDIR /web

RUN pip install -r requirements.txt

CMD ["python3", "run.py"]