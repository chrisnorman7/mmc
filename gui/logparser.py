"""Log parser for MMC."""
import re, wx, os, threading, time
from wx.lib.sized_controls import SizedFrame
from wx.lib.filebrowsebutton import FileBrowseButton

_expr = re.compile(r'^\[.+ \(([^)]+)\)\] \((.+)\) (.*)$')
logPrefix = '<<< Sending Log File >>>'
logSuffix = '<<< End of Log >>>'
progressTitle = 'Sending...'

class LogParserError(Exception):
 """Main error class."""
 def __init__(self, line, message):
  return super(LogParserError, self).__init__('Error on line %s: %s' % (line, message))

class LogParser(object):
 """
 A parsed log.
 
 Contains a list of (float time, str type, str line) lines to be output.
 
 Times are relative to each other, so can be queued up with time.sleep().
 
 LogParser(contents[, sep])
 
 * contents is the raw log data.
 * sep is the line seperator, and defaults to \\n.
 
 """
 def __init__(self, contents, sep = '\n'):
  self.contents = []
  self.timeOffset = 0.0 # The first time which is encountered.
  i = 0
  for line in contents.split(sep):
   i += 1
   if not line or line.startswith('#'):
    continue # Ignore blank and commented lines.
   m = _expr.match(line)
   if not m:
    raise LogParserError(i, 'Line does not conform to expected log format.')
   (time, type, line) = m.groups()
   try:
    time = float(time)
    if i == 1:
     # This is the first line, so add the offset.
     self.timeOffset = time
     time = 0.0
    else:
     # This isn't the first line, get a relative.
     time -= self.timeOffset
   except ValueError:
    raise LogParserException(i, 'Invalid time specification.')
   if time < 0.0:
    raise LogParserError(i, 'Line is out of cronological order.')
   self.contents.append((time, type, line))

class LogParserFrame(SizedFrame):
 """
 The frame to use with LogParser.
 
 LogParserFrame(world)
 
 * world is the world to send the entries too.
 
 """
 def __init__(self, world):
  super(LogParserFrame, self).__init__(None, title = 'Send Log')
  self.world = world
  p = self.GetContentsPane()
  p.SetSizerType('form')
  self.log = FileBrowseButton(p)
  self.log.SetLabel('Log &file to send')
  self.process = wx.CheckBox(p, label = '&Process resulting lines')
  self.process.SetValue(True)
  wx.StaticText(p, label = 'Send &before log')
  self.logPrefix = wx.TextCtrl(p, style = wx.TE_RICH, value = logPrefix)
  wx.StaticText(p, label = 'Send &after log')
  self.logSuffix = wx.TextCtrl(p, style = wx.TE_RICH, value = logSuffix)
  self.ok = wx.Button(p, label = '&OK')
  self.ok.Bind(wx.EVT_BUTTON, self.onOk)
  self.cancel = wx.Button(p, label = '&Cancel')
  self.cancel.Bind(wx.EVT_BUTTON, lambda event: self.Close(True))
  self.Maximize()
 
 def onOk(self, event):
  """Handle the form."""
  l = self.log.GetValue()
  if not os.path.isfile(l):
   return wx.MessageBox('You must supply a valid log file.', 'Error')
  with open(l, 'r') as f:
   s = f.read()
  try:
   p = LogParser(s)
  except LogParserError as e:
   return wx.MessageBox(str(e), 'Error in log file')
  prefix = self.logPrefix.GetValue()
  if prefix:
   lines = [(0.0, prefix)]
  else:
   lines = []
  lines += [(x, z) for x, y, z in p.contents if y == 'output']
  suffix = self.logSuffix.GetValue()
  if suffix:
   lines.append((lines[-1][0], suffix))
  LogParserProgress(lines, self.world, self.process.GetValue()).Show(True)
  self.Close(True)

class LogParserProgress(SizedFrame):
 """Sends the lines to the world and displays progress."""
 def __init__(self, lines, world, process):
  super(LogParserProgress, self).__init__(None, title = progressTitle)
  p = self.GetContentsPane()
  p.SetSizerType('form')
  self.thread = threading.Thread(name = 'Log Parser Thread', target = self._process)
  self.canceled = False
  self.lines = lines
  self.world = world
  self.pause = wx.CheckBox(p, label = 'P&ause')
  self.cancel = wx.Button(p, label = '&Cancel')
  self.cancel.Bind(wx.EVT_BUTTON, lambda event: setattr(self, 'canceled', True))
  self.label = wx.TextCtrl(p, style = wx.TE_RICH)
  self.process = wx.CheckBox(p, label = '&Process')
  self.process.SetValue(process)
  self.updateLabel(0)
  self.Maximize(False)
 
 def updateLabel(self, processed = 0):
  self.label.SetValue('Processing log file. Sent %s %s of %s.' % (processed, 'line' if processed == 1 else 'lines', len(self.lines)))
 
 def Show(self, *args):
  s = super(LogParserProgress, self).Show(*args)
  self.thread.start()
  return s
 
 def _process(self):
  start = time.time()
  processed = 0
  for l in self.lines:
   processed += 1
   (stamp, line) = l
   try:
    if self._send(start, stamp, line):
     break
   except Exception as e:
    return wx.MessageBox('Error sending line %s: %s' % (processed, str(e)), 'Error sending line')
   self.updateLabel(processed)
  self.Close(True)
 
 def _send(self, start, stamp, line):
  while True:
   if self.canceled:
    return True
   elif not self.pause.GetValue() and (time.time() - start) >= stamp:
    return self.world.output(line, self.process.GetValue())

if __name__ == '__main__':
 a = wx.App()
 class O(object):
  def output(self, line, process):
   print '%s (%s)' % (line, process)
 f = LogParserFrame(O())
 f.Show(True)
 a.MainLoop()
