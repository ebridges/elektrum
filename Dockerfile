# start from an official image
FROM python:3.7

RUN mkdir -p /app
COPY . /app
WORKDIR /app
RUN chmod +x /app/docker-entrypoint.sh
RUN pip install pipenv && pipenv install --system
EXPOSE 8000
ENTRYPOINT [ "/app/docker-entrypoint.sh" ]
