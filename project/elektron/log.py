import logging

loggers = {}

# https://stackoverflow.com/a/7175288/87408
def getLogger(name):
  global loggers
  logger_name = 'elektron.%s' % name
  if loggers.get(logger_name):
    return loggers.get(logger_name)
  else:
    logger = logging.getLogger(logger_name)
    loggers[logger_name] = logger
    return logger
