FROM python:3.12

RUN pip install --upgrade pip 

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 5999
CMD [ "python", "app.py" ]