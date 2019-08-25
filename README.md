VSCode Setup
https://gist.github.com/ebridges/9e2e5a840c91c7a034c80e3e43dd3a9b

PyCharm Setup for Coverage
https://gist.github.com/ebridges/d1ebe05e9fd87e409f6e5c978e44bde1


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

*Prerequisites*

* Configure environment:

`export ELEKTRON_ENV=[development|staging|production]`

* Generate environment file for the environment
  
  `cd network && ./run.sh --tags=common,cfg`

* Edit `db_hostname` in `etc/env/development.env` to be the IP address of the development database.

*Running Locally*

Django `runserver`:

* `cd project`
* `python manage.py runserver`
* `open http://localhost:8000`

Running with HTTPS:

* `cd project`
* `python manage.py runsslserver 127.0.0.1:8000`
* `open https://127.0.0.1:8000`

Gunicorn:

* `cd project`
* `gunicorn --bind :8000 elektron.wsgi:application`
* `open http://localhost:8000`

*Running in a container*

Building the container image for the App:

* `docker build --file Dockerfile-App --build-arg ELEKTRON_ENV=${ELEKTRON_ENV} -t roja/elektron_app:latest .`

Building the container image for the Proxy:

* `docker build --file Dockerfile-Proxy --build-arg ELEKTRON_ENV=${ELEKTRON_ENV} -t roja/elektron_proxy:latest .`

To run via Docker:

* `docker run --env ELEKTRON_ENV=${ELEKTRON_ENV} --publish 8000:8000 roja/elektron_app:latest`
* `open http://localhost:8000`

Run via Docker Compose:

_Docker compose runs the application behind a proxy, so it listens on `80` instead._

* `ELEKTRON_ENV=[development|staging|production] docker-compose up`
* `open http://localhost:80`

#### Misc Info

**To build network**

* see `network/README.md`

**Configuring a certificate for a domain name**

1. Request a public certificate via ACM.
1. Add the bare domain name and a `*` wildcard for the domain.
1. Choose DNS validation, and copy/retain the "Name" and "Value" for the CNAME record.
1. Add tags for the name & service of the certificate.
1. In Route 53, create a new hosted zone for the domain name; copy/retain the DNS Name Servers.
1. In the domain registrar's admin panel, paste the CNAME record and the Name Servers into the config for the domain into the registrar's admin panel.
1. Wait for the validation of the HTTPs certificate to complete.

Further Info:
* https://romandc.com/zappa-django-guide/walk_domain/#option-1-route53-and-acm

### Common Errors

<dl>
<dt><strong><tt>TypeError: 'NoneType' object is not callable</tt> when deploying to an environment</strong></dt>
<dd>
Causes can vary.
<br>
Check:
<li>Ensure host is in `ALLOWED_HOSTS` in the Django configuration.</li>
</dd>
<dt><strong><tt>
ResourceNotFoundException: An error occurred (ResourceNotFoundException) when calling the DescribeLogStreams operation: The specified log group does not exist.</tt></strong>
</dt>
<dd>
<li>Ensure that API has permissions to log to Cloudwatch.
<br>
Add <tt>arn:aws:iam::743873495175:role/elektrum-development-ZappaLambdaExecutionRole</tt> to <kbd>API Gateway / Settings / CloudWatch log role ARN</kbd>
<br>
<a href="https://stackoverflow.com/a/50022932/87408">https://stackoverflow.com/a/50022932/87408</a>
</li>
</dd>
<dl>

