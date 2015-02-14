errors = {
 'AlreadyConnected': 'This world is already connected.',
 'NoWorldYet': 'There is currently no world connected.',
 'NoHostYet': 'There is no hostname set for this world.',
 'NoPortYet': 'There is no port set for this world.',
 'NoConfigFileYet': 'There is no configuration file set for this world.',
 'InvalidPort': 'Port numbers must be between 1 and 65535.',
 'NotConnectedYet': 'This world is not connected yet.',
 'OutputThreadStarted': 'The output thread is already started.'
}

class UserError(Exception):
 pass

class ErrorHandler(object):
 """Dummy stderr, to log errors before the program has begun."""
 def __init__(self):
  self.buffer = ''
 
 def write(self, line):
  self.buffer += line
