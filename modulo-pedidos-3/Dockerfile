FROM python:3.9-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app .

EXPOSE 5000

CMD ["/usr/local/bin/gunicorn", "--bind", "0.0.0.0:5000", "main:app"]