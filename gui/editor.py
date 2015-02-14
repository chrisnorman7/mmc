import wx
import wx.lib.sized_controls as sc

class SourceFrame(sc.SizedFrame):
 """The frame from which all the editors are derived."""
 def __init__(self, title, simple):
  self.simple = simple
  self.type = 'source'
  super(SourceFrame, self).__init__(None, title = title)
  self.panel = self.GetContentsPane()
  self.panel.SetSizerType('form')
 
 def onOk(self, event = None):
  self.Close(True)
 
 def Show(self, state = True):
  s = self.simple
  self.simple = wx.CheckBox(self.panel, label = 'Se&nd commands not code')
  self.simple.SetValue(s)
  self.delete = wx.Button(self.panel, label = '&Delete')
  self.delete.Bind(wx.EVT_BUTTON, lambda event: self.remove(event) if wx.MessageBox('Are you sure you want to delete this %s?' % self.type, 'Confirm', style = wx.YES_NO) == wx.YES else None)
  self.cancelButton = wx.Button(self.panel, label = '&Cancel')
  self.cancelButton.Bind(wx.EVT_BUTTON, lambda event: self.Close(True))
  self.okButton = wx.Button(self.panel, label = '&OK')
  self.okButton.Bind(wx.EVT_BUTTON, self.onOk)
  self.okButton.SetDefault()
  super(SourceFrame, self).Show(state)
 
 def remove(self, event = None):
  if event:
   self.Close(True)

class AliasFrame(SourceFrame):
 def __init__(self, alias = '', code = '', classes = [], simple = False, title = None, add = None, remove = None):
  super(AliasFrame, self).__init__('Edit alias', simple = simple)
  self.type = 'alias'
  self.addFunc = add
  self.removeFunc = remove
  self.oldAlias = title
  wx.StaticText(self.panel, label = '&Alias')
  self.alias = wx.TextCtrl(self.panel, value = alias)
  wx.StaticText(self.panel, label = '&Send')
  self.code = wx.TextCtrl(self.panel, style = wx.TE_MULTILINE|wx.TE_RICH2, value = code)
  wx.StaticText(self.panel, label = 'C&lasses')
  self.classes = wx.TextCtrl(self.panel, value = ','.join(classes))
  wx.StaticText(self.panel, label = '&Title')
  self.title = wx.TextCtrl(self.panel, value = title or alias)
 
 def onOk(self, event):
  self.remove()
  try:
   self.addFunc(self.alias.GetValue(), self.code.GetValue(), classes = self.classes.GetValue().replace(', ', ',').split(',') if self.classes.GetValue() else [], simple = self.simple.GetValue(), title = self.title.GetValue() or self.alias.GetValue())
   super(AliasFrame, self).onOk()
  except Exception as e:
   wx.MessageBox(str(e), 'Error')
 
 def remove(self, event = None):
  self.removeFunc(self.oldAlias)
  super(AliasFrame, self).remove(event)


class TriggerFrame(SourceFrame):
 def __init__(self, trigger = '', code = '', classes = [], regexp = True, simple = False, stop = True, title = None, add = None, remove = None):
  super(TriggerFrame, self).__init__('Edit trigger', simple = simple)
  self.type = 'trigger'
  self.addFunc = add
  self.removeFunc = remove
  self.simple = simple
  self.oldTrigger = title
  wx.StaticText(self.panel, label = '&Trigger')
  self.trigger = wx.TextCtrl(self.panel, value = trigger)
  wx.StaticText(self.panel, label = '&Send')
  self.code = wx.TextCtrl(self.panel, style = wx.TE_MULTILINE|wx.TE_RICH, value = code)
  wx.StaticText(self.panel, label = 'C&lasses')
  self.classes = wx.TextCtrl(self.panel, value = ','.join(classes))
  wx.StaticText(self.panel, label = '&Title')
  self.title = wx.TextCtrl(self.panel, value = title or trigger)
  self.regexp = wx.CheckBox(self.panel, label = 'Trigger uses &regexp')
  self.regexp.SetValue(regexp)
  self.stop = wx.CheckBox(self.panel, label = '&Stop after execution')
  self.stop.SetValue(stop)
 
 def remove(self, event = None):
  self.removeFunc(self.oldTrigger)
  super(TriggerFrame, self).remove(event)
 
 def onOk(self, event):
  try:
   self.addFunc(self.trigger.GetValue(), self.code.GetValue(), classes = self.classes.GetValue().replce(', ', ',').split(',') if self.classes.GetValue() else [], regexp = self.regexp.GetValue(), simple = self.simple.GetValue(), stop = self.stop.GetValue(), title = self.title.GetValue() or self.trigger.GetValue())
   super(TriggerFrame, self).onOk()
  except Exception as e:
   wx.MessageBox(str(e), 'Error')
