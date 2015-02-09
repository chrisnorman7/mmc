"""The gui part of the worlds framework."""

import wx, world, sys, accessibility, application, editor, re, threading, os, sendfile, webbrowser, finder, logparser
from gui import MyGui
from errors import *
from time import sleep, time

class EntryCtrl(wx.TextCtrl):
 """The text control used for the entry line."""
 def Insert(self, text, pos = None, track = True):
  """Insert text at position pos. Move insertion point if track == True, and insertion point >= insertion point."""
  i = self.GetInsertionPoint()
  if pos == None:
   pos = i
  v = self.GetValue()
  self.SetValue(v[0:i] + text + v[i:])
  if track and pos >= i:
   self.SetInsertionPoint(i + len(text))

class OutputCtrl(wx.TextCtrl):
 """The text control used for the output window."""
 def write(self, text):
  wx.CallAfter(super(OutputCtrl, self).write, text)

class WorldFrame(MyGui.Frame):
 """Main window object."""
 @property # The output position.
 def outputPos(self):
  return self._outputPos[1]
 
 @outputPos.setter
 def outputPos(self, value):
  l = len(self.world.getOutput())
  if value < 0:
   value = 0
   wx.Bell()
  elif value >= l:
   wx.Bell()
   value = l - 1
  if value != self.outputPos:
   self._reviewKeyPresses = 0
   self._outputPos[1] = value
  else:
   self._reviewKeyPresses += 1
 
 def __init__(self, filename = None):
  """Initialise the window. If filename is provided, create a world too using :func:`gui.gui.WorldFrame.init`."""
  if sys.platform == 'darwin':
   self.ALT = wx.ACCEL_CMD
   self.CTRL = wx.ACCEL_RAW_CTRL
  else:
   self.ALT = wx.ACCEL_ALT
   self.CTRL = wx.ACCEL_CTRL
  self._outputPos = [time(), 0]
  self._reviewKeyPresses = 0
  self.reviewKeySpeed = 0.25
  super(WorldFrame, self).__init__(None)
  self.path = filename
  self.world = None
  self.panel = wx.Panel(self)
  s = wx.BoxSizer(wx.VERTICAL)
  if self.path == None:
   l = wx.StaticText(self.panel, label = 'Open an existing world with {ctrl}+O or create a new one with {ctrl}+N to begin.'.format(ctrl = 'CMD' if sys.platform == 'darwin' else 'CTRL'), size = (200, 800))
   l.SetFocus()
   s.Add(l, 1, wx.GROW)
   self.SetTitle('(V%s)' % application.appVersion)
   if len(sys.argv) > 1:
    for a in sys.argv[1:]:
     self.open(None, a)
  else:
   self.output = OutputCtrl(self.panel, style = wx.TE_MULTILINE|wx.TE_RICH|wx.TE_READONLY)
   #self.panel.Bind(wx.EVT_SET_FOCUS, lambda event: self.world.onFocus(True))
   #self.panel.Bind(wx.EVT_KILL_FOCUS, lambda event: self.world.onFocus(False))
   self.output.Bind(wx.EVT_CHAR, self.outputHook)
   s1 = wx.BoxSizer(wx.HORIZONTAL)
   self.prompt = wx.StaticText(self.panel)
   self.entry = EntryCtrl(self.panel, style = wx.TE_RICH|wx.TE_MULTILINE, size = (1100, 200))
   self.commandIndex = 0
   wx.EVT_KEY_DOWN(self.entry, self.keyParser)
   #self.entry.Bind(wx.EVT_TEXT_ENTER, self.onEnter)
   self.entry.SetFocus()
   s1.Add(self.prompt, 1, wx.EXPAND)
   s1.Add(self.entry, 1, wx.EXPAND)
   s.Add(self.output, 1, wx.EXPAND)
   s.Add(s1, 0, wx.EXPAND)
   self.Bind(wx.EVT_CLOSE, self.onClose)
  self.panel.SetSizerAndFit(s)
  mb = wx.MenuBar()
  self.fileMenu = wx.Menu()
  self.Bind(wx.EVT_MENU, self.new, self.fileMenu.Append(wx.ID_NEW, '&New\tCTRL+N', 'Load a new blank world'))
  self.Bind(wx.EVT_MENU, self.open, self.fileMenu.Append(wx.ID_OPEN, '&Open...\tCTRL+O', 'Open a new world'))
  if self.path != None:
   self.fileMenu.AppendSeparator()
   self.Bind(wx.EVT_MENU, self.save, self.fileMenu.Append(wx.ID_SAVE, '&Save\tCTRL+S', 'Save the current world'))
   self.Bind(wx.EVT_MENU, self.saveAs, self.fileMenu.Append(wx.ID_SAVEAS, 'S&ave As...\tCTRL+SHIFT+S', 'Save the world with a new name'))
  self.fileMenu.AppendSeparator()
  self.Bind(wx.EVT_MENU, lambda event: self.Close(True), self.fileMenu.Append(wx.ID_EXIT, 'E&xit', 'Close the program'))
  mb.Append(self.fileMenu, '&File')
  self.sendMenu = wx.Menu()
  self.Bind(wx.EVT_MENU, self.onSendFile, self.sendMenu.Append(wx.ID_ANY, 'Send &File', 'Send a file to the world'))
  self.Bind(wx.EVT_MENU, self.onSendLog, self.sendMenu.Append(wx.ID_ANY, 'Send &Log', 'Send a log file for review'))
  mb.Append(self.sendMenu, '&Send')
  self.connectionMenu = wx.Menu()
  mb.Append(self.connectionMenu, '&Connection')
  self.programmingMenu = wx.Menu()
  mb.Append(self.programmingMenu, '&Programming')
  self.optionsMenu = wx.Menu()
  self.Bind(wx.EVT_MENU, self.selectOutput, self.optionsMenu.Append(wx.ID_ANY, '&Select sound output...', 'Select a device to play sounds through'))
  mb.Append(self.optionsMenu, '&Options')
  self.helpMenu = wx.Menu()
  self.Bind(wx.EVT_MENU, self.onHelp, self.helpMenu.Append(wx.ID_HELP, '&Program Documentation%s' % '\tF1' if sys.platform.startswith('win') else '', 'Get help on using the program'))
  self.Bind(wx.EVT_MENU, lambda event: wx.AboutBox(application.appInfo), self.helpMenu.Append(wx.ID_ABOUT, '&About...', 'About the program'))
  mb.Append(self.helpMenu, '&Help')
  self.SetMenuBar(mb)
  self.Maximize(True)
  self.Show(True)
  self.init()
 
 def SetTitle(self, value):
  """Adds the application name to title."""
  return super(WorldFrame, self).SetTitle('%s - %s' % (application.appName, value))
 
 def new(self, event = None):
  """Creates a new window and world combination."""
  w = WorldFrame('')
  w.world.config.get_gui().Show(True)
  if not self.world:
   self.Close(True)
 
 def open(self, event = None, path = ''):
  """Open a new world."""
  if not path:
   dlg = wx.FileDialog(self, 'Select a world to open', style = wx.FD_OPEN)
   if dlg.ShowModal() == wx.ID_OK:
    path = dlg.GetPath()
   else:
    path = None
   dlg.Destroy()
  if path != None:
   w = None
   WorldFrame(path)
   if not self.world:
    self.Close(True)
 
 def save(self, event = None):
  """Save the current world."""
  w = self.world
  if not w.filename:
   self.saveAs()
  else:
   w.save()
 
 def saveAs(self, event = None):
  """Save the current world under a new name."""
  w = self.world
  dlg = wx.FileDialog(self, 'Save as', '', w.filename if w.filename else w.config.get('world', 'name') + world.fileext, style = wx.FD_SAVE)
  while dlg.ShowModal() != wx.ID_CANCEL:
   w.filename = dlg.GetPath()
   if not os.path.isfile(w.filename) or wx.MessageBox('Do you want to replace %s?' % w.filename, 'File exists', style = wx.YES_NO) == wx.YES:
    return w.save()
   else:
    w.filename = ''
 
 def onClose(self, event):
  """Code to be run before the window is closed for good."""
  w = self.world
  if w:
   if w.connected and wx.MessageBox('This world is still connected. Really close it?', 'Close the world', style = wx.YES_NO) == wx.NO:
    return
   try:
    if w.connected:
     w.close()
    if w.config.getboolean('world', 'autosave'):
     self.save() if w.filename else self.saveAs()
   except UserError as e:
    return wx.MessageBox(str(e), 'Error')
  event.Skip()
 
 def updateFunc(self, world, section, option, value):
  """
  Acts as the callback for :ref:`world-options`.
  
  To add more instructions, add them to the updateInstructions dictionary on this window. For example:
  
  self.updateInstructions['world']['name'] = lambda value: self.SetTitle(value)
  
  """
  try:
   self.updateInstructions[section][option](value)
  except KeyError:
   pass # There was no instruction found.
 
 def onEnter(self, event = None, clear = True):
  """Enter was pressed, handle commands from the entry line."""
  v = self.entry.GetValue()
  i = self.entry.GetInsertionPoint()
  if i < len(v):
   v = v[0:i - 1] + v[i:]
  if v and v[-1] == '\n':
   v = v[:-1]
  if clear:
   self.entry.Clear()
  self.commandIndex = 0
  try:
   self.world.send(v)
  except UserError:
   if wx.MessageBox('Do you want to connect this world?', 'World not connected', style = wx.YES_NO) == wx.YES:
    self.openWorld()
 
 def keyParser(self, event):
  """Process any keys pressed while the entry line has focused."""
  kc = event.GetKeyCode()
  km = event.GetModifiers()
  if km in [wx.ACCEL_NORMAL, wx.ACCEL_SHIFT] and kc == wx.WXK_RETURN:
   return self.onEnter(None, not km == wx.ACCEL_SHIFT)
  if not km:
   if kc in (wx.WXK_UP, wx.WXK_DOWN):
    e = self.entry.GetValue()
    l = 0 # No logging has been performed.
    g = self.world.getCommands()
    if not self.commandIndex and e and g and g[-1] != e:
     self.world.logCommand(e)
     l = 1
    if kc == wx.WXK_UP:
     self.commandIndex -= 1
    else:
     self.commandIndex += 1
    if not self.commandIndex:
     self.entry.Clear()
    elif self.commandIndex > 0:
     self.entry.Clear()
     wx.Bell()
     self.commandIndex = 0
    else:
     try:
      self.entry.SetValue(g[self.commandIndex])
      self.commandIndex -= l
      self.entry.SetInsertionPoint(len(self.entry.GetValue()))
     except IndexError:
      wx.Bell()
      self.commandIndex = len(self.world.getCommands()) * -1
    return
   elif kc == wx.WXK_ESCAPE:
    if self.world.config.getboolean('entry', 'escapeclearsentry'):
     return self.entry.Clear()
  event.Skip()
 
 def speakLine(self, pos = None):
  """Speak lines provided by :func:`world.World.getOutput`."""
  pos = self.outputPos if pos == None else pos
  self.outputPos = pos
  try:
   text = self.world.getOutput()[pos]
  except IndexError:
   text = 'No text.'
  if (time() - self._outputPos[0]) < self.reviewKeySpeed and self._reviewKeyPresses:
   if self._reviewKeyPresses >= 2:
    self._reviewKeyPresses = 0
    self.entry.Insert(text)
    text = 'Pasted.'
   elif self._reviewKeyPresses >= 1:
    d = wx.TextDataObject()
    d.SetText(text)
    wx.TheClipboard.Open() # Take command of the clipboard.
    wx.TheClipboard.SetData(d)
    wx.TheClipboard.Close()
    text = 'Coppied: %s' % text
  else:
   self._reviewKeyPresses = 0
  self._outputPos[0] = time()
  
  if self.world.config.getboolean('accessibility', 'speak'):
   accessibility.system.speak(text, True)
  if self.world.config.getboolean('accessibility', 'braille'):
   accessibility.system.braille(text)
 
 def addAlias(self, event = None):
  """The GUI front end to :func:`world.World.addAlias`."""
  editor.AliasFrame(add = self.world.addAlias).Show(True)
 
 def editAliases(self, event = None):
  """Edit aliases in a GUI."""
  dlg = wx.SingleChoiceDialog(None, 'Edit aliases', 'Choose an alias to edit', [a.title for a in self.world.aliases.values()])
  res = dlg.ShowModal()
  if res == wx.ID_OK:
   alias = self.world.aliases.values()[dlg.GetSelection()]
   editor.AliasFrame(alias = alias.pattern.pattern, code = getattr(alias, '_code'), classes = alias.classes, title = alias.title, simple = alias.simple, add = self.world.addAlias, remove = self.world.removeAlias).Show(True)
  dlg.Destroy()
 
 def addTrigger(self, event = None):
  """The GUI front end for :func:`world.World.addTrigger`."""
  editor.TriggerFrame(add = self.world.addTrigger).Show(True)
 
 def editTriggers(self, event = None):
  """Edit triggers in a GUI."""
  triggers = self.world.literalTriggers.values() + self.world.triggers.values()
  dlg = wx.SingleChoiceDialog(None, 'Edit triggers', 'Choose a trigger to edit', [t.title for t in triggers])
  res = dlg.ShowModal()
  if res == wx.ID_OK:
   trigger = triggers[dlg.GetSelection()]
   editor.TriggerFrame(trigger = trigger.pattern if type(trigger.pattern) in [unicode, str] else trigger.pattern.pattern, code = getattr(trigger, '_code'), classes = trigger.classes, regexp = trigger.regexp, simple = trigger.simple, stop = trigger.stop, title = trigger.title, add = self.world.addTrigger, remove = self.world.removeTrigger).Show(True)
  dlg.Destroy()
 
 def init(self):
  """Add a world to the window, and get it ready for action."""
  if self.world != None or self.path == None:
   return
  self.Bind(wx.EVT_MENU, self.openWorld, self.connectionMenu.Append(wx.ID_ANY, '&Open Connection\tCTRL+K', 'Open the connection to the world'))
  self.Bind(wx.EVT_MENU, lambda event: self.world.close(), self.connectionMenu.Append(wx.ID_ANY, '&Close connection\tCTRL+SHIFT+K', 'Close the world connection'))
  self.Bind(wx.EVT_MENU, self.addAlias, self.programmingMenu.Append(wx.ID_ANY, '&Add alias...', 'Add an alias to the world'))
  self.Bind(wx.EVT_MENU, self.editAliases, self.programmingMenu.Append(wx.ID_ANY, '&Edit aliases...\tCTRL+SHIFT+A', 'Edit the aliases for the world'))
  self.Bind(wx.EVT_MENU, self.addTrigger, self.programmingMenu.Append(wx.ID_ANY, '&Add trigger...', 'Add a trigger to the world'))
  self.Bind(wx.EVT_MENU, self.editTriggers, self.programmingMenu.Append(wx.ID_ANY, '&Edit Triggers...\tCTRL+SHIFT+T', 'Edit triggers for the world'))
  self.Bind(wx.EVT_MENU, lambda event: self.world.config.get_gui().Show(True), self.optionsMenu.Append(wx.ID_ANY, '&World options...\tF12', 'View and edit the configuration for the current world'))
  self.Bind(wx.EVT_MENU, lambda event: self.world.commandQueue.clear(), self.optionsMenu.Append(wx.ID_ANY, '&Clear Command Queue', 'Clear the command queue'))
  self.AddAccelerator(self.CTRL|wx.ACCEL_SHIFT, ord('i'), lambda event: self.speakLine(self.outputPos))
  self.AddAccelerator(self.CTRL|wx.ACCEL_SHIFT, ord('u'), lambda event: self.speakLine(self.outputPos - 1))
  self.AddAccelerator(self.CTRL|wx.ACCEL_SHIFT, ord('o'), lambda event: self.speakLine(self.outputPos + 1))
  self.AddAccelerator(self.CTRL|wx.ACCEL_SHIFT, ord('p'), lambda event: self.speakLine(len(self.world.getOutput()) - 1))
  self.AddAccelerator(self.CTRL|wx.ACCEL_SHIFT, ord('y'), lambda event: self.speakLine(0))
  for i in range(0, 10):
   self.AddAccelerator(self.ALT, ord(str(i)), lambda event, i = 10 if i == 0 else i: self.speakLine(len(self.world.getOutput()) - i))
  self.AddAccelerator(wx.ACCEL_NORMAL, wx.WXK_F2, lambda event: self.world.config.toggle('sounds', 'mastermute'))
  self.AddAccelerator(wx.ACCEL_NORMAL, wx.WXK_F3, lambda event: self.adjustVolume(-1.0))
  self.AddAccelerator(wx.ACCEL_NORMAL, wx.WXK_F4, lambda event: self.adjustVolume(1.0))
  try:
   self.world = world.World(self.path)
   sys.stdout = self.world
   self.world.onFocus = lambda value: None
  except Exception as e:
   wx.MessageBox(str(e), 'Problem with world file')
   return self.Close(True)
  self.world.outputBuffer = self.output
  self.world.environment['window'] = self
  self.world.environment['application'] = application
  self.world.environment['find'] = finder.find
  self.prompt.SetLabel(self.world.config.get('entry', 'prompt'))
  self.world.config.updateFunc = self.updateFunc
  self.updateInstructions = {
   'world': {
    'name': lambda value: self.SetTitle(value)
   },
   'entry': {
    'prompt': lambda value: self.prompt.SetLabel(value)
   },
   'sounds': {
    'mastervolume': lambda value: self.world.soundOutput.set_volume(float(value)),
    'mastermute': lambda value: self.world.soundOutput.set_volume(0.0 if bool(value) else self.world.config.getfloat('sounds', 'mastervolume'))
   }
  }
  self.SetTitle(self.world.name)
  if self.world.config.getboolean('connection', 'autoconnect') and self.world.hostname and not self.world.invalidPort(self.world.port):
   self.openWorld()
 
 def outputHook(self, event):
  """Move the user to the entry line, and have whatever key they pressed added to their command."""
  kc = event.GetKeyCode()
  if kc >= 32 and kc <= 126:
   self.entry.Insert(chr(kc))
   self.entry.SetFocus()
  else:
   event.Skip()
 
 def selectOutput(self, event = None):
  """Selects a new audio output."""
  o = self.world.soundOutput
  p = getattr(o, '__class__')
  dlg = wx.SingleChoiceDialog(self, 'Select Output Device', 'Select an output device from the list', o.get_device_names())
  if dlg.ShowModal():
   o.free()
   self.world.soundOutput = p(device = dlg.GetSelection() + 1)
  dlg.Destroy()
 
 def openWorld(self, event = None):
  """Open the world's connection. Do it in a new thread so it doesn't block."""
  threading.Thread(name = 'World opener', target = self._openWorld).start()
 
 def _openWorld(self):
  """Backend for :func:`gui.worldframe.WorldFrame.openWorld`."""
  try:
   self.world.open()
  except Exception as e:
   wx.MessageBox(str(e), 'Error')
 
 def onSendFile(self, event = None):
  """Send a file to the world."""
  wx.CallAfter(sendfile.SendFileFrame(self.world.send, linesep = self.world.config.get('entry', 'commandsep')).Show, True)
 
 def onSendLog(self, event):
  s = logparser.LogParserFrame(self.world)
  wx.CallAfter(s.Show, True)
 
 def adjustVolume(self, amount = 1.0):
  """Adjust the output volume by small amounts."""
  v = self.world.config.getfloat('sounds', 'mastervolume')
  v += amount
  if v < 0.0:
   v = 0.0
   wx.Bell()
  elif v > 100.0:
   v = 100.0
   wx.Bell()
  self.world.config.set('sounds', 'mastervolume', int(v))
  accessibility.system.speak('Volume set to %s.' % v)
 
 def onHelp(self, event = None):
  """Displays HTML help."""
  dir = 'docs'
  page = 'index.html'
  if not dir in os.listdir(application.appDirectory):
   dir = 'http://www.code-metropolis.com/mmc/docs/%s' % page
  else:
   dir = os.path.join(application.appDirectory, dir)
   if '_build' in os.listdir(dir):
    dir = os.path.join(dir, '_build', 'html', page)
   else:
    dir = os.path.join(dir, page)
  webbrowser.open(dir)
