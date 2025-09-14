FROM python:3.12 AS deps

RUN pip install --upgrade pip 

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

FROM deps AS app

COPY . /app
WORKDIR /app

EXPOSE 5999
CMD [ "python", "app.py" ]