FROM python:3.7-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD . /code
RUN pip install --trusted-host pypi.python.org -r deploy/temp-requirements.txt
