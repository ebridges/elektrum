# start from an official image
FROM python:3.7

RUN mkdir -p /opt/services/elektron
WORKDIR /opt/services/elektron
COPY . /opt/services/elektron
RUN chmod +x docker-entrypoint.sh
RUN pip install pipenv && pipenv install --system
EXPOSE 8000
CMD ["gunicorn", "--chdir", "elektron/project", "--bind", ":8000", "elektron.wsgi:application"]
ENTRYPOINT [ "./docker-entrypoint.sh" ]
