FROM python:3.7-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD . /code
EXPOSE 80
RUN pip install --trusted-host pypi.python.org -r deploy/temp-requirements.txt
CMD python manage.py runserver 0.0.0.0:80
