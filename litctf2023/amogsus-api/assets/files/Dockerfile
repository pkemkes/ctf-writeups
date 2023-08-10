FROM python

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD flask --app main run --host=0.0.0.0 
