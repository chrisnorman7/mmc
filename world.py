"""The World class. Should be instantiated every time a new world is required."""

from telnetlib import Telnet, socket
from sound_lib import stream, output
from sound_lib.main import BassError
from errors import *
from inspect import getdoc
from collections import deque, OrderedDict
from confmanager import ConfManager, parser
from wx.lib.filebrowsebutton import *
from wx.lib.agw.floatspin import FloatSpin
from random import Random
import threading, os, re, wx, accessibility, json, unicodedata, codecs, source, match, sys
from time import ctime, time, strftime
from types import NoneType

fileext = '.mmcworld' # The default file extention for world files.
class World(object):
 """The main world class."""
 #First, set up some commonly used properties:

 @property # Guess if the world is connected.
 def connected(self):
  return isinstance(self.con, Telnet)

 @connected.setter # Don't let them try to set it:
 def connected(self, value):
  raise RuntimeError('To change the connection state, please use the open and close methods.')

 @property # The name of the world.
 def name(self):
  return self.config.get('world', 'name')

 @name.setter
 def name(self, value):
  self.config.set('world', 'name', value)

 @property # The hostname of the world.
 def hostname(self):
  return self.config.get('connection', 'hostname')

 @hostname.setter
 def hostname(self, value):
  self.config.set('connection', 'hostname', value)

 @property # The world's port.
 def port(self):
  return self.config.get('connection', 'port')

 @port.setter
 def port(self, value):
  self.config.set('connection', 'port', value)

 @property # The filename to load the world's settings from.
 def filename(self):
  # Make sure the filename ends with the proper file extention.
  retval = self._filename
  if retval and not retval.endswith(fileext):
   retval += fileext
  return retval

 @filename.setter
 def filename(self, value):
  self._filename = value
 
 @property # The working directory of the world.
 def directory(self):
  return os.path.dirname(self.filename)
 
 @property # The command char
 def commandChar(self):
  return self.config.get('entry', 'commandchar')

 @commandChar.setter
 def commandChar(self, value):
  self.config.set('entry', 'commandchar', value)
 
 def __init__(self):
  """Create all the default config, then you can use .load(filename) to load the config from disk."""
  self.escape = chr(27)
  self.baseVolume = 1.0
  self.colourRe = re.compile(r'(%s\[((?:\d;)?\d{1,2})m)' % self.escape)
  encodeTest = lambda value: None if codecs.getencoder(value) else 'Traceback should be self explanitory'
  self.logEncoding = 'UTF-8'
  self.normalise = lambda value: unicodedata.normalize(self.config.get('entry', 'unicodeform'), unicode(value)).encode(self.config.get('entry', 'encoding'), 'ignore')
  self.soundOutput = output.Output() # Just keep this stored.
  self._outputThread = None # The output thread, to be checked at the start of _threadManager.
  self.logFile = 'Output %s.log' % strftime('%Y-%m-%d %H-%M-%S').replace(':', '-')
  self.write = lambda value: self.output(value) # For tracebacks and the like.
  self.colours = {
   '0': ('white', 'black'),
   '30': ('Black', None),
   '31': ('red', None),
   '32': ('green', None),
   '33': ('yellow', None),
   '34': ('blue', None),
   '35': ('purple', None),
   '36': ('cyan', None),
   '37': ('white', None),
   '39': ('white', None),
   '40': (None, 'black'),
   '41': (None, 'red'),
   '42': (None, 'green'),
   '43': (None, 'yellow'),
   '44': (None, 'blue'),
   '45': (None, 'purple'),
   '46': (None, 'cyan'),
   '47': (None, 'white'),
   '49': (None, 'black')
  }
  self.styles = {
   '1': ('bold', True),
   '3': ('italics', True),
   '4': ('underline', True),
   '5': ('blinking', True),
   '9': ('strikethrough', True),
   '22': ('bold', False),
   '23': ('italics', False),
   '24': ('underline', False),
   '25': ('blinking', False),
   '29': ('strikethrough', False)
  }
  (fg, bg) = self.colours['0']
  self._fg = fg
  self._bg = bg
  self.commandQueue = deque() # Queue for self._send.
  self._commandInterval = 0.0 # Time since last command was executed.
  self.basicTypes = [
   str,
   dict,
   list,
   tuple,
   unicode,
   int,
   long,
   float,
   bool,
   NoneType
  ]
  self.random = Random()
  self.soundRe = re.compile(r'(.*)([*]\d+)(.*)')
  self.codeRe = re.compile(r'^\n( +)', re.M)
  self.variableRe = re.compile(r'(@([a-zA-Z]\w+))')
  self.statementRe = re.compile(r'(@\{([^}]+)\})')
  self._filename = '' # The property where the filename will be stored (fill it with self.load).
  self.environment = {
   'world': self,
   'accessibility': accessibility,
   're': re,
  }
  self._log = [] # The complete log of the session, containing both input and output.
  self._logIndex = 0 # The entry of the last entry which was written to disk.
  self._output = [] # The text which should be in the output window.
  self.outputBuffer = None # Must contain a .write method.
  self.errorBuffer = ErrorBuffer(self.output, [], {'process': False}) # Make errors beep.
  self.outputSub = None
  self.logSub = None # The line to write to the log in place of the actual line.
  self._gag = {
   'entry': 0,
   'output': 0,
   'voice': 0,
   'braille': 0
  }
  self.con = None # The Telnet connection.
  self.invalidPort = lambda value: None if (value >= 1 and value <= 65535) else errors['InvalidPort']
  self.onSend = lambda: None
  self.onOutput = lambda: None
  self.onBeep = lambda: self.errorBuffer.beepFunc()
  self.onSave = lambda: None # The method to be called when the world is saved.
  self.onOpen = lambda: None # The method to be called when the connection is opened.
  self.onConnected = lambda: None # The method to be called when the connection is established.
  self.onClose = lambda: None # The method to be called when the connection is closed.
  self.onError = lambda error = None: self.errorBuffer.write(error)
  self.onTrigger = lambda: None
  self.onAlias = lambda: None
  # Create default configuration, and let self.load override it if the user wants:
  self.defaultConfig = {
   'config': {},
   'aliases': {},
   'triggers': {},
   'variables': {}
  }
  self.config = ConfManager('World properties')
  self.config.add_section('world')
  self.config.set('world', 'name', 'Untitled World', title = 'The name of the world', validate = lambda value: None if value else 'World names cannot be blank')
  self.config.set('world', 'username', '', title = 'The username to use for this world')
  self.config.set('world', 'password', '', title = 'The password for this world (saves in plain text)', kwargs = {'style': wx.TE_PASSWORD})
  self.config.set('world', 'notes', '', title = 'Notes for this world', kwargs = {'style': wx.TE_RICH|wx.TE_MULTILINE})
  self.config.set('world', 'autosave', True, title = 'Save this world automatically when closed')
  self.config.add_section('connection')
  self.config.set('connection', 'hostname', '', title = 'The hostname of the world', validate = lambda value: None if value else 'Without a hostname, your world will not be able to connect.')
  self.config.set('connection', 'port', 0, title = 'The port to use for this world', validate = self.invalidPort)
  self.config.set('connection', 'autoconnect', True, title = 'Automatically connect this world when it opens')
  self.config.set('connection', 'connectstring', '', title = 'The connection string, using {u} for username and {p} for password, and seperating the commands with your command seperator')
  self.config.add_section('entry')
  self.config.set('entry', 'commandchar', '/', validate = lambda value: None if (not re.match('[A-Za-z0-9]', value) and len(value) == 1) else 'The command character can not be a letter or a number, and must be only one character.', title = 'The character to make commands get executed by the client rather than being sent straight to the mud')
  self.config.set('entry', 'helpchar', '?', title = 'The command to indicate you need help on something (clear to disable)')
  self.config.set('entry', 'commandsep', ';', title = 'The character which seperates multiple commands', validate = lambda value: None if len(value) == 1 else 'Commands must be seperated by only one character')
  self.config.set('entry', 'commandinterval', 0.0, title = 'The time between sending batched commands', kwargs = {'min_val': 0.0, 'increment': 0.1, 'digits': 2})
  self.config.set('entry', 'echocommands', True, title = 'Echo commands to the output window')
  self.config.set('entry', 'logduplicatecommands', False, title = 'Log duplicate commands')
  self.config.set('entry', 'processaliases', True, title = 'Process aliases')
  self.config.set('entry', 'simple', False, title = 'When adding new aliases and triggers, send their code directly to the game after replacing arguments instead of executing them (can be changed by setting the simple flag)')
  self.config.set('entry', 'prompt', 'Entry', title = 'Prompt')
  self.config.set('entry', 'escapeclearsentry', True, title = 'Clear the entry line when the escape key is pressed')
  self.config.set('entry', 'unicodeform', 'NFKD', title = 'The unicode normalize form', validate = lambda value: None if value in ['NFC', 'NFD', 'NFKC', 'NFKD'] else 'Form must be a valid form for unicodedata.normalize.')
  self.config.set('entry', 'encoding', 'ascii', title = 'Text encoding for commands sent to the server', validate = encodeTest)
  self.config.add_section('output')
  self.config.set('output', 'suppressblanklines', True, title = 'Suppress blank lines in the output window')
  self.config.set('output', 'gag', False, title = 'Gag all output')
  self.config.set('output', 'processtriggers', True, title = 'Process triggers')
  self.config.set('output', 'printtriggers', False, title = 'Print the titles or regular expressions of matched triggers to the output window (useful for debugging)')
  self.config.set('output', 'printunrecognisedformatters', False, title = 'Print unrecognised formatters to the output window')
  self.config.add_section('accessibility')
  self.config.set('accessibility', 'speak', True, title = 'Speak output')
  self.config.set('accessibility', 'braille', True, title = 'Braille output (if supported)')
  self.config.set('accessibility', 'outputscroll', True, title = 'Allow output window scrolling')
  self.config.set('accessibility', 'printcolours', False, title = 'Print ANSI formatters in the output window')
  self.config.add_section('logging')
  self.config.set('logging', 'logdirectory', '', title = 'Directory to store world log files', validate = lambda value: None if (not value or os.path.isdir(os.path.abspath(os.path.join(self.directory, value)))) else 'Directory must exist. If you do not want logging, leave this field blank.', control = DirBrowseButton)
  self.config.set('logging', 'loginterval', 50, title = 'After how many lines should the log be dumped to disk', validate = lambda value: None if value > 10 else 'At least 10 lines must seperate dump opperations.')
  self.config.set('logging', 'logencoding', 'UTF-8', title = 'The encoding for log files', validate = encodeTest)
  self.config.add_section('sounds')
  self.config.set('sounds', 'mastermute', False, title = 'Mute sounds')
  self.config.set('sounds', 'mastervolume', 75, title = 'Master volume', validate = lambda value: None if value >= 0 and value <= 100 else 'Volume must be between 0 and 100.')
  self.config.add_section('scripting')
  self.config.set('scripting', 'enable', True, title = 'Enable scripting')
  self.config.set('scripting', 'expandvariables', True, title = 'Expand variables on the command line')
  self.config.set('scripting', 'variablere', self.variableRe.pattern, title = 'The regular expression variable declarations on the command line must conform too', validate = lambda value: setattr(self, 'variableRe', re.compile(value)))
  self.config.set('scripting', 'expandstatements', True, title = 'Expand statements on the command line')
  self.config.set('scripting', 'statementre', self.statementRe.pattern, title = 'The regular expression statements entered on the command line must conform too', validate = lambda value: setattr(self, 'statementRe', re.compile(value)))
  self.config.set('scripting', 'startfile', '', title = 'The main script file', control = FileBrowseButton, validate = lambda value: None if not value or os.path.isfile(os.path.abspath(os.path.join(self.directory, value))) else 'This field must either be blank, or contain the path to a script file.')
  self.config.set('scripting', 'bypasscharacter', '>', title = 'The command to bypass scripting on the command line')
  self.config.add_section('saving')
  self.config.set('saving', 'aliases', False, title = 'Save aliases in the world file')
  self.config.set('saving', 'triggers', False, title = 'Save triggers in the world file')
  self.config.set('saving', 'variables', True, title = 'Save variables in the world file')
 
 def load(self, filename = None):
  """
  Loads the configuration from filename if provided, and executes the default script file if scripting is enabled.
  
  """
  self.aliases = OrderedDict() # The internal list of aliases.
  self.triggers = OrderedDict() # The internal list of triggers.
  self.literalTriggers = OrderedDict() # The triggers that don't contain any variable text.
  self.variables = deque() # The variables to save when the world is closed.
  self.classes = deque() # The currently active classes.
  if filename:
   self._validFile(filename)
   with open(filename, 'r') as f:
    self.defaultConfig = json.load(f)
  self.config = parser.parse_json(self.config, self.defaultConfig['config'])
  self.soundOutput.set_volume(0.0 if self.config.get('sounds', 'mastermute') else self.config.get('sounds', 'mastervolume'))
  for args, kwargs in self.defaultConfig['aliases']:
   self.addAlias(*args, **kwargs)
  for args, kwargs in self.defaultConfig['triggers']:
   self.addTrigger(*args, **kwargs)
  for k, v in self.defaultConfig['variables'].iteritems():
   self.addVariable(k, v, True)
  if filename:
   d = os.path.dirname(filename)
   if d:
    sys.path.insert(0, d)
   self.filename = os.path.abspath(filename)
  f = self.config.get('scripting', 'startfile')
  if f:
   f = os.path.join(os.path.dirname(self.filename), f)
   execfile(f, self.getEnvironment())
   if not self.connected and self.config.get('connection', 'autoconnect') and self.hostname and not self.invalidPort(self.port):
    self.open()
   else:
    print '%s: (%s, %s).' % (self.config.get('connection', 'autoconnect'), self.hostname, self.port)
 
 def reload(self, filename = None):
  """Reloads the world, saving first if required."""
  if self.config.get('world', 'autosave'):
   self.save()
  self.load(filename or self.filename)
 
 def save(self):
  """
  Write the configuration to disk.
  
  """
  if not self.filename:
   raise IOError(errors['NoConfigFileYet'])
  self.onSave()
  stuff = dict()
  for thing in ['aliases', 'triggers']:
   stuff[thing] = [] # Populate with (args, kwargs) pairs.
   if self.config.get('saving', thing):
    for c, o in getattr(self, thing).iteritems():
     stuff[thing].append(o.serialise())
  stuff['variables'] = dict()
  if self.config.get('saving', 'variables'):
   for v in self.variables:
    if hasattr(self, v):
     var = getattr(self, v)
     if type(var) in self.basicTypes:
      stuff['variables'][v] = var
  stuff['config'] = self.config.get_dump()
  with open(self.filename, 'w') as f:
   json.dump(stuff, f, indent = 1, sort_keys = True) # Finally write the completed dictionary.
 
 def addAlias(self, alias, command, classes = [], title = None, simple = None):
  """
  addAlias(alias, command[, classes[, title[, simple]]])
  
  Adds an alias to the world.
  
  * alias is the command which will be used to invoke the alias, given as a regular expression.
  * Command is the command to be sent to the mud when this alias is used.
  * Classes is a list of the classes this alias applies too. It defaults to an empty list.
  * title is the title of the alias, and defaults to the alias text itsself.
  * simple is used to override the simple setting in the entry configuration.
  
  """
  if simple == None:
   simple = self.config.get('entry', 'simple')
  if title == None:
   title = alias
  c = re.compile(alias)
  self.aliases[c] = source.Source(c, self.formatCode(command), classes, simple, title)
 
 def removeAlias(self, alias):
  """
  removeAlias(alias)
  
  Removes an alias from the world.
  
  * Alias is the title of the alias to remove.
  
  """
  for k, v in self.aliases.iteritems():
   if v.title == alias:
    del self.aliases[k]
    return True
  return False
 
 def addTrigger(self, trigger, command, classes = [], regexp = True, simple = None, stop = True, title = None):
  """
  addTrigger(trigger, command[, classes[, regexp[, simple[, stop[, title]]]]])
  
  Adds a trigger to the world.
  
  * Trigger is a regular expression of the line from the mud this trigger must match too.
  * Command is the command which should be sent to the mud when this trigger is found.
  * Classes is a list of the classes this trigger applies too. It defaults to an empty list.
  * regexp tells the world if this trigger is a regular expression, or a literal string (use of literal strings can speed up performance).
  * simple is used to override the simple setting in the entry configuration.
  * stop tells the trigger to stop processing after it has completed. Defaults to True.
  * title is the friendly name of the trigger, and defaults to trigger.
  
  """
  if simple == None:
   simple = self.config.get('entry', 'simple')
  if title == None:
   title = trigger
  c = command if simple else self.formatCode(command)
  t = source.Source(re.compile(trigger) if regexp else trigger, c, classes, simple, title)
  t.regexp = regexp
  t.stop = stop
  if regexp:
   self.triggers[t.pattern] = t
  else:
   self.literalTriggers[trigger] = t

 def removeTrigger(self, trigger):
  """
  removeTrigger(trigger)
  
  Removes a trigger from the world.
  
  * Trigger is the title or the regular expression or literal string of the trigger you want to remove.
  
  Note: in cases where a trigger has been coded with a title, that must be used instead of the regular expression. All other triggers will have their title set to the regular expression or literal string they were created with.
  
  """
  for k, t in self.literalTriggers.iteritems():
   if t.title == trigger:
    del self.literalTriggers[k]
    return False
  else:
   for k, t in self.triggers.iteritems():
    if t.title == trigger:
     del self.triggers[k]
     return True
  return False
 
 def addVariable(self, name, value, save = False):
  """
  addVariable(name, value[, save = False])
  
  Add a variable to the world.
  
  * Name is the name of the variable.
  * Value is the value of the variable.
  * If save is True, then this variable will be saved along with the rest of the world.
  
  """
  setattr(self, name, value)
  if save and name not in self.variables:
   self.variables.append(name)

 def removeVariable(self, name, delete = True):
  """
  removeVariable(name[, delete])
  
  Removes a variable from the world's list of variables to save with the world.
  
  * Name is the name of the variable to remove.
  * If delete is True, then the variable will also be deleted.
  
  """
  if name in self.variables:
   self.variables.remove(name)
  if delete and hasattr(self, name):
   delattr(self, name)

 def open(self):
  """
  Opens the connection to the mud if it's not already open.
  
  """
  if self.connected:
   raise UserError(errors['AlreadyConnected'])
  if not self.hostname:
   raise UserError(errors['NoHostYet'])
  reason = self.invalidPort(self.port)
  if reason:
   raise UserError(reason)
  try:
   self.soundOutput.start()
  except BassError as e:
   pass # It's probably already been started.
  if self._outputThread:
   raise RuntimeError('%s (%s)' % (errors['OutputThreadStarted'], self._outputThread))
  self._outputThread = OutputThread(target = self._threadManager, name = 'World Thread') # Create the thread.
  try:
   self.onOpen()
  except Exception as e:
   self.outputStatus('Error in self.onOpen: %s' % e)
  self._outputThread.start()
 
 def close(self):
  """
  Closes the connection to the mud.
  
  """
  if self.connected:
   #self.onClose()
   self.con.close()
   self._close() # Reset the thread and connection, and stop all sounds playing through the output.
  else:
   raise UserError(errors['NotConnectedYet'])

 def _threadManager(self):
  """
  Manages the thread that reads the output from the game and processes commands.
  
  """
  if self.connected:
   raise UserError(errors['AlreadyConnected'])
  try:
   self.con = Telnet(self.hostname, self.port)
   self.onConnected()
  except Exception as problem:
   self._close()
   raise problem
  self.outputStatus('Connected to %s (%s), on port %s.' % (self.hostname, socket.getaddrinfo(self.hostname, self.port)[0][4][0], self.port))
  cs = self.config.get('connection', 'connectstring')
  uid = self.config.get('world', 'username')
  password = self.config.get('world', 'password')
  if cs and uid and password:
   for c in cs.format(u = uid, p = password).split(self.config.get('entry', 'commandsep')):
    self.writeToCon(c)
  while not self._outputThread.shouldStop():
   if self.commandQueue and (time() - self._commandInterval) >= self.config.get('entry', 'commandinterval'):
    threading.Thread(name = 'Command Thread', target = self._send, args = [self.commandQueue.popleft()]).start()
   try:
    output = self.con.read_very_eager()
   except Exception as msg:
    self.onError()
    self.outputStatus(str(msg)) # Print the error to the world.
    break
   if output:
    self.output(output)
  if self.connected:
   self.close()
  else:
   self.onClose()
  self.logFlush()
  self._outputThread = None # Set the thread back to it's original value.
 
 def output(self, data, process = None, sub = None, log = True):
  """
  output(data[, process[, sub[, log]]])
  
  Handles output, logging and printing.
  
  * process decides whether or not to try and match triggers, and defaults to the setting in the output configuration.
  * sub overrides any substitution performed with the substitute command.
  * log decides whether to log the line or not. Set to false to output but not log.
  
  """
  if type(data) not in [str, unicode]:
   data = str(data)
  data = data.replace('\r', '')
  if process == None:
   process = self.config.get('output', 'processtriggers')
  for line in data.split('\n'):
   self.onOutput()
   if '\a' in line:
    self.onBeep()
    line = line.replace('\a', '<beep>' if self.config.get('accessibility', 'printcolours') else '')
    if not line:
     continue
   toBeLogged = line
   (line, actual) = self._processLine(line)
   if line and process:
    tobject = None
    results = []
    while True:
     if line in self.literalTriggers:
      trigger = self.literalTriggers[line]
      if self.matchClasses(trigger.classes):
       results.append((trigger, [], {}))
     if not self.triggers:
      break
     results += match.match(line, self.triggers.values(), self.matchSource).results
     break
    for trigger, args, kwargs in results:
     self.onTrigger()
     if self.config.get('output', 'printtriggers'):
      self.output(trigger.title, False)
     args = [line] + list(args)
     if trigger.simple:
      self.send(self.formatSimple(trigger.code, args), log = False)
     else:
      try:
       self.execute(trigger.code, environment = {'args': args, 'kwargs': kwargs})
      except Exception as e:
       self.onError()
       self.outputStatus('Error in trigger: "%s".\n%s' % (trigger.title, str(e)))
     if trigger.stop:
      break
   if sub != None:
    (line, actual) = self._processLine(sub)
   elif self.outputSub != None:
    (line, actual) = self._processLine(self.outputSub)
    self.outputSub = None
   line = ''.join([x for x in actual if not isinstance(x, StyleObject)])
   g = self.gagged()
   lineOk = not self.config.get('output', 'gag') and (line or not self.config.get('output', 'suppressblanklines'))
   hw = hasattr(self.outputBuffer, 'write')
   ho = hasattr(self.outputBuffer, 'output')
   hasWrite = hw or ho
   if g['output']:
    self.gag(-1, 'output')
   elif lineOk:
    if ho:
     self.outputBuffer.output(actual)
    elif hw:
     self.outputBuffer.write(line + '\n')
    else:
     print line
    if log:
     self.logOutput(self.logSub if self.logSub != None else toBeLogged)
     self._output.append(line)
     self.logSub = None
   if log:
    if g['braille']:
     self.gag(-1, 'braille')
    elif lineOk and hasWrite:
     self.braille(line)
    if g['voice']:
     self.gag(-1, 'voice')
    elif lineOk and hasWrite:
     self.speak(line)
 
 def outputStatus(self, line):
  """
  Output a line prepended by the current time stamp.
  
  """
  for l in line.strip('\r\n').split('\n'):
   self.output('%s: %s' % (ctime(), l), 0)
 
 def send(self, command, process = None, log = True):
  """
  send(command[, process[, log]])
  
  Send a command to the MUD.
  
  * If process is True, check for aliases first.
  * If log is True, log the command.
  
  """
  if type(command) not in [unicode, str]:
   raise TypeError('Can only send strings.')
  self.onSend()
  if log:
   self.logCommand(command)
  if self.config.get('entry', 'echocommands'):
   self.output(command, process = False, log = False)
  h = self.config.get('entry', 'helpchar')
  if h and command.startswith(h):
   command = command.replace(h, '').strip()
   if command:
    try:
     command = eval(command, self.getEnvironment())
    except Exception as e:
     self.output(e, process = False)
    self.help(command)
   else:
    g = self.getEnvironment().keys()
    return self.output('Try to get help on the following globals: %s and %s.' % (', '.join(g[:-1]), g[-1]), process = False)
  else:
   if process == None:
    if command and command[0] == self.config.get('scripting', 'bypasscharacter'):
     process = False
     command = command[1:]
    else:
     process = self.config.get('entry', 'processaliases')
   if command and process:
    cc = self.commandChar
    if command.startswith(cc) and self.config.get('scripting', 'enable'):
     return self.execute(self.normalise(command[1:]))
    vre = self.variableRe
    sre = self.statementRe
    if self.config.get('scripting', 'expandvariables') and vre:
     e = self.getEnvironment()
     for t, v in vre.findall(command):
      if v in e:
       command = command.replace(t, str(e[v]))
    if self.config.get('scripting', 'expandstatements') and sre:
     for t, s in sre.findall(command):
      command = command.replace(t, unicode(eval(s, e)))
    command = command.split(self.config.get('entry', 'commandsep'))
   else:
    command = [command]
   for c in command:
    self.commandQueue.append(c)
 
 def _send(self, command):
  self._commandInterval = time()
  for alias in self.aliases.itervalues():
   m = self.matchSource(command, alias)
   if m:
    self.onAlias()
    (alias, args, kwargs) = m
    args = list(args)
    args.insert(0, command)
    if alias.simple:
     command = self.formatSimple(alias.code, args)
    else:
     try:
      return self.execute(alias.code, environment = {'args': args})
     except Exception as e:
      return self.outputStatus('Error in alias %s: %s.' % (alias.title, e)) 
    break
  self.writeToCon(command)
 
 def writeToCon(self, line):
  """
  writeToCon(line)
  
  Writes line directly to the telnet connection.
  
  * line is the line to write to the connection.
  
  """
  if not self.connected:
   raise UserError(errors['NotConnectedYet'])
  else:
   self.con.write(self.normalise(line) + '\n')
 
 def writeToLog(self, type, line):
  """
  writeToLog(type, line)
  
  Generic logging system. Dumps to disc every so often, depending on your log interval setting.
  
  * type is a string describing the type of log entry this is.
  * line is the line which should be ogged.
  
  """
  self._log.append((type, time(), line))
  if len(self._log[self._logIndex:]) >= self.config.get('logging', 'loginterval'):
   self.logFlush()
   return True
  return False
 
 def logFlush(self):
  l = os.path.join(self.directory, self.config.get('logging', 'logdirectory'))
  if os.path.isdir(l):
   b = u''
   for entryType, entryTime, entryLine in self._log[self._logIndex:]:
    b += '[%s (%s)] (%s) %s\n' % (ctime(entryTime), entryTime, entryType, entryLine)
   with open(os.path.join(l, self.logFile), 'a') as f:
    f.write(b.encode(self.config.get('logging', 'logencoding')))
    self._logIndex = len(self._log)
 
 def execute(self, code, environment = dict()):
  """
  execute(code[, environment])
  
  Executes code, giving environment as globals.
  
  Environment defaults to an empty dictionary, and is added to the overall environment for execution.
  
  If this function is called as a result of a trigger or alias, args will be given as c style args, where the full command is args[0], and all subsequent arguments are located in positions 1 to n.
  
  """
  if not self.config.get('scripting', 'enable') and type(code) == str:
   self.send(code, log = False)
  else:
   if type(code) == str:
    c = compile(code, 'errors.log', 'exec')
   else:
    c = code
   eval(c, self.getEnvironment(environment))

 def logCommand(self, command):
  """
  logCommand(command)
  
  Adds a command to the command log.
  
  * command is the command to be logged.
  """
  if self.gagged()['entry']:
   self.gag(-1, 'entry')
  else:
   c = self.getCommands()
   if not c or c[-1] != command or self.config.get('entry', 'logduplicatecommands'):
    self.writeToLog('command', command)

 def getCommands(self):
  """
  getCommands()
  
  Returns the command log.
  
  """
  return [z for x, y, z in self._log if x == 'command']

 def logOutput(self, line):
  """
  logOutput(line)
  
  Adds lines to the output log.
  
  * line is the line to be added to the output.
  
  """
  self.writeToLog('output', line)

 def getOutput(self):
  """
  getOutput()
  
  Returns the real output log with all gags and substitutions, rather than the raw representation maintained by outputLog.
  
  """
  return self._output
 
 def substitute(self, line, system = 'output'):
  """
  substitute(line[, system])
  
  Used in combination with addTrigger to replace lines of text in system.
  
  * line is the line to replace the actual line with.
  * system is either 'output' (the output window') or 'log' (the output log).
  
  """
  if type(line) not in (str, unicode):
   line = str(line)
  setattr(self, '%sSub' % system, line)

 def gag(self, number = 1, system = 'all'):
  """
  gag([number[, system]])
  
  Gags number lines from being sent through system.
  
  * If system is a list, work through all the values.
  * Number defaults to 1, and system defaults to 'output'.
  
  The possible values for system are: entry, output, braille, voice and all.
  
  """
  if system == 'all':
   system = self._gag.keys()
   system.remove('entry')
  else:
   if type(system) != list:
    system = [str(system)]
  for x in system:
   if x in self._gag:
    self._gag[x] += number
   else:
    raise KeyError('No gagging system %s.' % x)

 def ungag(self, system = 'all'):
  """
  ungag([system])
  
  Turns gagging off for the specified system(s).
  
  * If system is given as a list, work through the list ungagging all systems. See the help for gag for a list of the possible system values.
  
  """
  if system == 'all':
   system = self._gag.keys()
  else:
   if type(system) != list:
    system = [str(system)]
  for x in system:
   if x in self._gag:
    self._gag[x] = 0
   else:
    raise KeyError('No gagging system %s.' % x)

 def gagged(self):
  """
  Returns what systems are gagged.
  
  """
  return self._gag

 def playSound(self, filename, volume = 0.0, pan = 0.0, frequency = 44100, looping = False, play = True):
  """
  playSound(filename[, volume[, pan[, frequency[, looping[, play]]]]])
  
  Plays a sound with the specified parameters.
  
  * filename is the full or relative path the the file to be played.
  * volume is relative volume, given as a floating point number and defaults to 1.0 (full).
  * pan is relative pan, given as a floating point number and defaults to 0.0.
  * frequency is the frequency given in hz and defaults to 44100.
  * looping is a boolean value which tells the sound to either play continuously, or only play once and defaults to False.
  * play is a boolean telling the function to play the sound straight away, or simply return it, leaving it up to the user to play at some later time and defaults to Trye.
  
  """
  m = re.match(self.soundRe, filename)
  if m:
   g = m.groups()[1]
   filename = filename.replace(g, str(int(int(g.strip('*')) * self.random.random()) + 1))
  try:
   s = stream.FileStream(file = filename)
  except BassError as e:
   raise BassError(e.code, 'Error playing file %s: %s.' % (filename, str(e)))
  v = self.baseVolume + volume
  if v < 0.0:
   v = 0.0
  elif v > 1.0:
   v = 1.0
  s.set_volume(v)
  p = 0.0 + pan
  if p > 1.0:
   p = 1.0
  elif p < -1.0:
   p = -1.0
  s.set_pan(p)
  s.set_frequency(frequency)
  s.set_looping(looping)
  if play:
   threading.Thread(name = 'Sound Player', target = s.play_blocking).start()
  return s

 def getEnvironment(self, environment = {}):
  """
  getEnvironment([environment]
  
  Gets the environment for execute and other tasks.
  
  * environment is a dictionary to add to the over all environment, and defaults to an empty dictionary.
  
  """
  e = dict(environment, **self.environment)
  e.update(locals(), **globals())
  for x in dir(self):
   if not x.startswith('_'):
    e[x] = getattr(self, x)
  return e

 def formatCode(self, code):
  """
  formatCode(code)
  
  Given multi line code, strips the first level of indent, preparing it for compilation.
  
  * code is the code to be modified.
  
  """
  m = self.codeRe.match(code)
  if m:
   return code.replace('\n%s' % m.groups()[0], '\n')
  return code

 def matchClasses(self, probable, actual = None):
  """
  matchClasses(probable[, actula])
  
  Match the probable triggers against the actual classes provided.
  
  * probably is the classes to be tested.
  * actual is the actual classes loaded, and defaults to those currently active on the world.
  
  """
  if actual == None:
   actual = self.classes
  return not probable or len([x for x in probable if x in actual]) == len(probable)

 def formatSimple(self, text, groups):
  for r in range(0, len(groups)):
   text = text.replace('%%%s' % r, groups[r])
  return text

 def classToggle(self, c, state = None):
  """
  classToggle(class[, state])
  
  Adds or removes a class from the list of currently active classes.
  
  * class is the class name.
  * state is True or False, based on whether or not you want the class to be active or not, and defaults to the oposite state.
  
  """
  if state == None:
   state = not c in self.classes
  if state == False and c in self.classes:
   self.classes.remove(c)
  elif state == True and c not in self.classes:
   self.classes.append(c)
 
 def matchSource(self, line, thing):
  """
  matchSource(line, thing)
  
  Attempt to match line to thing.
  
  * line is the line of text to match.
  * thing is the source to match line against.
  
  """
  m = thing.pattern.match(line)
  if m and self.matchClasses(thing.classes):
   return (thing, m.groups(), m.groupdict())
 
 def _close(self):
  self.con = None # Reset the connection to it's default state.
  self._outputThread.cancel()
  self.soundOutput.stop()
 
 def help(self, thing = None):
  """
  help([thing])
  
  Gets help on thing.
  
  * Thing defaults to the world object, and prints information similar to Python's built-in help system.
  
  """
  if thing == None:
   thing = self
  d = getdoc(thing)
  if d:
   print d
  else:
   print 'No documentation for %s.' % thing
   return
  if not callable(thing) and issubclass(type(thing), object):
   print '\n'
   functions = []
   properties = []
   for x in dir(thing):
    if not x.startswith('_'):
     if callable(getattr(thing, x)):
      functions.append(x)
     else:
      properties.append(x)
   if functions:
    if len(functions) > 1:
     functions = '%s and %s' % (', '.join(functions[:-1]), functions[-1])
    else:
     functions = functions[0]
   else: 
    functions = 'None'
   print 'Functions of %s: %s.' % (type(thing), functions)
   if properties:
    if len(properties) > 1:
     properties = '%s and %s' % (', '.join(properties[:-1]), properties[-1])
    else:
     properties = properties[0]
   else:
    properties = 'None'
   print 'Properties of %s: %s.' % (type(thing), properties)
 
 def _processLine(self, line):
  """Process line ready for output."""
  actual = []
  i = 0 # Where we're at in the list.
  for chunk in re.split(self.colourRe, line):
   if not i: # Chunk is to be printed.
    actual.append(chunk)
   elif i == 1: #This is the colour string to be replaced.
    line = line.replace(chunk, '')
   elif i == 2: # This is the bit which tells us which colour is needed.
    i = -1 # Increment will set it to 0.
    pc = self.config.get('accessibility', 'printcolours')
    for c in chunk.split(';'):
     if c == '0': # Reset!
      (fg, bg) = self.colours['0']
      actual.append(StyleObject(foreground = fg, background = bg, bold = False, italics = False, underline = False, strikethrough = False, blink = False))
      if pc:
       actual.append('<reset>')
     elif c in self.colours: # Found the colour.
      (fg, bg) = self.colours[c]
      text = ''
      if fg:
       self._fg = fg
       text = '%s text' % fg
      if bg:
       self._bg = bg
       text += '%s%s background' % (' on a ' if text else '', bg)
      actual.append(StyleObject(foreground = fg, background = bg))
      if pc: # Print colours to the output window.
       actual.append('<%s>' % text)
     elif chunk in ['7', '27']: # Inverse on and off...
      (fg, bg) = (self._fg, self._bg)
      actual.append(StyleObject(foreground = bg, background = fg))
      if pc:
       actual.append('<%s>' % 'inverse' if chunk == '7' else '/inverse')
     elif chunk in self.styles:
      s, v = self.styles[chunk]
      o = StyleObject()
      setattr(o, s, v)
      actual.append(o)
      if pc:
       actual.append('<%s%s>' % ('' if v else '/', s))
     else:
      if self.config.get('output', 'printunrecognisedformatters'):
       actual.append('<Unrecognised: %s>' % chunk)
   i += 1
  return (line, actual)
 
 def speak(self, *args, **kwargs):
  """Speak arguments if speech is enabled on the world."""
  if self.config.get('accessibility', 'speak'):
   t = threading.Thread(name = 'Speech thread', target = accessibility.system.speak, args = args, kwargs = kwargs)
   t.start()
   return t
  else:
   return False
 
 def braille(self, *args, **kwargs):
  """Brailles arguments if brailling is enabled on the world."""
  if self.config.get('accessibility', 'braille'):
   t = threading.Thread(name = 'Braille thread', target = accessibility.system.braille, args = args, kwargs = kwargs)
   t.start()
   return t
  else:
   return False
 
 def _validFile(self, filename):
  if not os.path.exists(filename):
   raise IOError('File %s does not exist.' % filename)
  else:
   return True

class ErrorBuffer(object):
 """A buffer for catching errors."""
 def __init__(self, func, args, kwargs):
  """Func is the function to pass the error text onto, with args and kwargs."""
  self.func = func
  self.args = args
  self.kwargs = kwargs
  self.beepInterval = 1.0
  self._lastBeepTime = 0.0
  self.beepFunc = lambda: None
 
 def write(self, text = None):
  t = time()
  if t - self._lastBeepTime >= self.beepInterval:
   self.beepFunc()
   self._lastBeepTime = t
  if text:
   return self.func(text, *self.args, **self.kwargs)

class StyleObject(object):
 """a platform independant way to pass colour and style information to the front end."""
 def __init__(self, foreground = None, background = None, bold = None, italics = None, underline = None, strikethrough = None, blink = None):
  self.foreground = foreground
  self.background = background
  self.bold = bold
  self.italics = italics
  self.underline = underline
  self.strikethrough = strikethrough
  self.blink = blink

class OutputThread(threading.Thread):
 """The output thread, cancelable."""
 def __init__(self, *args, **kwargs):
  self._cancel = threading.Event()
  super(OutputThread, self).__init__(*args, **kwargs)
 
 def cancel(self):
  self._cancel.set()
 
 def shouldStop(self):
  return self._cancel.isSet()
