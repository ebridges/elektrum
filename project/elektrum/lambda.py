from apig_wsgi import make_lambda_handler
from elektrum.wsgi import app

lambda_handler = make_lambda_handler(app)
