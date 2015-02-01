"""Aliases and triggers as objects."""

class Source(object):
 """The top level object from which aliases and triggers are derived."""
 def __init__(self, pattern, code, classes, simple, title):
  """Set up ignored arguments."""
  self.ignoredArguments = ['ignoredArguments', 'code', 'pattern']
  self.pattern = pattern
  self.classes = classes
  self.simple = simple
  self.title = title
  self.setCode(code)
 
 def setCode(self, code):
  """Adds code to the object, compiling it ready for use."""
  self._code = code
  self.code = str(code) if self.simple else compile(code, 'errors.log', 'exec')
 
 def serialise(self):
  """Export the contents as (args, kwargs), ready to pass back into :func:`~world.World.addAlias`, or :func:`~world.World.addTrigger`."""
  args = [self.pattern if type(self.pattern) == str else self.pattern.pattern, self._code]
  kwargs = {}
  for x in dir(self):
   if not x.startswith('_') and x not in self.ignoredArguments and not callable(getattr(self, x)):
    kwargs[x] = getattr(self, x)
  return (args, kwargs)
