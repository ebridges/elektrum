from apig_wsgi import make_lambda_handler
from elektrum.wsgi import application

handler = make_lambda_handler(application)
