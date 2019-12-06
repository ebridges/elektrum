from apig_wsgi import make_lambda_handler
from elektrum.wsgi import app

handler = make_lambda_handler(app)
