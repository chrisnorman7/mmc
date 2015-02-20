import updatecheck, json, sys, application, wx
from webbrowser import open as wopen

class UpdateFrame(updatecheck.UpdateCheckFrame):
 def __init__(self):
  self.downloadUrl = ''
  return super(UpdateFrame, self).__init__(application.appName, application.appVersion, 'http://code-metropolis.com/mmc/version.json')
 
 def updateCheck(self):
  """MMC-specific update stuff."""
  try:
   j = json.loads(self.request.content)
   if application.appVersion != j['version']:
    self.updateButton.Enable()
    self.downloadUrl = j['download'].format(platform = sys.platform)
    self.Show(True)
    self.Raise()
    return 'Version %s-%s is available.' % (application.appName, j['version'])
   else:
    if self.Shown:
     wx.MessageBox('Version %s is the latest version of %s.' % (application.appVersion, application.appName), 'Your software is up to date.')
  except Exception as e:
   self.displayError(repr(e))
   self.Close(True)
 
 def onUpdate(self, event = None):
  wopen(self.downloadUrl)
  return self.Close(True)

