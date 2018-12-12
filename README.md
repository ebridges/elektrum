
## Elektron

https://www.ybrikman.com/writing/2015/05/19/docker-osx-dev/
https://www.ybrikman.com/writing/2015/11/11/running-docker-aws-ground-up/
https://www.ybrikman.com/writing/2016/03/31/infrastructure-as-code-microservices-aws-docker-terraform-ecs/
https://www.expeditedssl.com/aws-in-plain-english
https://wsvincent.com/django-docker-postgresql/

https://docs.djangoproject.com/en/2.1/intro/tutorial01/
https://wsvincent.com/django-testing-tutorial/
https://medium.com/@tomwwright/automating-with-ansible-building-a-vpc-c252944d3d2e


AMI that has ECS Client & Docker Server pre-installed:
ami_id: 'ami-07eb698ce660402d2'

#### Running the Application

*Running Locally*

Django `runserver`:

* `cd project`
* `ELEKTRON_ENV=development python manage.py runserver`
* `open http://localhost:8000`

Gunicorn:

* `cd project`
* `ELEKTRON_ENV=development gunicorn --bind :8000 elektron.wsgi:application`
* `open http://localhost:8000`

*Running in a container*

Building the container image:

* `docker build -t roja/elektron:latest .`

_Before running, specify the environment by editing `ELEKTRON_ENV` in `etc/config.env`._

To run via Docker:

* `docker run --publish 8000:8000 roja/elektron:latest`
* `open http://localhost:8000`

Run via Docker Compose:

_Docker compose runs the application behind a proxy, so it listens on `80` instead._

* `docker-compose up`
* `open http://localhost:80`

#### Misc Info

Build network:

* see `network/README.md`

