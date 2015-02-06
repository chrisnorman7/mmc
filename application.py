import wx, os, multiprocessing
maxThreads = multiprocessing.cpu_count()
appMajorVersion = '1.1'
appMinorVersion = 'Beta'
appVersion = '%s%s' % (appMajorVersion, (' ' + appMinorVersion if appMinorVersion else ''))
appName = 'MMC'
appDescription = 'A MUD client written in pure Python. Features trigger, alias, hotkey, sound and support for assistive technologies.'
appVendorName = 'Software Metropolis'
appDevelopers = ['Chris Norman']
appInfo = wx.AboutDialogInfo()
appInfo.SetName(appName)
appInfo.SetDescription(appDescription)
appInfo.SetVersion(appVersion)
appInfo.SetDevelopers(appDevelopers)
appDirectory = os.getcwd()
app = wx.App(False)
app.SetAppDisplayName('%s (v %s)' % (appName, appVersion))
app.SetAppName(appName)
app.SetVendorName(appVendorName)
app.SetVendorDisplayName(appVendorName)
