FROM python:3-slim

WORKDIR /app

RUN pip install pipenv
COPY Pipfile Pipfile.lock ./

RUN pipenv install --dev

COPY . .

EXPOSE 5000

CMD ["sh", "./run_devserver.sh"]
