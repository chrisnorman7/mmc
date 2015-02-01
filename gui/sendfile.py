import wx, os, re
import wx.lib.sized_controls as sc
from wx.lib.filebrowsebutton import FileBrowseButton

class SendFileFrame(sc.SizedFrame):
 """File sending options."""
 def __init__(self, callback, filename = '', prefix = '', suffix = '', linesep = '\n', preline = '', postline = '', ignore = ''):
  super(SendFileFrame, self).__init__(None, title = 'Send File')
  self.callback = callback
  s = wx.TE_RICH|wx.TE_MULTILINE
  p = self.GetContentsPane()
  p.SetSizerType('form')
  wx.StaticText(p, label = '&File name')
  self.filename = FileBrowseButton(p)
  self.filename.SetValue(filename)
  wx.StaticText(p, label = 'Text to &prefix the file with')
  self.prefix = wx.TextCtrl(p, value = prefix, style = s)
  wx.StaticText(p, label = 'Text to p&refix each line with')
  self.preLine = wx.TextCtrl(p, value = preline, style = s)
  wx.StaticText(p, label = 'Text to s&uffix each line with')
  self.postLine = wx.TextCtrl(p, value = postline, style = s)
  wx.StaticText(p, label = 'Line &seperator')
  self.linesep = wx.TextCtrl(p, value = linesep, style = s)
  wx.StaticText(p, label = 'Text to &suffix the file with')
  self.suffix = wx.TextCtrl(p, value = suffix, style = s)
  wx.StaticText(p, label = 'Text to &ignore')
  self.ignore = wx.TextCtrl(p, value = ignore)
  self.cancel = wx.Button(p, label = '&Cancel')
  self.cancel.Bind(wx.EVT_BUTTON, lambda event: self.Close(True))
  self.ok = wx.Button(p, label = '&OK')
  self.ok.Bind(wx.EVT_BUTTON, self.onOk)
  self.ok.SetDefault()
  self.Maximize(True)
 
 def onOk(self, event):
  """Sends the stuff using callback."""
  f = self.filename.GetValue()
  if not os.path.isfile(f):
   return wx.MessageBox('No such file: %s.' % f, 'Error', style = wx.ICON_ERROR)
  c = self.prefix.GetValue()
  if self.ignore.GetValue():
   m = re.compile(self.ignore.GetValue())
  else:
   m = None
  with open(f, 'r') as f:
   for line in f:
    line = line[:-1]
    if not m or not m.match(line):
     c+= '%s%s%s%s' % (self.preLine.GetValue(), line, self.postLine.GetValue(), self.linesep.GetValue())
  self.callback(c + self.suffix.GetValue())
  self.Close(True)
